"""N-1 contingency screening: trip every line, see what breaks.

Output: ranked list of dangerous outages -> pick demo scenarios from here.
Usage: python src/n1_screening.py [case30|case39|case57|case118] [load_scale] [target_base_loading_pct]
"""
import sys

import pandapower as pp

from grid_tools import load_grid, LOADING_LIMIT


def screen(
    case: str = "case30",
    load_scale: float = 1.0,
    target_base_loading_pct: float | None = 80.0,
):
    net = load_grid(case, load_scale=load_scale,
                    target_base_loading_pct=target_base_loading_pct)
    base_max = net.res_line.loading_percent.max()
    print(f"Grid: {case} | {len(net.bus)} buses, {len(net.line)} lines | "
          f"load scale {load_scale:.2f} | base case max loading {base_max:.1f}%\n")

    results = []
    for line in net.line.index:
        if not net.line.at[line, "in_service"]:
            continue
        net.line.at[line, "in_service"] = False
        try:
            pp.runpp(net)
            over = net.res_line[net.res_line.loading_percent > LOADING_LIMIT]
            over = over[net.line.loc[over.index, "in_service"]]
            if len(over):
                results.append((line, len(over), float(over.loading_percent.max())))
        except pp.LoadflowNotConverged:
            results.append((line, -1, float("inf")))  # diverged = severe
        net.line.at[line, "in_service"] = True

    pp.runpp(net)
    results.sort(key=lambda r: (-r[1] if r[1] >= 0 else -999, -r[2]))
    if not results:
        print("Grid is fully N-1 secure at current loading. "
              "Scale loads up (net.load.p_mw *= 1.3) to create stress for the demo.")
    else:
        print(f"{'outage line':>12} | {'overloaded lines':>16} | {'worst loading %':>15}")
        print("-" * 50)
        for line, n_over, worst in results:
            tag = "DIVERGED" if n_over < 0 else f"{worst:.1f}"
            print(f"{line:>12} | {max(n_over, 0):>16} | {tag:>15}")
    return results


if __name__ == "__main__":
    screen(
        sys.argv[1] if len(sys.argv) > 1 else "case30",
        float(sys.argv[2]) if len(sys.argv) > 2 else 1.0,
        float(sys.argv[3]) if len(sys.argv) > 3 else 80.0,
    )
