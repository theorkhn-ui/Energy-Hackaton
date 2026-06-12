"""LLM grid-operation agent: observes a stressed grid, acts via tools, narrates.

Usage:
  python src/agent.py --mock            # no API key needed: scripted policy through same plumbing
  ANTHROPIC_API_KEY=... python src/agent.py --case case30 --trip 9

Every run writes a narrated transcript to runs/ — raw material for the video.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from grid_tools import (load_grid, run_powerflow, get_grid_state, trip_line,
                        reconnect_line, redispatch_gen, shed_load)

MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")
MAX_STEPS = 15

SYSTEM = """You are a transmission grid operator agent. A contingency just occurred and \
lines are overloaded. Restore the grid to a safe state (all line loadings <= 100%).

Rules, in priority order:
1. Prefer generator redispatch (cheap, reversible).
2. Topology changes (reconnect available lines) where helpful.
3. Load shedding is a LAST RESORT — minimize MW shed.

Before every action, explain in 1-2 sentences WHY, citing the specific loadings you see. \
After the grid is safe, summarize what you did and the total load shed. Be concise."""

TOOL_SCHEMAS = [
    {"name": "get_grid_state", "description": "Observe overloaded lines, generator setpoints and limits, total load.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "run_powerflow", "description": "Re-run AC power flow; returns convergence, worst loading, overload count.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "redispatch_gen", "description": "Set generator active power in MW (clipped to limits).",
     "input_schema": {"type": "object", "properties": {"gen": {"type": "integer"}, "p_mw": {"type": "number"}},
                      "required": ["gen", "p_mw"]}},
    {"name": "reconnect_line", "description": "Switch a line back into service.",
     "input_schema": {"type": "object", "properties": {"line": {"type": "integer"}}, "required": ["line"]}},
    {"name": "trip_line", "description": "Switch a line out of service (topology action).",
     "input_schema": {"type": "object", "properties": {"line": {"type": "integer"}}, "required": ["line"]}},
    {"name": "shed_load", "description": "LAST RESORT: curtail load index by fraction (0-1).",
     "input_schema": {"type": "object", "properties": {"load": {"type": "integer"}, "fraction": {"type": "number"}},
                      "required": ["load", "fraction"]}},
]


def execute_tool(net, name: str, args: dict) -> dict:
    fns = {
        "get_grid_state": lambda: get_grid_state(net),
        "run_powerflow": lambda: run_powerflow(net),
        "redispatch_gen": lambda: redispatch_gen(net, args["gen"], args["p_mw"]),
        "reconnect_line": lambda: reconnect_line(net, args["line"]),
        "trip_line": lambda: trip_line(net, args["line"]),
        "shed_load": lambda: shed_load(net, args["load"], args["fraction"]),
    }
    return fns[name]()


def is_safe(net) -> bool:
    r = run_powerflow(net)
    return r["converged"] and r["n_overloaded_lines"] == 0


class Transcript:
    def __init__(self, tag: str):
        Path("runs").mkdir(exist_ok=True)
        self.path = Path("runs") / f"transcript_{tag}_{time.strftime('%Y%m%d_%H%M%S')}.md"
        self.lines = [f"# Agent run — {tag}\n"]

    def say(self, role: str, text: str):
        print(f"[{role}] {text}")
        self.lines.append(f"**{role}:** {text}\n")

    def save(self):
        self.path.write_text("\n".join(self.lines))
        print(f"\ntranscript -> {self.path}")


def setup_scenario(case: str, trip: int, stress: float):
    net = load_grid(case)
    net.load.p_mw *= stress
    run_powerflow(net)
    r = trip_line(net, trip)
    return net, r


def run_llm_agent(net, t: Transcript):
    import anthropic
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content":
                 f"Contingency occurred. Initial assessment: {json.dumps(run_powerflow(net))}. "
                 "Restore the grid to a safe state."}]
    for step in range(MAX_STEPS):
        resp = client.messages.create(model=MODEL, max_tokens=1500, system=SYSTEM,
                                      tools=TOOL_SCHEMAS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                t.say("agent", block.text.strip())
            elif block.type == "tool_use":
                result = execute_tool(net, block.name, dict(block.input))
                t.say("tool", f"{block.name}({json.dumps(dict(block.input))}) -> {json.dumps(result)}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "content": json.dumps(result)})
        if not tool_results:
            break
        messages.append({"role": "user", "content": tool_results})
        if is_safe(net):
            messages.append({"role": "user", "content":
                             [{"type": "text", "text": "Grid is safe. Give your final summary."}]})
            resp = client.messages.create(model=MODEL, max_tokens=800, system=SYSTEM, messages=messages)
            t.say("agent", resp.content[0].text.strip())
            break
    return is_safe(net)


def run_mock_agent(net, t: Transcript):
    """Scripted policy through the exact same executor — tests plumbing w/o API key."""
    t.say("agent", "(mock) Observing grid state.")
    state = execute_tool(net, "get_grid_state", {})
    t.say("tool", f"get_grid_state -> {json.dumps(state)[:300]}...")
    gens = state["generators"]
    if len(gens) >= 2:
        down = max(gens, key=lambda g: g["p_mw"])
        up = max(gens, key=lambda g: g["max_p_mw"] - g["p_mw"])
        r = execute_tool(net, "redispatch_gen", {"gen": down["gen"], "p_mw": down["p_mw"] - 15})
        t.say("tool", f"redispatch_gen(gen={down['gen']}, -15MW) -> {json.dumps(r)}")
        r = execute_tool(net, "redispatch_gen", {"gen": up["gen"], "p_mw": up["p_mw"] + 15})
        t.say("tool", f"redispatch_gen(gen={up['gen']}, +15MW) -> {json.dumps(r)}")
    r = execute_tool(net, "shed_load", {"load": 4, "fraction": 0.15})
    t.say("tool", f"shed_load(4, 0.15) -> {json.dumps(r)}")
    return is_safe(net)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="case30")
    ap.add_argument("--trip", type=int, default=9)
    ap.add_argument("--stress", type=float, default=1.3)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()

    net, after = setup_scenario(a.case, a.trip, a.stress)
    t = Transcript("mock" if a.mock else "llm")
    t.say("scenario", f"{a.case}, load x{a.stress}, line {a.trip} tripped -> {json.dumps(after)}")

    ok = run_mock_agent(net, t) if a.mock else run_llm_agent(net, t)
    t.say("result", f"{'SAFE' if ok else 'NOT SAFE'} | final: {json.dumps(run_powerflow(net))}")
    t.save()
