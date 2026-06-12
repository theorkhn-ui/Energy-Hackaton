"""Stale kWp register audit: estimate true kWp from observed output peaks.

For each inverter: estimated_kwp = p99.7 of P_AC at irradiation 950-1100 W/m2
(near-STC), compared to System_Overview kWp. Sustained ratio>1.1 inverters
should show estimated >> registered.

Run: PYTHONPATH=src/twin .venv/bin/python src/twin/kwp_audit.py
"""
from pathlib import Path

import pandas as pd

OUT = Path("runs/plant_a")


def main():
    import sys
    sys.path.insert(0, "src/twin")
    from run_plant_a import load, load_kwp

    pac, irrad, dv, evu = load()
    kwp, _ = load_kwp(list(pac.columns))

    near_stc = (irrad >= 950) & (irrad <= 1100)
    sub = pac[near_stc]
    est = sub.quantile(0.997)

    df = pd.DataFrame({
        "registered_kwp": kwp,
        "observed_peak_kw_atSTC": est.round(1),
    })
    # AC peak under near-STC irradiance ~ registered kWp x derate (~0.8-0.9 typical)
    df["peak_to_registered"] = (df.observed_peak_kw_atSTC / df.registered_kwp).round(2)
    plant_median = df.peak_to_registered.median()
    df["deviation_vs_plant"] = (df.peak_to_registered / plant_median).round(2)
    suspect = df[df.deviation_vs_plant > 1.15].sort_values("deviation_vs_plant", ascending=False)
    df.to_csv(OUT / "kwp_audit.csv")
    print(f"plant median peak/registered: {plant_median:.2f} "
          f"(normal AC/DC derate). n(near-STC samples)={int(near_stc.sum())}")
    print(f"\n== suspected stale kWp (deviation > 1.15x plant median) ==")
    print(suspect.to_string())
    if len(suspect):
        suggested = (suspect.observed_peak_kw_atSTC / plant_median).round(1)
        print("\nsuggested register values (kWp):")
        print(suggested.to_string())


if __name__ == "__main__":
    main()
