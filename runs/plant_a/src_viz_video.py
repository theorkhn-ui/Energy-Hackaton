#!/usr/bin/env python
"""Render three presentation PNGs (1920x1080 video frames) for Plant A findings.

Outputs into runs/plant_a/viz/:
  1. leadtime_chart.png   - flag lead time before each service ticket
  2. section_collapse.png - rolling peer ratio, sections 08+09 collapse
  3. money_chart.png      - annual cost of chronic underperformance
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
VIZ = HERE / "viz"
VIZ.mkdir(exist_ok=True)

FIGSIZE = (12.8, 7.2)
DPI = 150

# Okabe-Ito colorblind-safe palette
OI = {
    "orange": "#E69F00",
    "skyblue": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#000000",
}

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 14,
        "axes.titlesize": 21,
        "axes.titleweight": "bold",
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 13,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#444444",
        "font.family": "sans-serif",
    }
)


def category_group(cat: str) -> str:
    cat = str(cat)
    if cat in ("unbekannte Störung", "Fehlerursache konnte nicht ermittelt werden", "--"):
        return "Unknown cause"
    if cat in ("Kondensatoren defekt", "Platinen und mehr defekt", "Isolationswerte"):
        return "Component defect"
    if cat == "Strangausfall":
        return "String outage"
    return "Comm / init / LED fault"


GROUP_COLORS = {
    "Unknown cause": OI["skyblue"],
    "Component defect": OI["vermillion"],
    "String outage": OI["green"],
    "Comm / init / LED fault": OI["purple"],
}


# ---------------------------------------------------------------- chart 1
def chart_leadtimes():
    df = pd.read_csv(HERE / "ticket_leadtimes.csv")
    n_total = len(df)
    df = df.dropna(subset=["flag_lead_days"]).copy()
    n_flagged = len(df)
    df["group"] = df["category"].map(category_group)
    df = df.sort_values("flag_lead_days").reset_index(drop=True)
    median_lead = df["flag_lead_days"].median()

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    n = len(df)
    y = range(n)
    colors = df["group"].map(GROUP_COLORS)

    ax.hlines(y, 0, df["flag_lead_days"], color=colors, linewidth=2.0, alpha=0.85)
    ax.scatter(df["flag_lead_days"], list(y), s=60, c=colors, zorder=3,
               edgecolors="white", linewidths=0.8)

    # clean axis: no per-row tick labels
    ax.set_yticks([])
    ax.set_ylim(-1.5, n + 3.4)
    ax.set_xlim(-23, 70)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])

    # ticket-opened reference line; label above the lollipop field, line stops below it
    ax.vlines(0, -1.5, n + 0.7, color="#333333", linewidth=2)
    ax.text(0, n + 1.1, "ticket opened", ha="center", va="bottom",
            fontsize=14, fontweight="bold", color="#333333")

    # median line; label above the field too (no arrow -> nothing to cross);
    # line starts above the legend block in the lower-right corner
    ax.vlines(median_lead, 14, n + 0.7, color=OI["blue"], linewidth=1.6,
              linestyle="--", alpha=0.8)
    ax.text(median_lead, n + 1.1, f"median lead: {median_lead:.1f} days",
            ha="center", va="bottom", fontsize=14, fontweight="bold", color=OI["blue"])

    # inline labels for a handful of notable rows, placed in the empty left margin
    chosen = [0, n - 1]  # shortest and longest lead
    covered = {df.at[i, "group"] for i in chosen}
    for g in GROUP_COLORS:
        if g in covered:
            continue
        idxs = [i for i in range(n) if df.at[i, "group"] == g]
        if not idxs:
            continue
        mid = idxs[len(idxs) // 2]
        for cand in sorted(idxs, key=lambda i: abs(i - mid)):
            if all(abs(cand - k) >= 3 for k in chosen):
                chosen.append(cand)
                covered.add(g)
                break
    for i in sorted(chosen):
        r = df.loc[i]
        ax.text(-1.8, i, f"{r['inverter']}  ({r['ticket_date']})", ha="right",
                va="center", fontsize=12, fontweight="bold",
                color=GROUP_COLORS[r["group"]])

    ax.set_xlabel("days our flag fired before the ticket")
    ax.set_title(
        f"We saw it coming: flags fired before {n_flagged} of {n_total} service tickets",
        pad=18,
    )
    ax.text(1.0, 1.01, f"n = {n_flagged} tickets", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=13, color="#555555")

    present = [g for g in GROUP_COLORS if (df["group"] == g).any()]
    handles = [
        plt.Line2D([], [], color=GROUP_COLORS[g], marker="o", linestyle="-",
                   markersize=9, linewidth=2.5, label=g)
        for g in present
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=13,
              title="ticket category", title_fontsize=13)

    fig.tight_layout()
    fig.savefig(VIZ / "leadtime_chart.png", dpi=DPI)
    plt.close(fig)
    print("wrote leadtime_chart.png")


# ---------------------------------------------------------------- chart 2
COLLAPSE = ["01.08.057", "01.08.053", "01.08.058", "01.09.062", "01.09.065", "01.09.060"]
COLLAPSE_COLORS = [OI["vermillion"], OI["orange"], OI["purple"],
                   OI["blue"], OI["green"], OI["skyblue"]]


def chart_section_collapse():
    df = pd.read_csv(HERE / "daily_peer_ratio.csv", index_col=0, parse_dates=True)
    roll = df.rolling(30, min_periods=15).mean()
    roll = roll.loc["2024-06-01":]

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

    # background: all other inverters in light gray
    others = [c for c in roll.columns if c not in COLLAPSE]
    for c in others:
        ax.plot(roll.index, roll[c], color="#d9d9d9", linewidth=0.6, zorder=1)

    # shaded collapse region from Aug 2025
    shade_start = pd.Timestamp("2025-08-01")
    ax.axvspan(shade_start, roll.index[-1], color=OI["vermillion"], alpha=0.07, zorder=0)
    ax.text(shade_start + pd.Timedelta(days=8), 1.32, "collapse begins\nAug 2025",
            fontsize=14, fontweight="bold", color=OI["vermillion"], va="top")

    # the six collapse inverters with direct end-of-line labels
    label_slots = []
    for inv, color in zip(COLLAPSE, COLLAPSE_COLORS):
        s = roll[inv].dropna()
        ax.plot(s.index, s, color=color, linewidth=2.6, zorder=3)
        y_end = s.iloc[-1]
        # nudge labels apart vertically
        while any(abs(y_end - other) < 0.055 for other in label_slots):
            y_end -= 0.055
        label_slots.append(y_end)
        ax.text(s.index[-1] + pd.Timedelta(days=6), y_end, inv,
                color=color, fontsize=13, fontweight="bold", va="center")

    ax.axhline(1.0, color="#888888", linewidth=1, linestyle=":")
    ax.set_ylabel("performance vs plant median")
    ax.set_ylim(-0.05, 1.4)
    ax.set_xlim(roll.index[0], roll.index[-1] + pd.Timedelta(days=80))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.set_title("Section 08+09 failing since Aug 2025", pad=18)
    ax.text(0.0, 1.005, "30-day rolling mean of daily peer-normalized ratio  "
                        "(gray = all other inverters)",
            transform=ax.transAxes, fontsize=13, color="#555555", va="bottom")

    fig.tight_layout()
    fig.savefig(VIZ / "section_collapse.png", dpi=DPI)
    plt.close(fig)
    print("wrote section_collapse.png")


# ---------------------------------------------------------------- chart 3
def chart_money():
    u = pd.read_csv(HERE / "underperformers.csv", index_col=0)
    top = u.sort_values("lost_eur_365d", ascending=False).head(10)
    top = top.iloc[::-1]  # largest at top after barh

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

    highlight = "01.03.018"
    colors = [OI["vermillion"] if inv == highlight else OI["blue"] for inv in top.index]
    bars = ax.barh(top.index, top["lost_eur_365d"], color=colors, height=0.62)

    for inv, bar in zip(top.index, bars):
        v = bar.get_width()
        weight = "bold" if inv == highlight else "normal"
        color = OI["vermillion"] if inv == highlight else "#333333"
        suffix = "*" if inv == highlight else ""
        ax.text(v + 6, bar.get_y() + bar.get_height() / 2, f"€{v:,.0f}{suffix}",
                va="center", fontsize=15, fontweight=weight, color=color)

    xmax = top["lost_eur_365d"].max() * 1.18
    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.6, len(top) + 1.5)

    # annotation for the never-reported top loser: text fully above the bar field,
    # arrow drops onto the top bar from above (crosses no bars or labels)
    top_bar = bars[list(top.index).index(highlight)]
    bar_top = top_bar.get_y() + top_bar.get_height()
    ax.annotate(
        "never reported, found by our model",
        xy=(top_bar.get_width() * 0.80, bar_top + 0.06),
        xytext=(xmax * 0.99, len(top) + 0.65),
        ha="right", va="center",
        fontsize=16, fontweight="bold", color=OI["vermillion"],
        arrowprops=dict(arrowstyle="->", color=OI["vermillion"], lw=2,
                        connectionstyle="arc3,rad=-0.15"),
    )

    ax.set_xlabel("estimated lost revenue per year (EUR)")
    ax.set_title("What chronic underperformance costs per year", pad=18)
    ax.tick_params(axis="y", labelsize=15)

    fig.text(0.012, 0.012,
             "*conservative estimate; independent verification puts it at up to €523/yr",
             fontsize=12, color="#555555", style="italic")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(VIZ / "money_chart.png", dpi=DPI)
    plt.close(fig)
    print("wrote money_chart.png")


if __name__ == "__main__":
    chart_leadtimes()
    chart_section_collapse()
    chart_money()
    print("done")
