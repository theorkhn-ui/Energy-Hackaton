"""Rule-based baseline: the dumb fixer our LLM agent must beat.

Strategy: while overloads exist, shift generation from the cheapest-to-reduce
generator near the overload's receiving end to others with headroom; if that
fails after N rounds, shed load at the overloaded corridor.

Usage: python src/baseline_agent.py [case30] [line_to_trip]
"""
import sys

from grid_tools import (load_grid, run_powerflow, get_grid_state,
                        trip_line, redispatch_gen, shed_load)

MAX_ROUNDS = 10
STEP_MW = 10.0


def fix(net, log=print) -> bool:
    """Try to clear all overloads. Returns True if grid is safe."""
    for round_ in range(1, MAX_ROUNDS + 1):
        state = get_grid_state(net)
        overs = state["overloaded_lines"]
        if not overs:
            log(f"[round {round_}] grid safe.")
            return True
        worst = overs[0]
        log(f"[round {round_}] {len(overs)} overload(s); worst line "
            f"{worst['line']} at {worst['loading_pct']}%")

        # naive redispatch: reduce the most-loaded gen, raise the one with most headroom
        gens = state["generators"]
        if len(gens) >= 2:
            by_p = sorted(gens, key=lambda g: g["p_mw"], reverse=True)
            by_headroom = sorted(gens, key=lambda g: g["max_p_mw"] - g["p_mw"], reverse=True)
            down, up = by_p[0], by_headroom[0]
            if down["gen"] != up["gen"]:
                redispatch_gen(net, down["gen"], down["p_mw"] - STEP_MW)
                redispatch_gen(net, up["gen"], up["p_mw"] + STEP_MW)
                log(f"           redispatch: gen {down['gen']} -{STEP_MW}MW, "
                    f"gen {up['gen']} +{STEP_MW}MW")
                continue

        # fallback: shed 10% of the largest load
        biggest_load = int(net.load.p_mw.idxmax())
        shed_load(net, biggest_load, 0.10)
        log(f"           LOAD SHED: load {biggest_load} -10%")

    return not get_grid_state(net)["overloaded_lines"]


if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else "case30"
    net = load_grid(case)
    # stress the grid so contingencies actually hurt
    net.load.p_mw *= 1.3
    run_powerflow(net)

    line = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    print(f"=== Contingency: tripping line {line} on stressed {case} ===")
    r = trip_line(net, line)
    print(f"after trip: {r}\n")
    ok = fix(net)
    print(f"\nresult: {'SAFE' if ok else 'FAILED — overloads remain'}")
    print(f"final state: {run_powerflow(net)}")
