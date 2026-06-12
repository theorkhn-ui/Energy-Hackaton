"""Automated fault classification for Plant A (Enerparc challenge).

Cross-references inverter error codes with 5-min power drops to categorise
incidents as TRIP / DERATE / NUISANCE.

Pipeline:
  1. Group error events into incidents (same inverter + code, <=2h gap).
  2. Measure power impact: mean P_AC during incident vs the inverter's own
     median P_AC at the same time-of-day over the surrounding +/-14 days
     (daylight slots only).
  3. Map German error meanings to code families (grid-side, power-stage,
     DC-link, insulation, other).
  4. Write incidents.csv, FAULT_CLASSIFICATION.md, fault_matrix.png to
     runs/plant_a/faults/.

Usage (from repo root):
  .venv/bin/python src/twin/fault_classify.py --stage cache   # ~30s, once
  .venv/bin/python src/twin/fault_classify.py --stage run
"""

import argparse
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_PARQUET = os.path.join(
    ROOT, "data", "raw", "EP-Challenge-Final -", "Plant A (start here)",
    "1. Main-monitoring-data", "main_monitoring_data.parquet")
EVENTS_CSV = os.path.join(ROOT, "runs", "plant_a", "error_events_clean.csv")
OUT_DIR = os.path.join(ROOT, "runs", "plant_a", "faults")
CACHE_PAC = os.path.join(OUT_DIR, "cache_pac.parquet")

MERGE_GAP = pd.Timedelta("2h")        # events closer than this -> one incident
SLOT = pd.Timedelta("5min")           # telemetry resolution
BASELINE_DAYS = 14                    # +/- window for time-of-day baseline
TRIP_MAX = 0.30                       # ratio < 0.30          -> TRIP
NUISANCE_MIN = 0.90                   # ratio > 0.90          -> NUISANCE
DAYLIGHT_FRAC = 0.05                  # baseline > 5% of inverter p99 = daylight

FAMILY_EN = {
    "grid-side": "Grid-side (undervoltage / ENS)",
    "power-stage": "Power-stage fault",
    "dc-link": "DC-link",
    "insulation": "Insulation",
    "other": "Other",
}

CODE_EN = {
    655626: "grid undervoltage (ENS)",
    655616: "power-stage fault",
    655363: "DC-link asymmetry low",
    655365: "DC-link (pos.) below nominal",
    655366: "DC-link (pos.) below nominal",
    655369: "DC-link (neg.) below nominal",
    655371: "DC-link (pos. boosted) exceeded",
    655372: "DC-link (neg. boosted) exceeded",
    655373: "grid overvoltage (ENS)",
    655379: "insulation test failure",
    655385: "grid voltage too low too long",
    663565: "device over-temperature",
}


def code_family(meaning: str) -> str:
    m = meaning.lower()
    if "zwischenkreis" in m:             # DC link (check first: 655365/66 mention
        return "dc-link"                 # "Netzscheitelwert" but are DC-link faults)
    if "netz" in m:                      # Netzunterspannung / Netzueberspannung / ENS
        return "grid-side"
    if "leistungsteil" in m or "störmeldung" in m or "stormeldung" in m:
        return "power-stage"
    if "isolation" in m:
        return "insulation"
    return "other"


def stage_cache() -> None:
    """Extract the 12 relevant P_AC columns from the big parquet once."""
    os.makedirs(OUT_DIR, exist_ok=True)
    events = pd.read_csv(EVENTS_CSV)
    invs = sorted(events["inverter"].unique())
    cols = [f"INV {i} / P_AC (kW)" for i in invs]
    df = pd.read_parquet(RAW_PARQUET, columns=cols)
    df.columns = invs
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, format="%Y.%m.%d %H:%M")
    df = df.sort_index()
    df.to_parquet(CACHE_PAC)
    print(f"cached {df.shape} -> {CACHE_PAC}")


def build_incidents(events: pd.DataFrame) -> pd.DataFrame:
    events = events.sort_values(["inverter", "code", "ts"])
    rows = []
    for (inv, code), g in events.groupby(["inverter", "code"]):
        ts = g["ts"].tolist()
        start, prev, n = ts[0], ts[0], 1
        for t in ts[1:]:
            if t - prev <= MERGE_GAP:
                prev, n = t, n + 1
            else:
                rows.append((inv, code, g["meaning"].iloc[0], start, prev, n))
                start, prev, n = t, t, 1
        rows.append((inv, code, g["meaning"].iloc[0], start, prev, n))
    inc = pd.DataFrame(rows, columns=["inverter", "code", "meaning",
                                      "start", "end", "n_events"])
    inc["duration_h"] = ((inc["end"] - inc["start"] + SLOT)
                         .dt.total_seconds() / 3600).round(3)
    return inc.sort_values("start").reset_index(drop=True)


def measure_impact(inc: pd.DataFrame, pac: pd.DataFrame) -> pd.DataFrame:
    """Add power-impact ratio, classification and lost energy per incident."""
    p99 = pac.quantile(0.99)            # per-inverter capacity proxy
    ratios, classes, losses, base_means, act_means = [], [], [], [], []

    for r in inc.itertuples():
        s = pac[r.inverter]
        # slots covering the incident (inclusive of the slot of the last event)
        win = s.loc[r.start: r.end + SLOT - pd.Timedelta("1s")]
        # +/-14d context for the same inverter
        ctx = s.loc[r.start - pd.Timedelta(days=BASELINE_DAYS):
                    r.end + pd.Timedelta(days=BASELINE_DAYS)]
        med = ctx.groupby(ctx.index.time).median()      # time-of-day baseline

        base = win.index.map(lambda t, m=med: m.get(t.time(), np.nan))
        base = pd.Series(np.asarray(base, dtype=float), index=win.index)
        daylight = base > DAYLIGHT_FRAC * p99[r.inverter]
        act = win[daylight & win.notna()]
        bas = base[daylight & win.notna()]

        if len(act) == 0 or bas.sum() <= 0:
            # incident entirely at night/dawn: no daylight baseline -> no
            # measurable energy impact (power_ratio stays NaN as a flag)
            ratios.append(np.nan)
            classes.append("NUISANCE")
            losses.append(0.0)
            base_means.append(np.nan)
            act_means.append(np.nan)
            continue

        ratio = act.mean() / bas.mean()
        lost_kwh = float(np.maximum(bas - act, 0).sum() * 5 / 60)
        if ratio < TRIP_MAX:
            cls = "TRIP"
        elif ratio <= NUISANCE_MIN:
            cls = "DERATE"
        else:
            cls = "NUISANCE"
        ratios.append(round(float(ratio), 3))
        classes.append(cls)
        losses.append(round(lost_kwh, 2))
        base_means.append(round(float(bas.mean()), 2))
        act_means.append(round(float(act.mean()), 2))

    inc = inc.copy()
    inc["power_ratio"] = ratios
    inc["mean_pac_kw"] = act_means
    inc["baseline_kw"] = base_means
    inc["lost_kwh"] = losses
    inc["classification"] = classes
    return inc


def make_chart(inc: pd.DataFrame, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = ["grid-side", "power-stage", "dc-link", "insulation", "other"]
    fams = [f for f in order if f in inc["family"].unique()]
    classes = ["TRIP", "DERATE", "NUISANCE"]
    colors = {"TRIP": "#d62728", "DERATE": "#ff9f1c", "NUISANCE": "#7f8c8d"}

    pivot = (inc.pivot_table(index="family", columns="classification",
                             values="start", aggfunc="count", fill_value=0)
             .reindex(fams).reindex(columns=classes, fill_value=0))

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    bottom = np.zeros(len(fams))
    x = np.arange(len(fams))
    for cls in classes:
        vals = pivot[cls].values.astype(float)
        ax.bar(x, vals, 0.62, bottom=bottom, color=colors[cls], label=cls)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v > 0:
                ax.text(xi, b + v / 2, f"{int(v)}", ha="center", va="center",
                        fontsize=15, fontweight="bold",
                        color="white" if v > pivot.values.max() * 0.04 else "black")
        bottom += vals

    lost = inc.groupby("family")["lost_kwh"].sum().reindex(fams).fillna(0)
    for xi, fam in enumerate(fams):
        ax.text(xi, bottom[xi] + pivot.values.sum() * 0.012,
                f"{lost[fam]/1000:.1f} MWh lost", ha="center", va="bottom",
                fontsize=14, color="#2c3e50", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([FAMILY_EN[f].replace(" (", "\n(") for f in fams],
                       fontsize=15)
    ax.set_ylabel("Incidents", fontsize=16)
    ax.set_title("Plant A fault classification — incidents by code family "
                 "(2017–2019)", fontsize=19, fontweight="bold", pad=14)
    ax.tick_params(axis="y", labelsize=14)
    ax.legend(fontsize=15, title="Power impact", title_fontsize=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, bottom.max() * 1.14)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}")


def write_md(inc: pd.DataFrame, path: str) -> None:
    classes = ["TRIP", "DERATE", "NUISANCE"]
    order = ["grid-side", "power-stage", "dc-link", "insulation", "other"]
    fams = [f for f in order if f in inc["family"].unique()]

    lines = [
        "# Fault classification — Plant A",
        "",
        f"Source: {len(pd.read_csv(EVENTS_CSV))} raw error events "
        f"(2017-01 .. 2019-11), merged into **{len(inc)} incidents** "
        "(same inverter + code, gaps <= 2 h).",
        "",
        "Classification = mean 5-min P_AC during incident vs the inverter's "
        "own median power at the same time-of-day over +/-14 days "
        "(daylight only): **TRIP** < 30% of normal, **DERATE** 30-90%, "
        "**NUISANCE** > 90% (incl. incidents fully outside daylight hours, "
        "which by definition cost no energy).",
        "",
        "## Code family x classification",
        "",
        "| Code family | TRIP | DERATE | NUISANCE | Total | Mean duration (h) | Est. lost energy (MWh) |",
        "|---|---|---|---|---|---|---|",
    ]
    for fam in fams:
        g = inc[inc["family"] == fam]
        cnt = g["classification"].value_counts()
        lines.append(
            f"| {FAMILY_EN[fam]} | {cnt.get('TRIP', 0)} | {cnt.get('DERATE', 0)} "
            f"| {cnt.get('NUISANCE', 0)} | {len(g)} | {g['duration_h'].mean():.2f} "
            f"| {g['lost_kwh'].sum()/1000:.2f} |")
    cnt = inc["classification"].value_counts()
    lines.append(
        f"| **All** | **{cnt.get('TRIP', 0)}** | **{cnt.get('DERATE', 0)}** "
        f"| **{cnt.get('NUISANCE', 0)}** | **{len(inc)}** "
        f"| **{inc['duration_h'].mean():.2f}** "
        f"| **{inc['lost_kwh'].sum()/1000:.2f}** |")

    lines += ["", "## Per-code breakdown", "",
              "| Code | Meaning (EN) | Family | Incidents | TRIP | DERATE | NUISANCE | Lost MWh |",
              "|---|---|---|---|---|---|---|---|"]
    per = inc.groupby("code")
    for code, g in sorted(per, key=lambda kv: -len(kv[1])):
        c = g["classification"].value_counts()
        lines.append(
            f"| {code} | {CODE_EN.get(code, g['meaning'].iloc[0][:40])} "
            f"| {g['family'].iloc[0]} | {len(g)} | {c.get('TRIP', 0)} "
            f"| {c.get('DERATE', 0)} | {c.get('NUISANCE', 0)} "
            f"| {g['lost_kwh'].sum()/1000:.2f} |")

    # takeaway numbers
    fam_loss = inc.groupby("family")["lost_kwh"].sum().sort_values(ascending=False)
    top_fam = fam_loss.index[0]
    trip_share = {f: (inc[inc['family'] == f]['classification'] == 'TRIP').mean()
                  for f in fams}
    nuis = cnt.get("NUISANCE", 0) / len(inc) * 100
    lines += [
        "", "## Takeaway", "",
        f"{FAMILY_EN[top_fam]} incidents are the real energy killers: they "
        f"account for {fam_loss.iloc[0]/1000:.1f} MWh of the "
        f"{inc['lost_kwh'].sum()/1000:.1f} MWh total estimated loss, with "
        f"{trip_share[top_fam]*100:.0f}% of them being full trips. "
        f"By contrast, {nuis:.0f}% of all incidents are NUISANCE events that "
        "show no measurable power impact and can be deprioritised in O&M "
        "alarm handling. Cross-referencing error codes with power drops thus "
        "turns ~9,200 raw alarms into a short, ranked work list of incidents "
        "that actually cost energy.",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {path}")


def stage_run() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    events = pd.read_csv(EVENTS_CSV, parse_dates=["ts"])
    pac = pd.read_parquet(CACHE_PAC)

    inc = build_incidents(events)
    inc["family"] = inc["meaning"].map(code_family)
    inc = measure_impact(inc, pac)
    inc["code_en"] = inc["code"].map(CODE_EN)

    out_csv = os.path.join(OUT_DIR, "incidents.csv")
    inc.to_csv(out_csv, index=False)
    print(f"wrote {out_csv} ({len(inc)} incidents)")
    print(inc["classification"].value_counts().to_string())
    print(inc.groupby("family")["lost_kwh"].sum().to_string())

    write_md(inc, os.path.join(OUT_DIR, "FAULT_CLASSIFICATION.md"))
    make_chart(inc, os.path.join(OUT_DIR, "fault_matrix.png"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=["cache", "run", "all"], default="all")
    args = ap.parse_args()
    if args.stage in ("cache", "all"):
        stage_cache()
    if args.stage in ("run", "all"):
        stage_run()
