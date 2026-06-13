"""Absolute-baseline digital twin for Plant A.

Closes the documented limitation of the peer-ratio method: a loss that hits
every inverter equally is invisible to a relative (cross-sectional) metric.
Here each inverter is modelled against ITS OWN healthy history from physical
drivers (irradiance + module temperature), giving an ABSOLUTE health index.

Model, per inverter i (kWp-free, so it is robust to the stale-kWp register):

    P_exp[i,t] = k_i * G_t * (1 + gamma * (T_mod_t - 25))

  - G_t   = plane irradiance (W/m^2)
  - T_mod = module temperature (deg C); 25 C is the reference
  - gamma = module power temperature coefficient, fit globally on healthy data
  - k_i   = inverter's temperature-corrected healthy response (kW per W/m^2),
            calibrated on its first ~365 production days (its healthy youth)

  Daily health index:
    HI[i,d] = sum_t P_actual / sum_t P_exp   over daylight, non-curtailed steps

HI ~ 1.0 means "behaving like its healthy self"; below 1.0 is absolute loss,
detectable even when every inverter loses output together.

Run from repo root:  python src/twin/twin_baseline.py
Outputs:             runs/plant_a/twin/
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("runs/plant_a/twin")
CACHE = OUT / "twin_input_cache.parquet"
TARIFF_EUR_PER_KWH = 0.115  # representative Plant A feed-in tariff (11.5 ct/kWh)
STEP_H = 5 / 60

# Fit / aggregation thresholds. The SAME irradiance window is used to calibrate
# k_i and to aggregate the daily health index, so the linear P = k*G model is
# only ever evaluated in the strong-sun regime where it is physically valid
# (below ~250 W/m^2 inverter efficiency rolls off and the linear model would
# overstate expected output, biasing the index down).
G_STRONG = 300.0       # W/m^2: strong-sun regime for both fit and aggregation
G_DAY_MIN = 50.0       # W/m^2: a "daylight" step (used only for commissioning)
BASELINE_DAYS = 365    # healthy-youth window length per inverter
MIN_DAY_STEPS = 6      # require >=30min of strong sun for a valid HI day
GAMMA_DEFAULT = -0.0040  # fallback c-Si power tempco if the fit is unstable


def resolve_data_base() -> Path:
    env = os.environ.get("PLANT_A_BASE")
    cands = [Path(env)] if env else []
    root = Path.cwd()
    cands += [
        root.parent / "Data/Plant A (start here)",
        root / "Data/Plant A (start here)",
        root / "data/raw/EP-Challenge-Final -/Plant A (start here)",
    ]
    for b in cands:
        if (b / "1. Main-monitoring-data/main_monitoring_data.parquet").exists():
            return b
    raise FileNotFoundError("Plant A parquet not found. Set PLANT_A_BASE.")


def _match(cols, *needles):
    for c in cols:
        cl = str(c)
        if all(n.lower() in cl.lower() for n in needles):
            return c
    return None


def load_inputs_fast() -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    if CACHE.exists():
        df = pd.read_parquet(CACHE)
        pac = df[[c for c in df.columns if not c.startswith("_")]]
        return pac, df["_G"], df["_T"], df["_CURT"].astype(bool)

    import pyarrow.parquet as pqmod

    base = resolve_data_base()
    pqpath = base / "1. Main-monitoring-data/main_monitoring_data.parquet"
    all_cols = [f.name for f in pqmod.read_schema(pqpath)]

    ts_col = _match(all_cols, "timestamp") or "timestamp"
    pac_cols = [c for c in all_cols if c.startswith("INV ") and "P_AC" in c]
    g_col = _match(all_cols, "Irradiation")
    t_col = _match(all_cols, "Temperature", "Module")
    dv_col = _match(all_cols, "DV (%)")
    evu_col = _match(all_cols, "EVU (%)")

    data_cols = pac_cols + [c for c in (g_col, t_col, dv_col, evu_col) if c]
    use = ([ts_col] if ts_col in all_cols else []) + data_cols
    print(f"loading parquet: {len(pac_cols)} inverters + G/T/DV/EVU ...")
    raw = pd.read_parquet(pqpath, columns=use)

    # timestamp may come back as a column or as the restored index.
    if ts_col in raw.columns:
        raw = raw.set_index(pd.to_datetime(raw.pop(ts_col), errors="coerce"))
    else:
        raw.index = pd.to_datetime(raw.index, errors="coerce")
    raw = raw[~raw.index.isna()].sort_index()
    print(f"  index dtype={raw.index.dtype}, span {raw.index.min()} -> {raw.index.max()}")

    pac = raw[pac_cols].astype("float32")
    pac.columns = [c.split(" / ")[0].replace("INV ", "").strip() for c in pac_cols]
    g = raw[g_col].astype("float32")
    t = raw[t_col].astype("float32")
    dv = raw[dv_col].astype("float32") if dv_col else pd.Series(100.0, index=raw.index)
    evu = raw[evu_col].astype("float32") if evu_col else pd.Series(100.0, index=raw.index)
    curt = (dv.fillna(100) < 99.0) | (evu.fillna(100) < 99.0)

    OUT.mkdir(parents=True, exist_ok=True)
    cache = pac.copy()
    cache["_G"] = g
    cache["_T"] = t
    cache["_CURT"] = curt
    cache.to_parquet(CACHE)
    print(f"  cached -> {CACHE}")
    return pac, g, t, curt.astype(bool)


def first_production(pac: pd.DataFrame, g: pd.Series) -> pd.Series:
    """First timestamp each inverter clearly produces in daylight."""
    sun = g > 100
    out = {}
    for inv in pac.columns:
        producing = sun & (pac[inv] > 0.5)
        idx = producing[producing].index
        out[inv] = idx.min() if len(idx) else pac.index.max()
    return pd.Series(out)


def fit_gamma(pac, g, t, curt, starts) -> float:
    """Global module power temperature coefficient from healthy-youth data.

    Pool y = P / (k0_i * G) against x = (T - 25) at strong irradiance over each
    inverter's first BASELINE_DAYS; slope is gamma. Falls back to literature if
    the fit is degenerate.
    """
    xs, ys = [], []
    Tarr = t.to_numpy()
    Garr = g.to_numpy()
    for inv in pac.columns:
        s = starts[inv]
        win = (pac.index >= s) & (pac.index < s + pd.Timedelta(days=BASELINE_DAYS))
        p = pac[inv].to_numpy()
        ok = win & (Garr > G_STRONG) & (~curt.to_numpy()) & (p > 0) & np.isfinite(Tarr)
        if ok.sum() < 500:
            continue
        r = p[ok] / Garr[ok]
        k0 = np.median(r)
        if not np.isfinite(k0) or k0 <= 0:
            continue
        xs.append(Tarr[ok] - 25.0)
        ys.append(r / k0)
    if not xs:
        return GAMMA_DEFAULT
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    # robust-ish: clip absurd ratios, least squares slope through the cloud
    keep = (y > 0.3) & (y < 1.7)
    x, y = x[keep], y[keep]
    gamma = float(np.polyfit(x, y, 1)[0])
    if not np.isfinite(gamma) or gamma > 0 or gamma < -0.01:
        return GAMMA_DEFAULT
    return gamma


def calibrate(pac, g, t, curt, starts, gamma) -> pd.DataFrame:
    """Per-inverter k_i (temp-corrected healthy response) + fit quality."""
    Garr = g.to_numpy()
    Tarr = t.to_numpy()
    tempfac = 1.0 + gamma * (Tarr - 25.0)
    rows = {}
    for inv in pac.columns:
        s = starts[inv]
        win = (pac.index >= s) & (pac.index < s + pd.Timedelta(days=BASELINE_DAYS))
        p = pac[inv].to_numpy()
        ok = win & (Garr > G_STRONG) & (~curt.to_numpy()) & (p > 0) & np.isfinite(Tarr)
        n = int(ok.sum())
        if n < 200:
            rows[inv] = dict(k=np.nan, n_fit=n, baseline_start=s, fit_r2=np.nan)
            continue
        # Energy-weighted calibration: k_i = sum(P) / sum(G_eff) over the
        # baseline window. This is the SAME statistic as the health index
        # (an energy ratio), so an inverter reads HI = 1.0 on its own baseline
        # by construction; a median-of-ratios fit leaves a ~4% offset.
        geff = Garr[ok] * tempfac[ok]
        k = float(np.sum(p[ok]) / np.sum(geff))
        # baseline fit quality: expected vs actual on the same window
        pexp = k * Garr[ok] * tempfac[ok]
        ss_res = float(np.sum((p[ok] - pexp) ** 2))
        ss_tot = float(np.sum((p[ok] - np.mean(p[ok])) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
        rows[inv] = dict(k=k, n_fit=n, baseline_start=s, fit_r2=r2)
    return pd.DataFrame(rows).T


def expected_power(g, t, k: pd.Series, gamma: float, columns) -> pd.DataFrame:
    """P_exp[t,i] = k_i * G_t * (1 + gamma (T-25))."""
    geff = (g.to_numpy() * (1.0 + gamma * (t.to_numpy() - 25.0))).astype("float32")
    kvals = k.reindex(columns).to_numpy(dtype="float32")
    pexp = np.outer(geff, kvals).astype("float32")
    return pd.DataFrame(pexp, index=g.index, columns=list(columns))


def daily_sums(pac, pexp, g, curt, starts) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily summed actual and expected power over strong-sun, valid steps.

    Returns (num, den) where HI = num/den and daily energy = sum * STEP_H.
    Strong-sun (G > G_STRONG) matches the calibration regime so the linear
    model is only evaluated where it is valid.
    """
    base_valid = (g > G_STRONG) & (~curt)
    num_parts, den_parts = {}, {}
    for inv in pac.columns:
        p = pac[inv]
        valid = base_valid & p.notna() & (pac.index >= starts[inv])
        num_parts[inv] = p.where(valid)
        den_parts[inv] = pexp[inv].where(valid)
    num = pd.DataFrame(num_parts).resample("D").sum(min_count=MIN_DAY_STEPS)
    den = pd.DataFrame(den_parts).resample("D").sum(min_count=MIN_DAY_STEPS)
    return num, den


def daily_health(pac, pexp, g, curt, starts) -> pd.DataFrame:
    """Daily absolute health index per inverter: sum(actual)/sum(expected)."""
    num, den = daily_sums(pac, pexp, g, curt, starts)
    return num / den.where(den > 0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pac, g, t, curt = load_inputs_fast()
    print(f"  {len(pac):,} steps x {pac.shape[1]} inverters, "
          f"{pac.index.min()} -> {pac.index.max()}")

    starts = first_production(pac, g)
    gamma = fit_gamma(pac, g, t, curt, starts)
    print(f"  global gamma (module power tempco): {gamma:.5f} /degC")

    cal = calibrate(pac, g, t, curt, starts, gamma)
    cal.to_csv(OUT / "twin_calibration.csv")
    good = cal["k"].notna().sum()
    print(f"  calibrated k_i for {good}/{len(cal)} inverters; "
          f"median baseline fit R2 = {cal['fit_r2'].median():.3f}")

    pexp = expected_power(g, t, cal["k"], gamma, pac.columns)
    hi = daily_health(pac, pexp, g, curt, starts)
    hi.to_csv(OUT / "twin_health_index.csv")
    print(f"  daily health index: {hi.shape[0]} days x {hi.shape[1]} inverters")

    # Self-check: by construction each inverter must read ~1.0 on its own
    # baseline window. If it does, the absolute scale is trustworthy and any
    # later departure is a real signal (not a calibration artefact).
    base_med = {}
    for inv in pac.columns:
        s = starts[inv]
        win = hi.index[(hi.index >= s) & (hi.index < s + pd.Timedelta(days=BASELINE_DAYS))]
        base_med[inv] = hi.loc[win, inv].median()
    base_med = pd.Series(base_med)
    print(f"  baseline self-check: median HI on baseline windows = "
          f"{base_med.median():.3f} (target 1.00), "
          f"IQR [{base_med.quantile(.25):.3f}, {base_med.quantile(.75):.3f}]")

    last90 = hi.loc[hi.index >= hi.index.max() - pd.Timedelta(days=90)].median()
    last90 = last90.sort_values()
    print("\n  lowest current absolute health (last 90d median HI):")
    print(last90.head(8).round(3).to_string())
    print("\n  healthiest (last 90d median HI):")
    print(last90.tail(5).round(3).to_string())
    print(f"\n  plant-wide last-90d median HI across inverters: {last90.median():.3f}")

    print(f"\nsaved -> {OUT.resolve()}")


if __name__ == "__main__":
    main()

