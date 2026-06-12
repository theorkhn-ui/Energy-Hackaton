"""Quantify suspected stale kWp entries in Plant A's asset register.

Run after `run_plant_a.py` has refreshed `runs/plant_a/daily_peer_ratio.csv`.
The correction estimate is intentionally simple and auditable:

    implied_kWp = registered_kWp * median_peer_ratio

If an inverter is persistently above the peer median, the registered capacity is
likely too low. Sections 01.08/01.09 are reported separately because the active
collapse can distort their ratios.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_plant_a import load, load_kwp

OUT = Path("runs/plant_a")


def main() -> None:
    pac, _irrad, _dv, _evu = load()
    kwp, missing = load_kwp(list(pac.columns))
    if missing:
        raise RuntimeError(f"missing kWp values: {missing}")

    ratio = (
        pd.read_csv(OUT / "daily_peer_ratio.csv", index_col=0, parse_dates=True)
        .replace([np.inf, -np.inf], np.nan)
    )

    stats = pd.DataFrame({
        "inverter": ratio.columns,
        "registered_kwp": kwp.reindex(ratio.columns).values,
        "mean_ratio": ratio.mean().values,
        "median_ratio": ratio.median().values,
        "days_observed": ratio.notna().sum().values,
        "pct_days_above_1_1": ((ratio > 1.1).sum() / ratio.notna().sum()).values,
        "last365_mean_ratio": ratio.loc[ratio.index.max() - pd.Timedelta(days=365):].mean().values,
    })
    stats["implied_kwp_from_median"] = stats["registered_kwp"] * stats["median_ratio"]
    stats["kwp_gap"] = stats["implied_kwp_from_median"] - stats["registered_kwp"]
    stats["registered_understated_pct"] = stats["kwp_gap"] / stats["implied_kwp_from_median"] * 100

    stats["section"] = stats["inverter"].str.slice(0, 5)
    stats["classification"] = "not_flagged"
    sustained = (
        (stats["median_ratio"] >= 1.20)
        & (stats["pct_days_above_1_1"] >= 0.75)
        & (stats["days_observed"] >= 365)
    )
    confounded = stats["inverter"].str.startswith(("01.08", "01.09"))
    stats.loc[sustained & ~confounded, "classification"] = "clean_register_candidate"
    stats.loc[sustained & confounded, "classification"] = "operationally_confounded"
    watch = (
        (stats["classification"] == "not_flagged")
        & (stats["median_ratio"] >= 1.10)
        & (stats["pct_days_above_1_1"] >= 0.50)
    )
    stats.loc[watch, "classification"] = "watch"

    flagged = (
        stats[stats["classification"] != "not_flagged"]
        .sort_values(["classification", "median_ratio"], ascending=[True, False])
        .copy()
    )
    numeric = [
        "registered_kwp",
        "mean_ratio",
        "median_ratio",
        "pct_days_above_1_1",
        "last365_mean_ratio",
        "implied_kwp_from_median",
        "kwp_gap",
        "registered_understated_pct",
    ]
    flagged[numeric] = flagged[numeric].round(3)
    flagged.to_csv(OUT / "stale_kwp_audit.csv", index=False)
    write_markdown(flagged)

    clean = flagged[flagged["classification"] == "clean_register_candidate"]
    print(clean[["inverter", "registered_kwp", "median_ratio", "implied_kwp_from_median", "kwp_gap"]].to_string(index=False))
    print(f"\nclean register candidates: {len(clean)} -> {OUT / 'STALE_KWP_AUDIT.md'}")


def write_markdown(flagged: pd.DataFrame) -> None:
    clean = flagged[flagged["classification"] == "clean_register_candidate"]
    confounded = flagged[flagged["classification"] == "operationally_confounded"]
    watch = flagged[flagged["classification"] == "watch"]

    lines = [
        "# Stale kWp Register Audit",
        "",
        "Method: if an inverter is persistently above peer ratio 1.1, estimate the corrected asset-register capacity as `registered_kWp * median_peer_ratio`.",
        "",
        f"## Clean Register Candidates ({len(clean)})",
        "",
        table(clean),
        "",
        "These are the strongest master-data candidates because they are outside the active 01.08/01.09 collapse section and stay high for most observed days.",
        "",
        f"## Operationally Confounded High-Ratio Units ({len(confounded)})",
        "",
        table(confounded),
        "",
        "These sit in sections 01.08/01.09, where the active collapse can distort peer ratios. Do not use them as register-only evidence without field inspection.",
        "",
        f"## Watch Only ({len(watch)})",
        "",
        table(watch),
    ]
    (OUT / "STALE_KWP_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    cols = [
        "inverter",
        "registered_kwp",
        "median_ratio",
        "pct_days_above_1_1",
        "implied_kwp_from_median",
        "kwp_gap",
        "registered_understated_pct",
    ]
    view = df[cols].copy().where(pd.notna(df[cols]), "")
    headers = [str(c) for c in view.columns]
    rows = [[str(value) for value in row] for row in view.to_numpy()]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
        for i in range(len(headers))
    ]
    header = "| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


if __name__ == "__main__":
    main()
