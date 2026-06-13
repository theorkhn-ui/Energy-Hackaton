"""Validate the absolute-baseline twin and run the decisive uniform-loss proof.

Three things:
  1. Accuracy  - daily expected vs actual energy on healthy inverter-days.
  2. Reproduce - the twin independently re-finds the known faults.
  3. PROOF     - inject a synthetic uniform -10% on every inverter for the last
                 year. The relative peer metric (inverter / plant median) is
                 mathematically invariant and stays flat; the absolute twin
                 index drops ~10%. This is exactly the loss the peer-ratio
                 method cannot see, made visible.

Run from repo root:  python src/twin/twin_validate.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from twin_baseline import (  # noqa: E402  (local module, run from repo root)
    BASELINE_DAYS,
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
BLUE = "#1f6fb2"
LEMON = "#C8D400"
GRID = "#d9d9d4"


def healthy_controls(hi: pd.DataFrame, starts: pd.Series) -> list[str]:
    """Inverters that sit at ~1.0 across their whole post-baseline life."""
    out = []
    for inv in hi.columns:
        post = hi.loc[hi.index >= starts[inv] + pd.Timedelta(days=BASELINE_DAYS), inv]
        if len(post) > 200 and 0.95 <= post.median() <= 1.05 and post.std() < 0.12:
            out.append(inv)
    return out


def main() -> None:
    pac, g, t, curt = load_inputs_fast()
    starts = first_production(pac, g)
    gamma = fit_gamma(pac, g, t, curt, starts)
    cal = calibrate(pac, g, t, curt, starts, gamma)
    pexp = expected_power(g, t, cal["k"], gamma, pac.columns)

    num, den = daily_sums(pac, pexp, g, curt, starts)
    hi = num / den.where(den > 0)
    e_act = num * STEP_H   # daily actual kWh (strong-sun only)
    e_exp = den * STEP_H   # daily expected kWh

    # ------------------------------------------------------------------ #
    # 1. ACCURACY on healthy inverter-days (in baseline windows).
    # ------------------------------------------------------------------ #
    base_mask = pd.DataFrame(False, index=hi.index, columns=hi.columns)
    for inv in hi.columns:
        s = starts[inv]
        base_mask.loc[(hi.index >= s) & (hi.index < s + pd.Timedelta(days=BASELINE_DAYS)), inv] = True
    a = e_act.where(base_mask).to_numpy().ravel()
    e = e_exp.where(base_mask).to_numpy().ravel()
    ok = np.isfinite(a) & np.isfinite(e) & (e > 5)
    a, e = a[ok], e[ok]
    mape = float(np.mean(np.abs(a - e) / e) * 100)
    ss_res = float(np.sum((a - e) ** 2))
    ss_tot = float(np.sum((a - a.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    print(f"[accuracy] healthy daily-energy: MAPE={mape:.1f}%  R^2={r2:.3f}  (n={len(a):,} inverter-days)")

    # Out-of-sample healthy control: post-baseline days of stable inverters.
    ctrls = healthy_controls(hi, starts)
    cm = pd.DataFrame(False, index=hi.index, columns=hi.columns)
    for inv in ctrls:
        cm.loc[hi.index >= starts[inv] + pd.Timedelta(days=BASELINE_DAYS), inv] = True
    a2 = e_act.where(cm).to_numpy().ravel()
    e2 = e_exp.where(cm).to_numpy().ravel()
    ok2 = np.isfinite(a2) & np.isfinite(e2) & (e2 > 5)
    mape2 = float(np.mean(np.abs(a2[ok2] - e2[ok2]) / e2[ok2]) * 100)
    print(f"[accuracy] out-of-sample healthy control ({len(ctrls)} inverters): MAPE={mape2:.1f}%")

    # ------------------------------------------------------------------ #
    # 2. REPRODUCE known findings (last-365d median HI).
    # ------------------------------------------------------------------ #
    last365 = hi.loc[hi.index >= hi.index.max() - pd.Timedelta(days=365)]
    keys = {
        "01.08.053": "active collapse 08/09 (worst)",
        "01.08.058": "active collapse 08/09",
        "01.09.062": "active collapse 08/09",
        "01.08.057": "08/09 (recovered May 2026)",
        "01.03.018": "unreported fault, 0 tickets",
    }
    print("\n[reproduce] twin last-365d median HI vs known findings:")
    rep_rows = []
    for inv, note in keys.items():
        if inv in last365.columns:
            v = float(last365[inv].median())
            print(f"   {inv}  HI={v:.2f}   {note}")
            rep_rows.append(dict(inverter=inv, hi_last365=round(v, 3), note=note))
    pd.DataFrame(rep_rows).to_csv(OUT / "twin_reproduce.csv", index=False)

    # ------------------------------------------------------------------ #
    # 3. UNIFORM-LOSS PROOF.
    # ------------------------------------------------------------------ #
    LOSS = 0.10
    win_start = pac.index.max() - pd.Timedelta(days=365)
    pac_inj = pac.copy()
    inj_rows = pac_inj.index >= win_start
    pac_inj.loc[inj_rows] = pac_inj.loc[inj_rows] * (1.0 - LOSS)

    num_i, den_i = daily_sums(pac_inj, pexp, g, curt, starts)
    hi_i = num_i / den_i.where(den_i > 0)

    def peer(h: pd.DataFrame) -> pd.DataFrame:
        return h.div(h.median(axis=1), axis=0)

    days = hi.index >= win_start
    twin_before = float(hi.loc[days].stack().median())
    twin_after = float(hi_i.loc[days].stack().median())
    peer_before = float(peer(hi).loc[days].stack().median())
    peer_after = float(peer(hi_i).loc[days].stack().median())
    print("\n[PROOF] inject uniform -10% on ALL inverters, last 365 d:")
    print(f"   relative peer metric : {peer_before:.3f} -> {peer_after:.3f}  "
          f"(change {100*(peer_after/peer_before-1):+.1f}%)  <- BLIND")
    print(f"   absolute twin index  : {twin_before:.3f} -> {twin_after:.3f}  "
          f"(change {100*(twin_after/twin_before-1):+.1f}%)  <- DETECTED")
    pd.DataFrame([
        dict(metric="relative_peer", before=round(peer_before, 4), after=round(peer_after, 4)),
        dict(metric="absolute_twin", before=round(twin_before, 4), after=round(twin_after, 4)),
    ]).to_csv(OUT / "twin_uniform_loss.csv", index=False)

    # also: the real plant-wide gap the twin already sees (no injection).
    plant_gap = 1.0 - twin_before
    annual_exp_kwh = float(e_exp.loc[days].sum().sum())
    plant_gap_eur = plant_gap * annual_exp_kwh * TARIFF_EUR_PER_KWH
    print(f"\n[finding] real plant-wide gap vs commissioned baseline: "
          f"{100*plant_gap:.1f}%  (~EUR {plant_gap_eur:,.0f}/yr, "
          f"partly degradation/soiling, partly possible sensor drift - "
          f"invisible to peer-ratio).")

    make_charts(hi, starts, ctrls, peer_before, peer_after, twin_before, twin_after, LOSS)
    print(f"\nsaved validation outputs -> {OUT.resolve()}")


def make_charts(hi, starts, ctrls, peer_before, peer_after, twin_before, twin_after, loss):
    plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans",
                         "axes.edgecolor": INK, "axes.linewidth": 1.2})

    # --- PROOF chart: relative vs absolute under uniform loss ------------- #
    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=110)
    groups = ["Relative peer metric\n(inverter / plant median)", "Absolute twin index\n(vs own healthy baseline)"]
    before = [peer_before, twin_before]
    after = [peer_after, twin_after]
    deltas = ["unchanged - BLIND", f"-{int(loss*100)}% - DETECTED"]
    x = np.arange(2)
    w = 0.34
    ax.bar(x - w/2, before, w, label="Healthy plant", color=INK)
    ax.bar(x + w/2, after, w, label=f"After a uniform -{int(loss*100)}% on EVERY inverter",
           color=FAULT)
    for xi, (b, a) in enumerate(zip(before, after)):
        ax.text(xi - w/2, b + 0.012, f"{b:.2f}", ha="center", va="bottom", fontweight="bold")
        ax.text(xi + w/2, a + 0.012, f"{a:.2f}", ha="center", va="bottom", fontweight="bold", color=FAULT)
        # verdict, set high in the clear space above the bars
        ax.text(xi, 1.20, deltas[xi], ha="center", va="center", fontsize=14,
                fontweight="bold", color=(INK if xi == 0 else FAULT))
    ax.axhline(1.0, color=GRID, lw=1.5, zorder=0)
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=14)
    ax.set_ylim(0, 1.32); ax.set_ylabel("metric value (1.0 = healthy)")
    ax.set_title("A plant-wide loss is invisible to a relative metric — the absolute twin catches it",
                 fontweight="bold", fontsize=16, pad=30)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.11), ncol=2,
              fontsize=13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.subplots_adjust(bottom=0.12, top=0.85)
    fig.savefig(OUT / "twin_uniform_loss.png"); plt.close(fig)

    # --- Health timeline ------------------------------------------------- #
    fig, ax = plt.subplots(figsize=(13, 6.4), dpi=110)
    sm = hi.rolling(75, min_periods=20).median()
    ctrl = ctrls[0] if ctrls else hi.columns[0]
    ax.plot(sm.index, sm[ctrl], color=BLUE, lw=2.4, label=f"healthy control ({ctrl})")
    if "01.03.018" in sm:
        ax.plot(sm.index, sm["01.03.018"], color="#E58A00", lw=2.4, label="01.03.018 (unreported fault)")
    if "01.08.053" in sm:
        ax.plot(sm.index, sm["01.08.053"], color=FAULT, lw=2.6, label="01.08.053 (active collapse)")
    ax.plot(sm.index, sm.median(axis=1), color=INK, lw=2.0, ls="--", label="plant median")
    ax.axhline(1.0, color=GRID, lw=1.5, zorder=0)
    ax.set_ylim(0, 1.25); ax.set_ylabel("absolute health index (1.0 = commissioned baseline)")
    ax.set_title("Absolute twin health over time — anchored to each inverter's healthy youth",
                 fontweight="bold", fontsize=16)
    ax.legend(frameon=False, loc="lower left", ncol=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "twin_health_timeline.png"); plt.close(fig)
    print("[charts] twin_uniform_loss.png, twin_health_timeline.png")


if __name__ == "__main__":
    main()
