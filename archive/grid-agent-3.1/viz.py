"""Grid visualization for the demo video: loading-colored network plots.

Usage: python src/viz.py  -> renders before/after PNGs for the default scenario.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from grid_tools import load_grid, run_powerflow, trip_line


def _layout(net):
    g = nx.Graph()
    g.add_nodes_from(net.bus.index)
    for _, row in net.line.iterrows():
        g.add_edge(int(row.from_bus), int(row.to_bus))
    if hasattr(net, "trafo"):
        for _, row in net.trafo.iterrows():
            g.add_edge(int(row.hv_bus), int(row.lv_bus))
    return nx.kamada_kawai_layout(g), g


def plot_grid(net, path: str, title: str = ""):
    pos, g = _layout(net)
    fig, ax = plt.subplots(figsize=(10, 8))

    for idx, row in net.line.iterrows():
        u, v = int(row.from_bus), int(row.to_bus)
        if not row.in_service:
            ax.plot(*zip(pos[u], pos[v]), color="#999", ls=":", lw=1.5, zorder=1)
            continue
        load = float(net.res_line.at[idx, "loading_percent"])
        color = "#d62728" if load > 100 else "#ff7f0e" if load > 80 else "#2ca02c"
        ax.plot(*zip(pos[u], pos[v]), color=color, lw=1.5 + load / 40, zorder=2)
        if load > 80:
            mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
            ax.annotate(f"{load:.0f}%", (mx, my), fontsize=8, color=color,
                        fontweight="bold", ha="center",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=0.5))

    gen_buses = set(net.gen.bus.astype(int)) | set(net.ext_grid.bus.astype(int))
    for b in net.bus.index:
        is_gen = int(b) in gen_buses
        ax.scatter(*pos[b], s=140 if is_gen else 60,
                   c="#1f77b4" if is_gen else "#444",
                   marker="s" if is_gen else "o", zorder=3)
        ax.annotate(str(b), pos[b], fontsize=7, color="white",
                    ha="center", va="center", zorder=4)

    handles = [plt.Line2D([], [], color=c, lw=2, label=l) for c, l in
               [("#2ca02c", "< 80%"), ("#ff7f0e", "80-100%"), ("#d62728", "OVERLOAD"),
                ("#999", "out of service")]]
    ax.legend(handles=handles, loc="lower left", fontsize=8)
    ax.set_title(title, fontsize=13)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"saved {path}")


if __name__ == "__main__":
    net = load_grid("case30")
    net.load.p_mw *= 1.3
    run_powerflow(net)
    plot_grid(net, "runs/grid_base.png", "Stressed grid — before contingency")
    trip_line(net, 9)
    plot_grid(net, "runs/grid_contingency.png", "Line 9 tripped — overloads appear")
