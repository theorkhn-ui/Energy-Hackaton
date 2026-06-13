"""What-if simulator on the absolute twin: the 08/09 collapse, forward.

The twin gives an absolute expected-output model per inverter, so we can run
scenarios that pure analytics cannot:

  * Forward-project the active 01.08/01.09 collapse over the next 12 months and
    price the revenue at risk from the twin's own expected output.
  * Cost-of-delay curve: total loss as a function of when the crew is dispatched
    (repair date), so "fix it on your terms" gets a number.

Run from repo root:  python src/twin/twin_whatif.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from twin_baseline import (  # noqa: E402
    STEP_H,
    TARIFF_EUR_PER_KWH,
    calibrate,
    daily_sums,
    expected_power,
    first_production,
    fit_gamma,
    load_inputs_fast,
)

OUT = Path("runs/plant_a/twin")
INK = "#0A0A0A"
FAULT = "#E5484D"
LEMON = "#C8D400"
GRID = "#d9d9d4"

# An inverter is "currently degraded" in 08/09 if its recent absolute health is
# below baseline. Two tiers are reported: the run-rate bleeding NOW (only the
# currently-degraded units, conservative) and the SECTION CEILING (full annual
# revenue of all 08/09 capacity, the worst case if the collapse completes).
RECENT_DAYS = 120
COLLAPSE_HI = 0.90


def main() -> None:
    pac, g, t, curt = load_inputs_fast()
    starts = first_production(pac, g)
    gamma = fit_gamma(pac, g, t, curt, starts)
    cal = calibrate(pac, g, t, curt, starts, gamma)
    pexp = expected_power(g, t, cal["k"], gamma, pac.columns)
    num, den = daily_sums(pac, pexp, g, curt, starts)
    hi = num / den.where(den > 0)
    e_exp = den * STEP_H  # daily expected kWh (strong-sun)

    end = hi.index.max()
    recent = hi.loc[hi.index >= end - pd.Timedelta(days=RECENT_DAYS)]

    # Expected annual energy per inverter (last 365 d of expected output).
    # e_exp counts only strong-sun steps (where the linear model is valid), so
    # gross it up to full daylight by the irradiation ratio to get a true annual
    # figure (the linear model is not trustworthy below G_STRONG, but the energy
    # there is a small, irradiation-proportional tail).
    from twin_baseline import G_DAY_MIN, G_STRONG
    g365 = g.loc[g.index >= end - pd.Timedelta(days=365)]
    gross = float(g365[g365 > G_DAY_MIN].sum() / g365[g365 > G_STRONG].sum())
    yr = e_exp.loc[e_exp.index >= end - pd.Timedelta(days=365)]
    annual_exp_kwh = yr.sum() * gross
    print(f"[energy] strong-sun -> full-daylight gross-up factor: {gross:.3f}")

    # Identify the active-collapse cohort in sections 01.08 / 01.09.
    sec_mask = [c.startswith("01.08") or c.startswith("01.09") for c in hi.columns]
    sec = hi.columns[np.array(sec_mask)]
    cohort = []
    for inv in sec:
        h = recent[inv].median()
        if np.isfinite(h) and h < COLLAPSE_HI:
            cohort.append(inv)
    cohort = sorted(cohort)

    rows = []
    for inv in cohort:
        h = float(recent[inv].median())
        a_kwh = float(annual_exp_kwh.get(inv, np.nan))
        realized = a_kwh * (1 - h) * TARIFF_EUR_PER_KWH      # current run-rate loss
        at_risk = a_kwh * TARIFF_EUR_PER_KWH                 # if it goes fully to zero
        rows.append(dict(inverter=inv, recent_HI=round(h, 3),
                         annual_expected_kWh=round(a_kwh),
                         realized_loss_eur_yr=round(realized),
                         at_risk_eur_yr=round(at_risk)))
    coh = pd.DataFrame(rows).sort_values("at_risk_eur_yr", ascending=False)
    coh.to_csv(OUT / "twin_collapse_cohort.csv", index=False)

    realized_total = coh["realized_loss_eur_yr"].sum()
    # Section ceiling: full annual expected revenue of ALL 08/09 capacity, the
    # worst case if the whole section degrades to zero (the tail risk).
    section_ceiling = float(annual_exp_kwh.reindex(sec).sum()) * TARIFF_EUR_PER_KWH
    at_risk_total = section_ceiling
    print(f"[collapse] {len(coh)} of {len(sec)} 08/09 inverters currently "
          f"degraded (recent HI < {COLLAPSE_HI}):")
    print(coh.to_string(index=False))
    print(f"\n[collapse] TIER 1 - bleeding now (run-rate): ~EUR {realized_total:,.0f}/yr")
    print(f"[collapse] TIER 2 - section ceiling if 08/09 fully collapses: "
          f"~EUR {section_ceiling:,.0f}/yr ({len(sec)} inverters)")

    # ---- Cost-of-delay: integrate loss from today until repair date D ----- #
    # Assume each cohort inverter keeps losing at its current run-rate until the
    # crew arrives, then is restored to baseline. Loss(D) = run-rate * D.
    daily_runrate = realized_total / 365.0
    horizon = np.arange(0, 366, 7)
    loss_by_delay = daily_runrate * horizon
    pd.DataFrame({"repair_in_days": horizon,
                  "cumulative_loss_eur": np.round(loss_by_delay)}
                 ).to_csv(OUT / "twin_cost_of_delay.csv", index=False)

    make_chart(coh, horizon, loss_by_delay, realized_total, at_risk_total)
    print(f"\nsaved what-if outputs -> {OUT.resolve()}")


def make_chart(coh, horizon, loss_by_delay, realized_total, at_risk_total):
    plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans",
                         "axes.edgecolor": INK, "axes.linewidth": 1.2})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2), dpi=110,
                                   gridspec_kw={"width_ratios": [1.1, 1]})

    # Left: per-inverter at-risk revenue, recent HI annotated.
    c = coh.head(10).iloc[::-1]
    y = np.arange(len(c))
    ax1.barh(y, c["at_risk_eur_yr"], color=GRID, label="full revenue at risk")
    ax1.barh(y, c["realized_loss_eur_yr"], color=FAULT, label="losing now (run-rate)")
    ax1.set_yticks(y); ax1.set_yticklabels(c["inverter"])
    for yi, (_, r) in zip(y, c.iterrows()):
        ax1.text(r["at_risk_eur_yr"] + 30, yi, f"HI {r['recent_HI']:.2f}",
                 va="center", fontsize=12, color=INK)
    ax1.set_xlabel("EUR / year")
    ax1.set_title("Active 01.08 / 01.09 collapse: revenue at risk per inverter",
                  fontweight="bold", fontsize=15)
    ax1.legend(frameon=False, loc="lower right")
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)

    # Right: cost-of-delay curve.
    ax2.plot(horizon, loss_by_delay, color=FAULT, lw=3)
    ax2.fill_between(horizon, loss_by_delay, color=FAULT, alpha=0.10)
    for d in (30, 90, 180):
        val = realized_total / 365.0 * d
        ax2.plot([d], [val], "o", color=INK)
        ax2.annotate(f"{d} d: EUR {val:,.0f}", (d, val),
                     xytext=(d + 6, val), fontsize=12, va="center")
    ax2.set_xlabel("repair dispatched in N days")
    ax2.set_ylabel("cumulative lost revenue (EUR)")
    ax2.set_title("Cost of delay: the price of waiting",
                  fontweight="bold", fontsize=15)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)

    fig.suptitle(f"Twin what-if: ~EUR {realized_total:,.0f}/yr bleeding now, up to "
                 f"~EUR {at_risk_total:,.0f}/yr at risk if 08/09 fully collapses",
                 fontweight="bold", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "twin_whatif_collapse.png"); plt.close(fig)
    print("[chart] twin_whatif_collapse.png")


if __name__ == "__main__":
    main()
