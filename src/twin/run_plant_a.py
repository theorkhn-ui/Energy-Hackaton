"""Full Plant A analysis. Outputs findings to runs/plant_a/.

Run: .venv/bin/python src/twin/run_plant_a.py
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

BASE = Path("data/raw/EP-Challenge-Final -/Plant A (start here)")
PARQUET = BASE / "1. Main-monitoring-data/main_monitoring_data.parquet"
OUT = Path("runs/plant_a")
OUT.mkdir(parents=True, exist_ok=True)

STEP_H = 5 / 60  # 5-minute data


def load():
    schema = pq.ParquetFile(PARQUET).schema_arrow.names
    pac_cols = [c for c in schema if c.startswith("INV") and "P_AC" in c]
    extra = ["DRD11A / DV (%)", "DRD11A / EVU (%)",
             "Plant / Irradiation_average (W/m²)", "Plant / Altitude (°)"]
    extra = [c for c in extra if c in schema]
    tbl = pq.read_table(PARQUET, columns=pac_cols + extra + ["timestamp"])
    df = tbl.to_pandas()
    df.index = pd.to_datetime(df.index, format="%Y.%m.%d %H:%M")
    df = df.sort_index()
    df = df.astype("float32")
    pac = df[pac_cols].rename(columns={c: re.search(r"INV\s*([\d.]+)", c).group(1)
                                       for c in pac_cols})
    irrad = df["Plant / Irradiation_average (W/m²)"]
    dv = df.get("DRD11A / DV (%)")
    evu = df.get("DRD11A / EVU (%)")
    return pac, irrad, dv, evu


def load_kwp(pac_cols):
    so = pd.read_excel(BASE / "2. Additional Data/System_Overview.xlsx", header=2)
    so.columns = [str(c).strip() for c in so.columns]
    desc_col = next(c for c in so.columns if "ACC" in str(so[c].iloc[0:5].values) or True)
    # robust: find the column whose values contain 'WR '
    for c in so.columns:
        if so[c].astype(str).str.contains(r"WR \d").any():
            desc_col = c
            break
    kwp_col = next(c for c in so.columns if "PDC" in str(c))
    rows = so[so[desc_col].astype(str).str.match(r"WR [\d .]+$")]
    kwp = {}
    for _, r in rows.iterrows():
        inv_id = re.sub(r"[^\d.]", "", str(r[desc_col]).replace(" ", ""))
        inv_id = re.sub(r"\.+", ".", inv_id).strip(".")
        kwp[inv_id] = float(r[kwp_col])
    s = pd.Series(kwp)
    s = s[s.index.isin(pac_cols)]
    missing = [c for c in pac_cols if c not in s.index]
    return s, missing


def main():
    print("loading monitoring data...")
    pac, irrad, dv, evu = load()
    print(f"  {pac.shape[0]:,} rows x {pac.shape[1]} inverters, "
          f"{pac.index.min()} -> {pac.index.max()}")

    kwp, missing = load_kwp(list(pac.columns))
    # fallback: estimate kWp from observed p99.5 of P_AC
    for inv in missing:
        kwp[inv] = float(pac[inv].quantile(0.995))
    kwp = kwp.reindex(pac.columns)
    print(f"  kWp matched from System_Overview: {len(kwp) - len(missing)}, "
          f"estimated: {len(missing)}")

    if dv is not None:
        print("  DV value counts:", dv.value_counts().head(5).to_dict())
    if evu is not None:
        print("  EVU value counts:", evu.value_counts().head(5).to_dict())
    curtailed = pd.Series(False, index=pac.index)
    for sig in (dv, evu):
        if sig is not None:
            curtailed |= sig.fillna(100) < 99
    print(f"  curtailed steps: {int(curtailed.sum()):,} "
          f"({curtailed.mean()*100:.2f}% of all)")

    # ---------- daily energy & performance ----------
    day_e = pac.resample("D").sum() * STEP_H               # kWh per inverter/day
    day_g = (irrad.clip(lower=0).resample("D").sum() * STEP_H) / 1000.0  # kWh/m2
    pi = day_e.div(kwp, axis=1).div(day_g.where(day_g > 0.3), axis=0)  # daily PR
    ratio = pi.div(pi.median(axis=1), axis=0)              # peer-normalized
    ratio.to_csv(OUT / "daily_peer_ratio.csv")

    # ---------- chronic underperformers (last 365 d) ----------
    recent = ratio.loc[ratio.index.max() - pd.Timedelta(days=365):]
    stats = pd.DataFrame({
        "mean_ratio": recent.mean(),
        "days_below_95": (recent < 0.95).sum(),
        "days_observed": recent.notna().sum(),
    })
    under = stats[(stats.mean_ratio < 0.97) & (stats.days_below_95 > 30)]
    under = under.sort_values("mean_ratio")

    # ---------- revenue impact (last 365 d) ----------
    tar = pd.read_excel(BASE / "2. Additional Data/feed-in-tarrifs.xlsx", header=None)
    tar_inv = tar.iloc[1:, 0].astype(str).str.extract(r"INV\s*([\d.]+)")[0]
    mean_tariff = pd.Series(
        tar.iloc[1:, -100:].apply(pd.to_numeric, errors="coerce").mean(axis=1).values,
        index=tar_inv.values).dropna()  # ct/kWh, recent ~2 yrs
    e_recent = day_e.loc[recent.index]
    expected = e_recent.div(recent.clip(lower=0.2))
    lost_kwh = (expected - e_recent).clip(lower=0).sum()
    eur = (lost_kwh * mean_tariff.reindex(lost_kwh.index).fillna(mean_tariff.mean()) / 100)
    under["lost_kwh_365d"] = lost_kwh[under.index].round(0)
    under["lost_eur_365d"] = eur[under.index].round(0)
    under = under.sort_values("lost_eur_365d", ascending=False)
    under.to_csv(OUT / "underperformers.csv")
    print("\n== chronic underperformers (last 365d, ranked by € lost) ==")
    print(under.head(15).to_string())

    # ---------- outage detection (full granularity, curtailment-aware) ----------
    sun = irrad > 100
    peers_on = pac.median(axis=1) > 1.0
    candidate = pac.le(0.01) | pac.isna()
    valid = sun & peers_on & ~curtailed
    out_steps = candidate[valid].sum()
    outages = pd.DataFrame({
        "outage_hours_total": (out_steps * STEP_H).round(1),
        "pct_of_sun_hours": (out_steps / valid.sum() * 100).round(2),
    }).sort_values("outage_hours_total", ascending=False)
    outages.to_csv(OUT / "outage_hours.csv")
    print("\n== top outage inverters (daylight, non-curtailed, peers producing) ==")
    print(outages.head(10).to_string())

    # ---------- soiling-style drift (last 365 d) ----------
    roll = recent.rolling(21, min_periods=10).mean()
    drift = (roll.iloc[-1] - roll.iloc[:30].mean()).sort_values()
    drift.to_csv(OUT / "drift_365d.csv")
    print("\n== largest negative drift over last 365d (soiling candidates) ==")
    print(drift.head(10).round(3).to_string())

    # ---------- ticket cross-reference ----------
    tk = pd.ExcelFile(BASE / "2. Additional Data/Tickets.xlsx")
    tickets = pd.concat([tk.parse(s) for s in tk.sheet_names], ignore_index=True)
    tickets["startdate"] = pd.to_datetime(tickets["startdate"], errors="coerce", utc=True)
    print(f"\n== tickets: {len(tickets)} | components: "
          f"{tickets['component'].value_counts().head(6).to_dict()}")
    tickets.to_csv(OUT / "tickets_parsed.csv", index=False)

    # ---------- monthly heatmap ----------
    monthly = ratio.resample("ME").mean()
    fig, ax = plt.subplots(figsize=(16, 10))
    im = ax.imshow(monthly.T.values, aspect="auto", cmap="RdYlGn",
                   vmin=0.7, vmax=1.1, interpolation="nearest")
    ax.set_yticks(range(len(monthly.columns)), monthly.columns, fontsize=5)
    step = max(1, len(monthly) // 24)
    ax.set_xticks(range(0, len(monthly), step),
                  [d.strftime("%Y-%m") for d in monthly.index[::step]],
                  rotation=45, fontsize=7)
    ax.set_title("Peer-normalized performance ratio — inverter × month (green=good)")
    fig.colorbar(im, label="ratio vs plant median")
    fig.tight_layout()
    fig.savefig(OUT / "heatmap_monthly_ratio.png", dpi=130)
    print(f"\nsaved outputs -> {OUT}/")


if __name__ == "__main__":
    main()
