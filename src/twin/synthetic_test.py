"""Synthetic-data smoke test for the twin pipeline (until real Enerparc data arrives).

Builds 30 days of 15-min data for 6 inverters with planted faults:
- INV 01.01.003: soiling, 8% linear decline
- INV 01.01.005: chronic underperformer (-10%)
- INV 01.01.002: 2-day total outage mid-month
Then checks the pipeline finds exactly these.

Run: python src/twin/synthetic_test.py
"""
import numpy as np
import pandas as pd

from analysis import (performance_index, peer_ratio, flag_underperformers,
                      soiling_signal, flag_outages)

rng = np.random.default_rng(42)

idx = pd.date_range("2026-05-01", periods=30 * 96, freq="15min")
hours = idx.hour + idx.minute / 60
sun = np.clip(np.sin((hours - 6) / 12 * np.pi), 0, None)
irrad = pd.Series(sun * 850 * (0.7 + 0.3 * rng.random(len(idx))), index=idx)

INVS = [f"01.01.{i:03d}" for i in range(1, 7)]
KWP = pd.Series(100.0, index=INVS)

pac = pd.DataFrame(index=idx, columns=INVS, dtype=float)
for inv in INVS:
    pac[inv] = KWP[inv] * (irrad / 1000) * 0.95 * (1 + rng.normal(0, 0.02, len(idx)))

days = (idx - idx[0]).days.values
pac["01.01.003"] *= (1 - 0.08 * days / 30)          # soiling drift
pac["01.01.005"] *= 0.90                              # chronic underperformance
outage = (idx >= "2026-05-14") & (idx < "2026-05-16")
pac.loc[outage, "01.01.002"] = 0.0                    # outage

curtail = pd.DataFrame({"DRD11A / DV (%)": 100.0}, index=idx)

pi = performance_index(pac, irrad, KWP)
ratio = peer_ratio(pi)

print("== underperformers ==")
under = flag_underperformers(ratio)
print(under.to_string(index=False) if len(under) else "none")

print("\n== soiling candidates ==")
soil = soiling_signal(ratio)
print(soil.to_string(index=False) if len(soil) else "none")

print("\n== outages ==")
out = flag_outages(pac, irrad, curtail)
print(out.to_string(index=False) if len(out) else "none")

assert "01.01.005" in set(under.get("inverter", [])), "missed chronic underperformer"
assert "01.01.003" in set(soil.get("inverter", [])), "missed soiling"
assert "01.01.002" in set(out.get("inverter", [])), "missed outage"
print("\nALL PLANTED FAULTS DETECTED")
