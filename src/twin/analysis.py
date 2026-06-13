"""Digital-twin analytics: expected power, underperformance, soiling drift.

Core idea (simple and explainable, judges can verify):
1. Performance index per inverter = P_AC / (kWp * irradiation/1000)  [~performance ratio]
2. Peer-normalize: inverter PI / plant median PI at each timestamp
   -> removes weather, curtailment, seasonal effects entirely.
3. Flags:
   - UNDERPERFORMER: sustained peer-relative deficit
   - SOILING: slow monotonic decline of the 7-day rolling peer ratio
   - OUTAGE/FAULT: P_AC ~ 0 while peers produce (and no curtailment active)
"""
from __future__ import annotations

import pandas as pd


def performance_index(pac: pd.DataFrame, irrad: pd.Series, kwp: pd.Series) -> pd.DataFrame:
    """PI[t, inv] = P_AC / (kWp * G/1000). NaN where irradiation is ~0."""
    g = irrad.where(irrad > 50)
    pi = pac.div(kwp, axis=1).div(g / 1000.0, axis=0)
    return pi.clip(upper=2.0)


def peer_ratio(pi: pd.DataFrame) -> pd.DataFrame:
    """Each inverter's PI relative to the plant median at the same timestamp."""
    med = pi.median(axis=1)
    return pi.div(med, axis=0)


def flag_underperformers(ratio: pd.DataFrame, threshold: float = 0.95,
                         min_days: int = 3) -> pd.DataFrame:
    """Inverters whose daily mean peer ratio stays below threshold for min_days."""
    daily = ratio.resample("D").mean()
    flags = []
    for inv in daily.columns:
        low = daily[inv] < threshold
        run = low.rolling(min_days).sum() >= min_days
        if run.any():
            flags.append({"inverter": inv,
                          "mean_ratio": round(float(daily[inv].mean()), 3),
                          "days_flagged": int(low.sum()),
                          "first_flag": str(run.idxmax().date())})
    return pd.DataFrame(flags).sort_values("mean_ratio") if flags else pd.DataFrame()


def soiling_signal(ratio: pd.DataFrame, window_days: int = 7,
                   drop_threshold: float = 0.03) -> pd.DataFrame:
    """Slow decline detection: rolling mean of daily peer ratio, total drift."""
    daily = ratio.resample("D").mean().rolling(window_days, min_periods=3).mean()
    out = []
    for inv in daily.columns:
        s = daily[inv].dropna()
        if len(s) < window_days:
            continue
        drift = float(s.iloc[-1] - s.iloc[0])
        if drift < -drop_threshold:
            out.append({"inverter": inv, "drift": round(drift, 3),
                        "start": round(float(s.iloc[0]), 3),
                        "end": round(float(s.iloc[-1]), 3)})
    return pd.DataFrame(out).sort_values("drift") if out else pd.DataFrame()


def flag_outages(pac: pd.DataFrame, irrad: pd.Series, curtail: pd.DataFrame,
                 min_irrad: float = 100.0) -> pd.DataFrame:
    """P~0 while sun is up, peers produce, and no curtailment active."""
    producing = irrad > min_irrad
    curtailed = (curtail < 99).any(axis=1) if len(curtail.columns) else pd.Series(False, index=pac.index)
    peers_on = pac.median(axis=1) > 0
    candidates = pac.eq(0) | pac.isna()
    mask = candidates[producing & peers_on & ~curtailed]
    events = []
    for inv in pac.columns:
        n = int(mask[inv].sum()) if inv in mask else 0
        if n > 0:
            hours = n * _step_hours(pac.index)
            events.append({"inverter": inv, "outage_steps": n,
                           "est_hours": round(hours, 1)})
    return (pd.DataFrame(events).sort_values("outage_steps", ascending=False)
            if events else pd.DataFrame())


def _step_hours(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 0.0
    return pd.Series(index).diff().median().total_seconds() / 3600.0
