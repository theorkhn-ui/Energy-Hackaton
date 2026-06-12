"""Grid actions exposed as tools for the LLM agent.

Every function takes/returns plain Python types so it can be wrapped
directly as an LLM tool (JSON in, JSON out).
"""
from __future__ import annotations

import pandapower as pp
import pandapower.networks as pn

LOADING_LIMIT = 100.0  # % line loading considered an overload


def load_grid(
    case: str = "case30",
    load_scale: float = 1.0,
    target_base_loading_pct: float | None = None,
) -> pp.pandapowerNet:
    """Load an IEEE test grid and optionally make the base case demo-safe.

    Some pandapower benchmark grids are already overloaded under their built-in
    thermal limits. For a clean N-1 demo, normalize line ratings so the intact
    grid starts below the limit, then apply any requested load stress.
    """
    net = getattr(pn, case)()
    pp.runpp(net)
    if target_base_loading_pct is not None:
        base_max = float(net.res_line.loading_percent.max())
        if base_max > 0:
            net.line.max_i_ka *= base_max / target_base_loading_pct
            pp.runpp(net)
    if load_scale != 1.0:
        net.load.p_mw *= load_scale
        pp.runpp(net)
    return net


def run_powerflow(net) -> dict:
    """Run AC power flow. Returns convergence + worst line loading."""
    try:
        pp.runpp(net)
    except pp.LoadflowNotConverged:
        return {"converged": False}
    return {
        "converged": True,
        "max_line_loading_pct": round(float(net.res_line.loading_percent.max()), 1),
        "n_overloaded_lines": int((net.res_line.loading_percent > LOADING_LIMIT).sum()),
    }


def get_grid_state(net) -> dict:
    """Observation for the agent: overloaded lines, generator setpoints, headroom."""
    overloads = []
    for idx, row in net.res_line.iterrows():
        if row.loading_percent > LOADING_LIMIT and net.line.at[idx, "in_service"]:
            overloads.append({
                "line": int(idx),
                "from_bus": int(net.line.at[idx, "from_bus"]),
                "to_bus": int(net.line.at[idx, "to_bus"]),
                "loading_pct": round(float(row.loading_percent), 1),
            })
    gens = []
    for idx, row in net.gen.iterrows():
        gens.append({
            "gen": int(idx),
            "bus": int(row.bus),
            "p_mw": round(float(row.p_mw), 1),
            "max_p_mw": round(float(row.max_p_mw), 1),
            "min_p_mw": round(float(row.min_p_mw), 1),
        })
    return {"overloaded_lines": overloads, "generators": gens,
            "total_load_mw": round(float(net.load.p_mw.sum()), 1)}


def trip_line(net, line: int) -> dict:
    """Take a line out of service (the contingency, or an agent action)."""
    net.line.at[line, "in_service"] = False
    return run_powerflow(net)


def reconnect_line(net, line: int) -> dict:
    net.line.at[line, "in_service"] = True
    return run_powerflow(net)


def redispatch_gen(net, gen: int, p_mw: float) -> dict:
    """Set generator active power (clipped to its limits)."""
    lo, hi = float(net.gen.at[gen, "min_p_mw"]), float(net.gen.at[gen, "max_p_mw"])
    net.gen.at[gen, "p_mw"] = max(lo, min(hi, p_mw))
    return run_powerflow(net)


def shed_load(net, load: int, fraction: float) -> dict:
    """Curtail a load by `fraction` (0-1). Last resort — penalised in scoring."""
    net.load.at[load, "p_mw"] *= (1.0 - fraction)
    return run_powerflow(net)


# --- tool schema for the LLM agent (wire to your favourite SDK) -------------
TOOLS = [
    {"name": "run_powerflow", "description": "Re-run AC power flow and report worst loading."},
    {"name": "get_grid_state", "description": "List overloaded lines and generator setpoints/headroom."},
    {"name": "trip_line", "description": "Switch a line out of service.", "args": {"line": "int"}},
    {"name": "reconnect_line", "description": "Switch a line back into service.", "args": {"line": "int"}},
    {"name": "redispatch_gen", "description": "Set generator P (MW), clipped to limits.",
     "args": {"gen": "int", "p_mw": "float"}},
    {"name": "shed_load", "description": "LAST RESORT: curtail a load by fraction 0-1.",
     "args": {"load": "int", "fraction": "float"}},
]
