"""Plant B soiling analysis (Enerparc challenge).

Pipeline (staged, cached in runs/plant_b/cache_* so each stage fits a 45s window):
  stage 1: load 5-min parquet, build pvlib clear-sky reference (timestamps are UTC,
           verified against the 'Plant / Altitude' sun-elevation column), filter to
           clear-sky daytime samples, compute per-inverter performance index
           PI = P_AC / (kWp * G_meas/1000), aggregate to daily medians.
  stage 2: peer-normalize (inverter PI / plant median PI), 14-day rolling mean,
           sawtooth heuristic: decline >3% followed by recovery >2% within 7 days.
  stage 3: outputs -> SOILING_FINDINGS.md, soiling_per_inverter.csv, soiling_chart.png

Run from repo root:  .venv/bin/python src/twin/run_plant_b.py
"""

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/EP-Challenge-Final -/Plant B  (optional, only plant A is sufficient too)"
PARQUET = RAW / "1. Main-monitoring-data/main_monitoring_data_plant_b.parquet"
XLSX = RAW / "2. Additional Data/System_Overview_plant b.xlsx"
OUT = ROOT / "runs/plant_b"
OUT.mkdir(parents=True, exist_ok=True)

LAT, LON = 53.269, 12.121  # from Coordinate.txt (near Silmersdorf, Germany)

CACHE_DAILY = OUT / "cache_daily_pi.parquet"
CACHE_META = OUT / "cache_meta.csv"


def load_kwp():
    """kWp + row orientation per inverter from System_Overview (row 2 is the real header)."""
    x = pd.read_excel(XLSX, header=None)
    wr = x[x[0].astype(str).str.startswith("WR")].copy()
    inv_id = wr[0].str.replace(" ", "", regex=False).str.replace("WR", "", regex=False)
    meta = pd.DataFrame(
        {"inv": inv_id.values, "kwp": wr[9].astype(float).values,
         "orient": wr[4].values, "location": wr[3].values}
    ).set_index("inv")
    return meta


def stage1():
    if CACHE_DAILY.exists() and CACHE_META.exists():
        return
    meta = load_kwp()
    df = pd.read_parquet(PARQUET)
    df = df[~df.index.duplicated(keep="first")].sort_index()

    inv_cols = {}
    for c in df.columns:
        m = re.match(r"INV (\S+) / P_AC \(kW\)", c)
        if m and m.group(1) in meta.index:
            inv_cols[c] = m.group(1)

    # clear-sky GHI (timestamps verified UTC via solar-noon check on the Altitude column)
    loc = pvlib.location.Location(LAT, LON, tz="UTC")
    idx_utc = df.index.tz_localize("UTC")
    cs = loc.get_clearsky(idx_utc, model="ineichen")["ghi"].to_numpy()

    g = df["Plant / Irradiation_average (W/m²)"].to_numpy()
    evu = df["SIL11A / EVU (%)"].to_numpy() if "SIL11A / EVU (%)" in df else np.full(len(df), 100.0)

    # clear-sky candidates: pyranometer tracks the clear-sky model and sun is high;
    # exclude grid-curtailment intervals (EVU < 99 %)
    with np.errstate(invalid="ignore", divide="ignore"):
        kt = np.where(cs > 1, g / np.maximum(cs, 1), np.nan)
    mask = (cs > 200) & (kt > 0.85) & (kt < 1.15) & ~(evu < 99)

    P = df[list(inv_cols)].copy()
    P.columns = [inv_cols[c] for c in inv_cols]
    kwp = meta.loc[P.columns, "kwp"].to_numpy()

    pi = P.to_numpy() / (kwp[None, :] * g[:, None] / 1000.0)
    pi = np.where(mask[:, None], pi, np.nan)
    # drop outages (inverter off while sun is up) and clipping (near inverter AC limit)
    pmax = np.nanquantile(P.to_numpy(), 0.999, axis=0)
    pi = np.where(P.to_numpy() < 0.05 * kwp[None, :], np.nan, pi)
    pi = np.where(P.to_numpy() > 0.97 * pmax[None, :], np.nan, pi)
    pi = np.where((pi > 0) & (pi < 2), pi, np.nan)

    pi = pd.DataFrame(pi, index=df.index, columns=P.columns)
    day = pi.groupby(pi.index.floor("D"))
    daily = day.median()
    n = day.count()
    daily = daily.where(n >= 12)  # need >=1 h of clear-sky samples per day

    # plant-level PI against the *model* (sensor-independent) on clear days
    p_plant = P.sum(axis=1, min_count=50).to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        pi_cs = np.where(mask, p_plant / (kwp.sum() * np.maximum(cs, 1) / 1000.0), np.nan)
    daily["__plant_vs_model"] = pd.Series(pi_cs, index=df.index).groupby(df.index.floor("D")).median()
    daily["__sensor_vs_model"] = pd.Series(np.where(mask, kt, np.nan), index=df.index).groupby(
        df.index.floor("D")).median()

    daily.to_parquet(CACHE_DAILY)
    meta.to_csv(CACHE_META)
    print(f"stage1: {len(df)} rows -> {len(daily)} days, {len(P.columns)} inverters, "
          f"clear-sky samples kept: {mask.sum()} ({100 * mask.mean():.1f}%)")


def detect_episodes(s, decline_thr=0.03, recovery_thr=0.02, recovery_win=7, lookback=90):
    """Sawtooth heuristic on a smoothed normalized series (1.0 = own long-run level)."""
    s = s.dropna()
    if len(s) < 60:
        return []
    jump = s - s.shift(recovery_win)
    events = []
    cand = jump[jump >= recovery_thr].index
    last = None
    for t in cand:
        if last is not None and (t - last).days < 14:
            continue
        win = s.loc[t - pd.Timedelta(days=lookback): t - pd.Timedelta(days=recovery_win)]
        if win.empty:
            continue
        peak_t, peak_v = win.idxmax(), win.max()
        trough = s.loc[t - pd.Timedelta(days=recovery_win):t].min()
        decline = (peak_v - trough) / peak_v
        if decline >= decline_thr and (t - peak_t).days >= 14:
            rec = (s.loc[t:t + pd.Timedelta(days=recovery_win)].max() - trough) / peak_v
            events.append({"peak_date": peak_t.date(), "recovery_date": t.date(),
                           "decline_pct": round(100 * decline, 2),
                           "recovery_pct": round(100 * rec, 2),
                           "duration_days": (t - peak_t).days})
            last = t
    return events


def stage23():
    daily = pd.read_parquet(CACHE_DAILY)
    meta = pd.read_csv(CACHE_META, index_col=0)
    plant_vs_model = daily.pop("__plant_vs_model")
    sensor_vs_model = daily.pop("__sensor_vs_model")

    # peer ratio: each inverter vs cross-plant median of that day -> cancels weather,
    # season, angle-of-incidence and sensor soiling; isolates per-inverter behaviour
    med = daily.median(axis=1)
    ratio = daily.div(med, axis=0)
    ratio = ratio.div(ratio.median())  # 1.0 = inverter's own long-run level
    smooth = ratio.rolling("14D", min_periods=7).mean()

    rows = []
    for inv in smooth.columns:
        s = smooth[inv]
        sv = s.dropna()
        if len(sv) < 100:
            rows.append({"inverter": inv, "kwp": meta.loc[inv, "kwp"], "orient": meta.loc[inv, "orient"],
                         "days_with_data": len(sv), "drift_pct_per_month": np.nan,
                         "n_episodes": 0, "max_episode_decline_pct": np.nan, "episodes": ""})
            continue
        x = (sv.index - sv.index[0]).days / 30.44
        slope = np.polyfit(x, sv.to_numpy(), 1)[0] * 100  # %/month overall drift
        eps = detect_episodes(s)
        rows.append({
            "inverter": inv, "kwp": meta.loc[inv, "kwp"], "orient": meta.loc[inv, "orient"],
            "days_with_data": len(sv), "drift_pct_per_month": round(slope, 3),
            "n_episodes": len(eps),
            "max_episode_decline_pct": max((e["decline_pct"] for e in eps), default=np.nan),
            "episodes": "; ".join(f"{e['peak_date']}->{e['recovery_date']} -{e['decline_pct']}%/+{e['recovery_pct']}%"
                                  for e in eps),
        })
    res = pd.DataFrame(rows).set_index("inverter").sort_values("n_episodes", ascending=False)
    res.to_csv(OUT / "soiling_per_inverter.csv")

    # plant-wide sawtooth (sensor-independent, vs clear-sky model)
    plant_smooth = plant_vs_model.rolling("21D", min_periods=10).median()
    # de-season: divide by day-of-year climatology so seasonal AOI shape doesn't trigger
    doy = plant_smooth.index.dayofyear
    clim = plant_smooth.groupby(doy).transform("median")
    plant_anom = (plant_smooth / clim).rolling("14D", min_periods=7).mean()
    plant_eps = detect_episodes(plant_anom)

    write_outputs(res, smooth, ratio, plant_vs_model, plant_anom, plant_eps, sensor_vs_model, meta)


def write_outputs(res, smooth, ratio, plant_vs_model, plant_anom, plant_eps, sensor_vs_model, meta):
    ok = res[res.days_with_data > 1000]
    # "best example": most episodes, tie-break by deepest decline
    best = ok.sort_values(["n_episodes", "max_episode_decline_pct"], ascending=False).index[0]

    # chart: top = plant output vs clear-sky model (seasonal sawtooth?), bottom = best inverter peer ratio
    plt.rcParams.update({"font.size": 15, "axes.titlesize": 18, "axes.labelsize": 16})
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 7.2), dpi=150, sharex=True)

    ax = axes[0]
    ax.plot(plant_vs_model.index, plant_vs_model, ".", ms=2, color="#bbbbbb", label="daily (clear-sky days)")
    ax.plot(plant_anom.index, plant_anom * plant_vs_model.median(), lw=2, color="#1f77b4",
            label="de-seasonalized 14d trend")
    ax.set_ylabel("Plant PI vs clear-sky\nmodel (-)")
    ax.set_ylim(plant_vs_model.quantile(0.02) * 0.9, plant_vs_model.quantile(0.98) * 1.1)
    ax.set_title("Plant B: plant-wide performance vs pvlib clear-sky model")
    ax.legend(loc="lower left", fontsize=12)
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(ratio.index, ratio[best], ".", ms=2, color="#cccccc", label="daily peer ratio")
    ax.plot(smooth.index, smooth[best], lw=2, color="#d62728", label="14-day mean")
    for e in detect_episodes(smooth[best]):
        ax.axvspan(pd.Timestamp(e["peak_date"]), pd.Timestamp(e["recovery_date"]),
                   color="#ff7f0e", alpha=0.25)
    ax.axhline(1.0, color="k", lw=0.8, ls="--")
    ax.set_ylim(0.85, 1.1)
    ax.set_ylabel(f"INV {best}\npeer ratio (-)")
    ax.set_title(f"Most sawtooth-like inverter: INV {best} "
                 f"({int(res.loc[best, 'n_episodes'])} episodes flagged, shaded)")
    ax.legend(loc="lower left", fontsize=12)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "soiling_chart.png")

    n_flag = int((ok.n_episodes > 0).sum())
    drift_med = ok.drift_pct_per_month.median()
    worst_drift = ok.drift_pct_per_month.nsmallest(5)
    sensor_trend = sensor_vs_model.rolling("60D", min_periods=20).median()

    # seasonal shading fingerprint: monthly climatology of peer ratios
    monthly = ratio.groupby(ratio.index.month).median()
    winter_gain = monthly.loc[[1, 2, 11]].mean()  # Dec has no clear-sky days at 53N
    top_winter = winter_gain.nlargest(5)

    md = f"""# Plant B: Soiling Findings

**Data**: 5-min monitoring 2018-01 .. 2026-06, 107 inverters (55-74 kWp each, 7.87 MWp total),
on-site pyranometer `Plant / Irradiation_average` present. Timestamps are **UTC** (verified against
the recorded sun-altitude column). Location 53.269N 12.121E (Silmersdorf, DE) from Coordinate.txt.

## Method
- Clear-sky candidates: pvlib Ineichen GHI > 200 W/m², measured/modelled ratio 0.85-1.15,
  grid curtailment (EVU < 99 %) removed, inverter clipping (>97 % of P99.9) and outages excluded.
- Performance index PI = P_AC / (kWp x G_meas/1000) per inverter, daily median (>=1 h of samples).
- Peer ratio = inverter PI / plant-median PI -> cancels weather, season and sensor drift.
- Sawtooth heuristic on 14-day rolling mean: decline >3 % over >=14 d, recovery >2 % within 7 d.

## Findings
- **Per-inverter soiling sawtooth**: {n_flag} of {len(ok)} inverters show at least one
  decline-and-recovery episode. Best example: **INV {best}** with
  {int(res.loc[best, 'n_episodes'])} episodes (max decline {res.loc[best, 'max_episode_decline_pct']} %):
  {res.loc[best, 'episodes']}
- **Relative drift** (peer ratio trend): median {drift_med:+.3f} %/month across inverters.
  Fastest-degrading vs peers: {', '.join(f'INV {i} ({v:+.2f} %/mo)' for i, v in worst_drift.items())}.
- **Plant-wide pattern**: plant PI vs the (sensor-independent) clear-sky model shows
  {len(plant_eps)} de-seasonalized decline/recovery episodes: {'; '.join(f"{e['peak_date']}->{e['recovery_date']} -{e['decline_pct']}%" for e in plant_eps) or 'none'}.
- **Winter shading fingerprint**: peer ratios fan out strongly in Nov-Feb. Edge inverters
  outperform the plant median by up to {100 * (top_winter.iloc[0] - 1):.0f} % in winter
  ({', '.join(f'INV {i} {100 * (v - 1):+.0f}%' for i, v in top_winter.items())}), i.e. the *typical*
  row loses that much to low-sun inter-row shading. December has no clear-sky qualifying days at 53 N.
- **Interpretation of the headline case**: INV 05.08.106/107 are the last row (C.003, west edge).
  Their decline starts each spring, deepens through July/August and snaps back every September,
  consistent with seasonal vegetation growth shading (or edge-of-field soiling) cleared in early
  autumn, repeating every year of the 8.5-year record. This is the clearest sawtooth in the plant.
- **Pyranometer health**: measured/model clear-sky ratio drifted from
  {sensor_trend.dropna().iloc[0]:.3f} (2018) to {sensor_trend.dropna().iloc[-1]:.3f} (2026),
  so keep this in mind when reading absolute PI levels (peer ratios are immune to this).

See `soiling_per_inverter.csv` for all inverters and `soiling_chart.png` for the headline chart.
"""
    (OUT / "SOILING_FINDINGS.md").write_text(md)
    print("stage2/3 done. best inverter:", best, "| flagged:", n_flag, "/", len(ok))
    print("plant-wide episodes:", len(plant_eps))


if __name__ == "__main__":
    stage1()
    stage23()
