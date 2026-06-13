"""Independent verification of three headline statistics for Plant A.

Recomputed from raw data only (this pass does not reuse the main analysis code).
Run from repo root: .venv/bin/python runs/plant_a/verify_clean.py [stage1|stage2]
stage1 builds daily/outage caches; stage2 (default if cache exists) prints verdicts.
"""
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW_CANDIDATES = [
    Path(os.environ["PLANT_A_BASE"]) if os.environ.get("PLANT_A_BASE") else None,
    Path("data/raw/EP-Challenge-Final -/Plant A (start here)"),
    Path("../Data/Plant A (start here)"),
]
RAW = next((p for p in RAW_CANDIDATES if p and p.exists()), RAW_CANDIDATES[1])
CACHE_DAILY = "runs/plant_a/verify_cache.parquet"          # daily energy + irr
CACHE_OUTAGE = "runs/plant_a/verify_cache_outage.parquet"  # 5-min outage flags, daily agg

SUN_MIN_KWH = 1.0      # daily plant irradiation energy (kWh/m2) for a "meaningful sun" day
TARIFF = 0.115         # EUR/kWh


def load_kwp():
    so = pd.read_excel(RAW / "2. Additional Data/System_Overview.xlsx", header=2)
    so = so[so["Description"].astype(str).str.strip().str.startswith("WR")]
    kwp = {}
    for _, r in so.iterrows():
        groups = re.findall(r"\d+", str(r["Description"]))
        if len(groups) < 3:
            continue
        # first three numeric groups identify the inverter; sub-entries (e.g. WR 01.01.004.02)
        # are extra module groups on the same inverter -> add their kWp
        iid = f"{int(groups[0]):02d}.{int(groups[1]):02d}.{int(groups[2]):03d}"
        kwp[iid] = kwp.get(iid, 0.0) + float(r["PDC (kWp)"])
    return pd.Series(kwp)


def stage1():
    df = pd.read_parquet(RAW / "1. Main-monitoring-data/main_monitoring_data.parquet")
    ts = pd.to_datetime(df.index, format="%Y.%m.%d %H:%M")
    inv_cols = [c for c in df.columns if c.startswith("INV") and "P_AC" in c]
    ids = [c.split(" / ")[0].replace("INV ", "") for c in inv_cols]
    p = df[inv_cols].astype("float64")
    p.columns = ids
    irr = df["Plant / Irradiation_average (W/m²)"].astype("float64")
    dv = df["DRD11A / DV (%)"].astype("float64")
    evu = df["DRD11A / EVU (%)"].astype("float64")
    day = pd.Series(ts.date, index=df.index).astype(str)

    # ---- daily cache: per-inverter kWh + plant irradiation kWh/m2 ----
    e_daily = (p * (5 / 60)).groupby(day.values).sum(min_count=1)
    e_daily["__irr_kwh"] = (irr.clip(lower=0) * (5 / 60) / 1000).groupby(day.values).sum(min_count=1)
    e_daily.index = pd.to_datetime(e_daily.index)
    e_daily.to_parquet(CACHE_DAILY)

    # ---- outage cache (claim 3): 5-min outage flags, aggregated per day per inverter ----
    curtailed = (dv < 99) | (evu < 99)
    plant_med = p.median(axis=1)
    base = (irr > 100) & (plant_med > 1) & (~curtailed)
    first_prod = {c: ts[(p[c] > 0).values].min() for c in p.columns}
    out = {}
    for c in p.columns:
        flag = base & p[c].notna() & (p[c] <= 0.01) & np.asarray(ts >= first_prod[c])
        out[c] = flag.groupby(day.values).sum()
    outage = pd.DataFrame(out)
    outage.index = pd.to_datetime(outage.index)
    outage.to_parquet(CACHE_OUTAGE)
    print("stage1 done:", e_daily.shape, outage.shape)


def build_peer(e, irr_kwh, kwp, sun_min, keep_zero_days):
    """Peer-normalized daily performance ratio.

    keep_zero_days=True counts a sunny day with zero recorded production as
    ratio 0 (a real bad day); False treats it as unobserved.
    """
    pi = e.div(kwp, axis=1).div(irr_kwh, axis=0)
    pi[irr_kwh < sun_min] = np.nan
    if not keep_zero_days:
        pi[e <= 0] = np.nan
    peer = pi.div(pi.median(axis=1), axis=0)
    peer[pi.notna().sum(axis=1) < 30] = np.nan
    return peer


def stage2():
    e = pd.read_parquet(CACHE_DAILY)
    irr_kwh = e.pop("__irr_kwh")
    kwp = load_kwp().reindex(e.columns)
    assert kwp.notna().all(), "kWp missing for some inverters"
    last_day = e.index.max()

    t = pd.read_excel(RAW / "2. Additional Data/Tickets.xlsx", sheet_name="2020-2026")
    t = t[t["component"].astype(str).str.startswith("INV")].copy()
    t["start"] = (pd.to_datetime(t["startdate"], utc=True, errors="coerce")
                  .dt.tz_convert("Europe/Berlin").dt.normalize().dt.tz_localize(None))
    t = t.dropna(subset=["start"])
    t["inv"] = t["component"].str.replace("INV ", "")

    # primary = lax filter (sun>=0.2 kWh/m2/day, zero-production days count as
    # ratio 0); alt = conservative (sun>=1.0, zero days unobserved)
    variants = {"primary(sun>=0.2,zeros=0)": (0.2, True),
                "alt(sun>=1.0,zeros=NaN)": (SUN_MIN_KWH, False)}
    for name, (sun, keep0) in variants.items():
        peer = build_peer(e, irr_kwh, kwp, sun, keep0)

        # ===== Claim 1: tickets preceded by a peer-ratio<0.8 day within 60d =====
        n_hit, leads = 0, []
        for _, r in t.iterrows():
            win = peer.loc[r["start"] - pd.Timedelta(days=60): r["start"], r["inv"]]
            bad = win[win < 0.8]
            if len(bad):
                n_hit += 1
                leads.append((r["start"] - bad.index.min()).days)
        print(f"[{name}] CLAIM1: {n_hit}/{len(t)} tickets with <0.8 day in prior 60d "
              f"(claimed 42/46); median lead to earliest bad day "
              f"{np.median(leads):.1f} d (claimed 51.5)")

        # ===== Claim 2: INV 01.03.018 chronic underperformance, last 365d =====
        inv2 = "01.03.018"
        yr = peer.loc[last_day - pd.Timedelta(days=364):, inv2].dropna()
        badmask = yr < 0.95
        e_yr = e.loc[yr.index, inv2]
        ratio_safe = yr[badmask].clip(lower=0.05)  # guard /0; no 0-days occur here
        lost_kwh = float((e_yr[badmask] / ratio_safe - e_yr[badmask]).sum())
        print(f"[{name}] CLAIM2: {inv2}: {int(badmask.sum())} of {len(yr)} observed days "
              f"<0.95 (claimed 272/317); lost {lost_kwh:.0f} kWh = "
              f"EUR {lost_kwh * TARIFF:.0f}/yr (claimed ~400)")

        # ===== Claim 3a: sections 01.08+01.09, 60d-mean peer ratio at end =====
        sec = [c for c in peer.columns if c.startswith(("01.08", "01.09"))]
        end60 = peer.loc[last_day - pd.Timedelta(days=59):, sec].mean()
        below = end60[end60 < 0.7]
        print(f"[{name}] CLAIM3a: {len(below)} inverters in 01.08+01.09 with 60d-mean "
              f"peer ratio <0.7 at end of data: "
              f"{', '.join(f'{k}={v:.2f}' for k, v in below.sort_values().items())} "
              f"(claimed: multiple)")

    # ===== Claim 3b: outage hours, filter-independent =====
    outage = pd.read_parquet(CACHE_OUTAGE)
    last365 = outage.loc[outage.index.max() - pd.Timedelta(days=364):]
    hrs = last365[["01.08.053", "01.08.057", "01.08.058"]].sum() * 5 / 60
    print("CLAIM3b: outage hours last 365d: " +
          ", ".join(f"{k}={v:.0f}h" for k, v in hrs.items()) +
          " (claimed ~740-840 each)")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "stage1" or not os.path.exists(CACHE_DAILY):
        stage1()
    if arg != "stage1":
        stage2()
