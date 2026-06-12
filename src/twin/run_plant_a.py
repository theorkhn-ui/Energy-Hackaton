"""Full Plant A analysis. Outputs findings to runs/plant_a/.

This runner is intentionally CSV-first so it works with the hackathon bundle
without pyarrow. Raw data stays outside git; by default the script reads the
local sibling folder:

    ../Data/Plant A (start here)

Override with PLANT_A_BASE if needed:

    $env:PLANT_A_BASE = "C:/path/to/Plant A (start here)"
    python src/twin/run_plant_a.py
"""
from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

STEP_H = 5 / 60  # 5-minute data
OUT = Path("runs/plant_a")


@dataclass(frozen=True)
class PlantPaths:
    base: Path
    monitoring: Path
    system_overview: Path
    tariffs: Path
    tickets: Path
    errorcodes: Path
    error_descriptions: Path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = resolve_paths()

    print(f"Plant A base: {paths.base}")
    print("loading monitoring data...")
    pac, irrad, altitude, dv, evu = load_monitoring(paths.monitoring)
    print(f"  {pac.shape[0]:,} rows x {pac.shape[1]} inverters, "
          f"{pac.index.min()} -> {pac.index.max()}")

    kwp, missing = load_kwp(paths.system_overview, pac.columns)
    if missing:
        raise RuntimeError(f"missing kWp values for: {', '.join(missing)}")
    print(f"  kWp matched from System_Overview: {kwp.notna().sum()} / {len(kwp)}")

    first_production = first_production_times(pac, irrad, kwp)
    pac_operational = mask_pre_commissioning(pac, first_production)

    curtailed = compute_curtailment(dv, evu, pac.index)
    print(f"  curtailed steps: {int(curtailed.sum()):,} "
          f"({curtailed.mean() * 100:.2f}% of all)")

    day_e, day_g, ratio = compute_daily_ratio(pac_operational, irrad, kwp)
    ratio.index.name = "timestamp"
    ratio.to_csv(OUT / "daily_peer_ratio.csv")

    under = compute_underperformers(ratio, day_e, paths.tariffs)
    under.to_csv(OUT / "underperformers.csv")
    print("\n== chronic underperformers (last 365d, ranked by EUR lost) ==")
    print(under.head(15).to_string() if len(under) else "none")

    outages = compute_outages(pac_operational, irrad, curtailed)
    outages.to_csv(OUT / "outage_hours.csv")
    print("\n== top outage inverters (daylight, non-curtailed, peers producing) ==")
    print(outages.head(10).to_string() if len(outages) else "none")

    drift = compute_drift(ratio)
    drift.to_csv(OUT / "drift_365d.csv", header=["drift_ratio_365d"])
    print("\n== largest negative drift over last 365d (soiling candidates) ==")
    print(drift.head(10).round(3).to_string() if len(drift) else "none")

    tickets = load_tickets(paths.tickets)
    tickets.to_csv(OUT / "tickets_parsed.csv", index=False)
    print(f"\n== normalized tickets: {len(tickets)} | components: "
          f"{tickets['component'].value_counts().head(6).to_dict()}")

    metadata = pd.DataFrame({
        "metric": [
            "monitoring_rows",
            "inverters",
            "start",
            "end",
            "curtailed_steps",
            "curtailed_pct",
            "matched_kwp",
        ],
        "value": [
            len(pac),
            len(pac.columns),
            pac.index.min(),
            pac.index.max(),
            int(curtailed.sum()),
            round(float(curtailed.mean() * 100), 4),
            int(kwp.notna().sum()),
        ],
    })
    metadata.to_csv(OUT / "run_metadata.csv", index=False)

    write_plots(ratio, under, pd.DataFrame())
    print(f"\nsaved outputs -> {OUT.resolve()}")


def resolve_paths() -> PlantPaths:
    candidates = []
    env_base = os.environ.get("PLANT_A_BASE")
    if env_base:
        candidates.append(Path(env_base))

    repo_root = Path.cwd()
    candidates.extend([
        repo_root / "data/raw/EP-Challenge-Final -/Plant A (start here)",
        repo_root.parent / "Data/Plant A (start here)",
        repo_root / "Data/Plant A (start here)",
    ])

    for base in candidates:
        if (base / "1. Main-monitoring-data/main_monitoring_data.csv").exists():
            return PlantPaths(
                base=base,
                monitoring=base / "1. Main-monitoring-data/main_monitoring_data.csv",
                system_overview=base / "2. Additional Data/System_Overview.xlsx",
                tariffs=base / "2. Additional Data/feed-in-tarrifs.xlsx",
                tickets=base / "2. Additional Data/Tickets.xlsx",
                errorcodes=base / "3. Errorcodes/errorcodes.csv",
                error_descriptions=base / "3. Errorcodes/errorcodes description (important).xlsx",
            )
    searched = "\n  - ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"could not find Plant A data. Searched:\n  - {searched}")


def load_monitoring(path: Path) -> tuple[pd.DataFrame, pd.Series, pd.Series | None, pd.Series | None, pd.Series | None]:
    header = pd.read_csv(path, sep=";", nrows=0, encoding="utf-8-sig").columns.tolist()
    ts_col = find_column(header, lambda c: c.lower() == "timestamp" or "time" in c.lower())
    pac_cols = [c for c in header if inverter_id(c) and "P_AC" in c]
    extra_cols = [
        find_column(header, lambda c: "Irradiation" in c),
        find_column(header, lambda c: "Altitude" in c, required=False),
        find_column(header, lambda c: re.search(r"/\s*DV\b", c), required=False),
        find_column(header, lambda c: re.search(r"/\s*EVU\b", c), required=False),
    ]
    usecols = [ts_col] + pac_cols + [c for c in extra_cols if c]
    dtype = {c: "float32" for c in usecols if c != ts_col}
    df = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        usecols=usecols,
        dtype=dtype,
        na_values=["", "nan", "NaN"],
        low_memory=False,
    )
    df.index = pd.to_datetime(df.pop(ts_col), format="%Y.%m.%d %H:%M", errors="coerce")
    df = df[~df.index.isna()].sort_index()

    pac = df[pac_cols].rename(columns={c: inverter_id(c) for c in pac_cols})
    irrad_col = find_column(df.columns, lambda c: "Irradiation" in c)
    altitude_col = find_column(df.columns, lambda c: "Altitude" in c, required=False)
    dv_col = find_column(df.columns, lambda c: re.search(r"/\s*DV\b", c), required=False)
    evu_col = find_column(df.columns, lambda c: re.search(r"/\s*EVU\b", c), required=False)
    return (
        pac,
        df[irrad_col],
        df[altitude_col] if altitude_col else None,
        df[dv_col] if dv_col else None,
        df[evu_col] if evu_col else None,
    )


def load() -> tuple[pd.DataFrame, pd.Series, pd.Series | None, pd.Series | None]:
    """Compatibility wrapper used by deep_analysis.py and collapse_cost.py."""
    paths = resolve_paths()
    pac, irrad, _altitude, dv, evu = load_monitoring(paths.monitoring)
    return pac, irrad, dv, evu


def load_kwp(path_or_pac_cols, pac_cols: pd.Index | list[str] | None = None) -> tuple[pd.Series, list[str]]:
    """Load installed kWp.

    Supports both call forms:
    - load_kwp(system_overview_path, pac_cols)
    - load_kwp(pac_cols)  # legacy interface used by collapse_cost.py
    """
    if pac_cols is None:
        path = resolve_paths().system_overview
        pac_cols = path_or_pac_cols
    else:
        path = Path(path_or_pac_cols)

    so = pd.read_excel(path, header=2)
    so.columns = [str(c).strip() for c in so.columns]
    desc_col = find_column(so.columns, lambda c: so[c].astype(str).str.contains(r"WR\s+\d", regex=True).any())
    kwp_col = find_column(so.columns, lambda c: "PDC" in str(c))

    rows = so[so[desc_col].astype(str).str.contains(r"WR\s+\d", regex=True, na=False)]
    kwp = {}
    for _, row in rows.iterrows():
        inv = inverter_id_from_wr(row[desc_col])
        if inv is None:
            continue
        kwp[inv] = kwp.get(inv, 0.0) + float(row[kwp_col] or 0.0)

    series = pd.Series(kwp, dtype="float64").reindex(pac_cols)
    missing = [str(c) for c in pac_cols if pd.isna(series.loc[c])]
    return series, missing


def first_production_times(pac: pd.DataFrame, irrad: pd.Series, kwp: pd.Series) -> pd.Series:
    starts = {}
    sun = irrad > 100
    for inv in pac.columns:
        threshold = max(1.0, float(kwp[inv]) * 0.03)
        producing = sun & pac[inv].gt(threshold)
        starts[inv] = producing[producing].index.min() if producing.any() else pac.index.min()
    return pd.Series(starts)


def mask_pre_commissioning(pac: pd.DataFrame, first_production: pd.Series) -> pd.DataFrame:
    out = pac.copy()
    for inv, start in first_production.items():
        out.loc[out.index < start, inv] = np.nan
    return out


def compute_curtailment(dv: pd.Series | None, evu: pd.Series | None, index: pd.DatetimeIndex) -> pd.Series:
    curtailed = pd.Series(False, index=index)
    for sig in (dv, evu):
        if sig is not None:
            curtailed |= sig.fillna(100).lt(99)
    return curtailed


def compute_daily_ratio(
    pac: pd.DataFrame,
    irrad: pd.Series,
    kwp: pd.Series,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    day_e = pac.resample("D").sum(min_count=1) * STEP_H
    day_g = (irrad.clip(lower=0).resample("D").sum(min_count=1) * STEP_H) / 1000.0
    pi = day_e.div(kwp, axis=1).div(day_g.where(day_g > 0.3), axis=0)
    pi = pi.where(day_e.notna())
    ratio = pi.div(pi.median(axis=1), axis=0).replace([np.inf, -np.inf], np.nan)
    return day_e, day_g, ratio


def compute_underperformers(ratio: pd.DataFrame, day_e: pd.DataFrame, tariff_path: Path) -> pd.DataFrame:
    recent = last_days(ratio, 365)
    stats = pd.DataFrame({
        "mean_ratio": recent.mean(),
        "days_below_95": (recent < 0.95).sum(),
        "days_below_80": (recent < 0.80).sum(),
        "days_observed": recent.notna().sum(),
    })
    under = stats[(stats.mean_ratio < 0.97) & (stats.days_below_95 > 30)].copy()
    if under.empty:
        return under

    lost_kwh, lost_eur = estimate_losses(day_e.loc[recent.index], recent, tariff_path)
    under["lost_kwh_365d"] = lost_kwh.reindex(under.index).round(0)
    under["lost_eur_365d"] = lost_eur.reindex(under.index).round(0)
    under = under.sort_values("lost_eur_365d", ascending=False)
    return under


def estimate_losses(day_e: pd.DataFrame, ratio: pd.DataFrame, tariff_path: Path) -> tuple[pd.Series, pd.Series]:
    expected = day_e.div(ratio.clip(lower=0.2))
    lost_kwh = (expected - day_e).clip(lower=0).sum()
    tariffs = load_recent_tariffs(tariff_path)
    lost_eur = lost_kwh * tariffs.reindex(lost_kwh.index).fillna(tariffs.mean()) / 100.0
    return lost_kwh, lost_eur


def load_recent_tariffs(path: Path) -> pd.Series:
    tar = pd.read_excel(path, header=None)
    inv = tar.iloc[2:, 0].astype(str).str.extract(r"INV\s*([\d.]+)")[0]
    values = tar.iloc[2:, -100:].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return pd.Series(values.values, index=inv.values).dropna()


def compute_outages(pac: pd.DataFrame, irrad: pd.Series, curtailed: pd.Series) -> pd.DataFrame:
    sun = irrad > 100
    peers_on = pac.median(axis=1, skipna=True) > 1.0
    valid = sun & peers_on & ~curtailed
    candidate = pac.notna() & pac.le(0.01)
    out_steps = candidate[valid].sum()
    valid_steps = int(valid.sum())
    if valid_steps == 0:
        return pd.DataFrame(columns=["outage_hours_total", "pct_of_sun_hours"])
    outages = pd.DataFrame({
        "outage_hours_total": (out_steps * STEP_H).round(1),
        "pct_of_sun_hours": (out_steps / valid_steps * 100).round(2),
    }).sort_values("outage_hours_total", ascending=False)
    return outages[outages["outage_hours_total"] > 0]


def compute_drift(ratio: pd.DataFrame) -> pd.Series:
    recent = last_days(ratio, 365)
    if recent.empty:
        return pd.Series(dtype="float64")
    roll = recent.rolling(21, min_periods=10).mean()
    return (roll.iloc[-1] - roll.iloc[:30].mean()).sort_values()


def load_tickets(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames = []
    for sheet in xl.sheet_names:
        raw = xl.parse(sheet)
        if {"component", "startdate"}.issubset(raw.columns):
            part = pd.DataFrame({
                "component": raw["component"].map(normalize_component),
                "start": parse_datetime(raw["startdate"]),
                "end": parse_datetime(raw.get("enddate")),
                "category": raw.get("category"),
                "source_sheet": sheet,
            })
        else:
            start = combine_date_time(raw.get("Start Date"), raw.get("Uhrzeit Beginn"))
            end = combine_date_time(raw.get("Datum Ende"), raw.get("Uhrzeit Ende"))
            part = pd.DataFrame({
                "component": raw.get("Komponente", pd.Series(index=raw.index, dtype=object)).map(normalize_component),
                "start": start,
                "end": end,
                "category": raw.get("Störungsart/ Beanstandung"),
                "source_sheet": sheet,
            })
        frames.append(part)

    tickets = pd.concat(frames, ignore_index=True)
    tickets = tickets.dropna(subset=["start"]).copy()
    tickets["end"] = tickets["end"].fillna(tickets["start"] + pd.Timedelta(days=1))
    tickets["category"] = tickets["category"].fillna("(blank)").astype(str)
    return tickets.sort_values("start").reset_index(drop=True)


def load_errors(path: Path, desc_path: Path) -> tuple[pd.DataFrame, dict[int, str]]:
    print("loading error codes...")
    header = pd.read_csv(path, sep=";", nrows=0, encoding="utf-8-sig").columns.tolist()
    ts_col = find_column(header, lambda c: c.lower() == "timestamp" or "time" in c.lower())
    error_cols = [c for c in header if c.endswith(" / Error") and inverter_id(c)]
    dtype = {c: "float32" for c in error_cols}
    df = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        usecols=[ts_col] + error_cols,
        dtype=dtype,
        na_values=["", "nan", "NaN"],
        low_memory=False,
    )
    df.index = pd.to_datetime(df.pop(ts_col), format="%Y.%m.%d %H:%M", errors="coerce")
    df = df[~df.index.isna()].sort_index()
    df = df.rename(columns={c: inverter_id(c) for c in error_cols})

    desc_raw = pd.read_excel(desc_path)
    desc = {}
    for _, row in desc_raw.iterrows():
        code = row.get("Dezimal")
        text = row.get("Code")
        if pd.notna(code):
            desc[int(code)] = str(text)
    return df, desc


def build_events(
    ratio: pd.DataFrame,
    day_e: pd.DataFrame,
    tariff_path: Path,
    tickets: pd.DataFrame,
    errors: pd.DataFrame,
    error_desc: dict[int, str],
) -> pd.DataFrame:
    recent = last_days(ratio, 365)
    lost_kwh, lost_eur = estimate_losses(day_e.loc[recent.index], recent, tariff_path)
    events = []
    threshold = 0.85
    min_days = 7
    for inv in recent.columns:
        low = recent[inv].lt(threshold).fillna(False)
        for start, end in consecutive_true_windows(low):
            days = int((end - start).days) + 1
            if days < min_days:
                continue
            window = recent.loc[start:end, inv]
            err_code, err_count, err_text = top_error_for_window(errors, error_desc, inv, start, end)
            ticket = nearest_ticket(tickets, inv, start, end)
            active = end >= recent.index.max() - pd.Timedelta(days=7)
            label = classify_event(err_code, ticket, active)
            events.append({
                "inverter": inv,
                "event_start": start.date().isoformat(),
                "event_end": end.date().isoformat(),
                "duration_days": days,
                "active_now": bool(active),
                "mean_ratio": round(float(window.mean()), 3),
                "min_ratio": round(float(window.min()), 3),
                "lost_kwh_365d": round(float(lost_kwh.get(inv, 0.0)), 0),
                "lost_eur_365d": round(float(lost_eur.get(inv, 0.0)), 0),
                "cause_label": label,
                "top_error_code": err_code,
                "top_error_count": err_count,
                "error_description": err_text,
                "nearest_ticket_component": ticket.get("component"),
                "nearest_ticket_category": ticket.get("category"),
                "nearest_ticket_start": ticket.get("start"),
                "model_lead_days": ticket.get("lead_days"),
            })

    if not events:
        return pd.DataFrame()
    out = pd.DataFrame(events)
    out["rank_score"] = (
        out["active_now"].astype(int) * 100000
        + out["lost_eur_365d"].fillna(0)
        + out["duration_days"].fillna(0)
    )
    return out.sort_values(["rank_score", "lost_eur_365d"], ascending=False).drop(columns=["rank_score"])


def build_ticket_leads(events: pd.DataFrame, tickets: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()
    rows = []
    inv_events = events.copy()
    inv_events["event_start_dt"] = pd.to_datetime(inv_events["event_start"])
    inv_events["event_end_dt"] = pd.to_datetime(inv_events["event_end"])
    for _, ticket in tickets.iterrows():
        component = ticket["component"]
        if not isinstance(component, str) or not component.startswith("INV "):
            continue
        inv = component.replace("INV ", "")
        cand = inv_events[inv_events["inverter"].eq(inv)].copy()
        if cand.empty:
            continue
        cand["lead_days"] = (ticket["start"] - cand["event_start_dt"]).dt.days
        cand = cand[(cand["lead_days"] >= 0) & (cand["lead_days"] <= 180)]
        if cand.empty:
            continue
        best = cand.sort_values("lead_days").iloc[0]
        rows.append({
            "ticket_component": component,
            "ticket_start": ticket["start"].date().isoformat(),
            "ticket_category": ticket["category"],
            "flagged_event_start": best["event_start"],
            "flagged_event_end": best["event_end"],
            "lead_days": int(best["lead_days"]),
            "event_mean_ratio": best["mean_ratio"],
        })
    return pd.DataFrame(rows).sort_values("lead_days", ascending=False) if rows else pd.DataFrame()


def build_ticket_validation(tickets: pd.DataFrame, outages: pd.DataFrame, under: pd.DataFrame) -> pd.DataFrame:
    inv_tickets = tickets[tickets["component"].astype(str).str.startswith("INV ")].copy()
    if inv_tickets.empty:
        return pd.DataFrame()
    ticket_counts = inv_tickets["component"].str.replace("INV ", "", regex=False).value_counts()
    index = sorted(set(ticket_counts.index) | set(outages.index) | set(under.index))
    out = pd.DataFrame({"inverter": index})
    out["ticket_count"] = out["inverter"].map(ticket_counts).fillna(0).astype(int)
    out["outage_hours_total"] = out["inverter"].map(outages["outage_hours_total"]).fillna(0).round(1)
    out["lost_eur_365d"] = out["inverter"].map(under["lost_eur_365d"]).fillna(0).round(0)
    out = out[(out["ticket_count"] > 0) | (out["outage_hours_total"] > 0) | (out["lost_eur_365d"] > 0)]
    return out.sort_values(["ticket_count", "outage_hours_total", "lost_eur_365d"], ascending=False)


def write_plots(ratio: pd.DataFrame, under: pd.DataFrame, events: pd.DataFrame) -> None:
    monthly = ratio.resample("ME").mean()
    if plt is None:
        write_svg_heatmap(monthly, OUT / "heatmap_monthly_ratio.svg")
        if not under.empty:
            write_svg_bar(under.head(12).sort_values("lost_eur_365d"), OUT / "top_underperformers.svg")
        if not events.empty:
            write_svg_timeline(events.head(12), OUT / "event_timeline.svg")
        return

    fig, ax = plt.subplots(figsize=(16, 10))
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad("#eeeeee")
    im = ax.imshow(np.ma.masked_invalid(monthly.T.values), aspect="auto", cmap=cmap,
                   vmin=0.7, vmax=1.1, interpolation="nearest")
    ax.set_yticks(range(len(monthly.columns)), monthly.columns, fontsize=5)
    step = max(1, len(monthly) // 24)
    ax.set_xticks(range(0, len(monthly), step),
                  [d.strftime("%Y-%m") for d in monthly.index[::step]],
                  rotation=45, fontsize=7)
    ax.set_title("Plant A digital twin: peer-normalized inverter performance")
    fig.colorbar(im, label="ratio vs plant median")
    fig.tight_layout()
    fig.savefig(OUT / "heatmap_monthly_ratio.png", dpi=150)
    plt.close(fig)

    if not under.empty:
        top = under.head(12).sort_values("lost_eur_365d")
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.barh(top.index, top["lost_eur_365d"], color="#c13b2a")
        ax.set_xlabel("Estimated EUR lost, last 365 days")
        ax.set_title("Revenue-ranked chronic underperformers")
        fig.tight_layout()
        fig.savefig(OUT / "top_underperformers.png", dpi=150)
        plt.close(fig)

    if not events.empty:
        top = events.head(12).copy()
        top["start"] = pd.to_datetime(top["event_start"])
        top["end"] = pd.to_datetime(top["event_end"])
        top = top.sort_values("start")
        fig, ax = plt.subplots(figsize=(11, 6))
        for y, (_, row) in enumerate(top.iterrows()):
            ax.barh(y, (row["end"] - row["start"]).days + 1, left=row["start"],
                    color="#2d6f8f" if row["active_now"] else "#7a8793")
        ax.set_yticks(range(len(top)), top["inverter"])
        ax.set_title("Ranked anomaly windows")
        ax.set_xlabel("Date")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(OUT / "event_timeline.png", dpi=150)
        plt.close(fig)


def write_svg_heatmap(monthly: pd.DataFrame, path: Path) -> None:
    invs = list(monthly.columns)
    dates = list(monthly.index)
    left, top, right, bottom = 92, 44, 150, 72
    plot_w = 1320
    plot_h = max(620, len(invs) * 12)
    width = left + plot_w + right
    height = top + plot_h + bottom
    cell_w = plot_w / max(1, len(dates))
    cell_h = plot_h / max(1, len(invs))

    parts = [svg_start(width, height)]
    parts.append(svg_text(left, 24, "Plant A digital twin: peer-normalized inverter performance", 18, "bold"))
    for y, inv in enumerate(invs):
        cy = top + y * cell_h + cell_h * 0.72
        parts.append(svg_text(8, cy, inv, 8, "normal", "#334e68"))
        for x, _ in enumerate(dates):
            val = monthly.iloc[x, y]
            parts.append(
                f'<rect x="{left + x * cell_w:.2f}" y="{top + y * cell_h:.2f}" '
                f'width="{cell_w + 0.2:.2f}" height="{cell_h + 0.2:.2f}" '
                f'fill="{ratio_color(val)}" />'
            )

    step = max(1, len(dates) // 14)
    for x in range(0, len(dates), step):
        label = dates[x].strftime("%Y-%m")
        tx = left + x * cell_w
        parts.append(
            f'<text x="{tx:.2f}" y="{top + plot_h + 18}" font-size="9" '
            f'transform="rotate(45 {tx:.2f},{top + plot_h + 18})">{html.escape(label)}</text>'
        )

    legend_x = left + plot_w + 35
    for i in range(80):
        value = 1.1 - i * 0.4 / 79
        parts.append(
            f'<rect x="{legend_x}" y="{top + i * 4}" width="20" height="4" '
            f'fill="{ratio_color(value)}" />'
        )
    for value in [1.10, 1.00, 0.90, 0.80, 0.70]:
        y = top + (1.1 - value) / 0.4 * 79 * 4
        parts.append(svg_text(legend_x + 28, y + 4, f"{value:.2f}", 10))
    parts.append(svg_text(legend_x - 8, top + 350, "ratio vs median", 10))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_svg_bar(top: pd.DataFrame, path: Path) -> None:
    left, top_margin, width, row_h = 120, 44, 760, 30
    height = top_margin + len(top) * row_h + 54
    max_value = max(1.0, float(top["lost_eur_365d"].max()))
    parts = [svg_start(left + width + 130, height)]
    parts.append(svg_text(left, 24, "Revenue-ranked chronic underperformers", 18, "bold"))
    for i, (inv, row) in enumerate(top.iterrows()):
        y = top_margin + i * row_h
        value = float(row["lost_eur_365d"])
        bar_w = width * value / max_value
        parts.append(svg_text(8, y + 18, str(inv), 12))
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.2f}" height="20" fill="#c13b2a" />')
        parts.append(svg_text(left + bar_w + 8, y + 15, f"EUR {value:.0f}", 12))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_svg_timeline(events: pd.DataFrame, path: Path) -> None:
    data = events.copy()
    data["start"] = pd.to_datetime(data["event_start"])
    data["end"] = pd.to_datetime(data["event_end"])
    data = data.sort_values("start")
    min_date = data["start"].min()
    max_date = data["end"].max()
    span = max(1, (max_date - min_date).days)
    left, top_margin, width, row_h = 110, 44, 860, 30
    height = top_margin + len(data) * row_h + 58
    parts = [svg_start(left + width + 160, height)]
    parts.append(svg_text(left, 24, "Ranked anomaly windows", 18, "bold"))
    for i, (_, row) in enumerate(data.iterrows()):
        y = top_margin + i * row_h
        start_x = left + (row["start"] - min_date).days / span * width
        end_x = left + ((row["end"] - min_date).days + 1) / span * width
        color = "#2d6f8f" if bool(row["active_now"]) else "#7a8793"
        parts.append(svg_text(8, y + 18, row["inverter"], 12))
        parts.append(
            f'<rect x="{start_x:.2f}" y="{y}" width="{max(2, end_x - start_x):.2f}" '
            f'height="20" fill="{color}" />'
        )
        parts.append(svg_text(end_x + 6, y + 15, row["cause_label"], 11, "normal", "#334e68"))
    parts.append(svg_text(left, height - 18, min_date.date().isoformat(), 11))
    parts.append(svg_text(left + width - 72, height - 18, max_date.date().isoformat(), 11))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def ratio_color(value: object) -> str:
    if pd.isna(value):
        return "#eeeeee"
    val = min(1.1, max(0.7, float(value)))
    t = (val - 0.7) / 0.4
    red = (190, 24, 45)
    yellow = (255, 238, 150)
    green = (30, 132, 73)
    if t < 0.5:
        return interpolate_color(red, yellow, t / 0.5)
    return interpolate_color(yellow, green, (t - 0.5) / 0.5)


def interpolate_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> str:
    rgb = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def svg_start(width: float, height: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">'
        '<rect width="100%" height="100%" fill="white" />'
    )


def svg_text(x: float, y: float, text: object, size: int, weight: str = "normal", color: str = "#102a43") -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(str(text))}</text>'
    )


def write_findings(
    metadata: pd.DataFrame,
    under: pd.DataFrame,
    outages: pd.DataFrame,
    drift: pd.Series,
    events: pd.DataFrame,
    ticket_leads: pd.DataFrame,
    ticket_validation: pd.DataFrame,
) -> None:
    meta = dict(zip(metadata["metric"], metadata["value"]))
    lines = [
        "# Plant A Digital Twin Findings",
        "",
        f"Data: {int(meta['monitoring_rows']):,} five-minute rows, "
        f"{int(meta['inverters'])} inverters, {meta['start']} -> {meta['end']}.",
        f"kWp matched for {int(meta['matched_kwp'])} inverters. "
        f"Curtailment steps: {int(meta['curtailed_steps']):,} "
        f"({float(meta['curtailed_pct']):.2f}% of all steps).",
        "",
        "## Headline story",
    ]
    if not events.empty:
        active = events[events["active_now"]].head(5)
        if not active.empty:
            invs = ", ".join(active["inverter"].tolist())
            lines.append(f"- Live issue: active underperformance is still visible in {invs}.")
        if "01.03.018" in events["inverter"].values:
            miss = events[events["inverter"].eq("01.03.018")].iloc[0]
            lines.append(
                "- Missed issue: INV 01.03.018 is a chronic underperformer "
                f"(mean ratio {miss['mean_ratio']}, estimated EUR {miss['lost_eur_365d']:.0f}/yr) "
                "with no inverter-specific ticket in the matched event window."
            )
    if not ticket_leads.empty:
        lines.append(
            f"- Validation: {len(ticket_leads)} inverter tickets have a preceding model flag "
            "within 180 days."
        )
    if not ticket_validation.empty:
        top_validation = ticket_validation.head(2)
        validation_text = ", ".join(
            f"{row.inverter} ({row.ticket_count} tickets, {row.outage_hours_total:.1f} outage h)"
            for row in top_validation.itertuples(index=False)
        )
        lines.append(f"- Ticket-heavy inverters also rank high after outage cleanup: {validation_text}.")

    lines.extend([
        "",
        "## Top chronic underperformers",
        markdown_table(under.reset_index(names="inverter").head(12)),
        "",
        "## Top outage hours after cleanup",
        markdown_table(outages.reset_index(names="inverter").head(12)),
        "",
        "## Ranked event table",
        markdown_table(events.head(12)),
        "",
        "## Ticket lead-time matches",
        markdown_table(ticket_leads.head(12)),
        "",
        "## Ticket validation",
        markdown_table(ticket_validation.head(12)),
        "",
        "## Drift candidates",
        markdown_table(drift.head(12).reset_index().rename(columns={"index": "inverter", 0: "drift_ratio_365d"})),
        "",
        "## Caveats",
        "- The model is peer-normalized, so plant-wide effects are intentionally suppressed.",
        "- Inverters with persistent ratio above 1.1 should be treated as an asset-register or kWp-calibration finding, not as extra performance.",
        "- Error descriptions are attached when the inverter emits a nonzero code during the ranked event window.",
    ])
    (OUT / "FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    metadata: pd.DataFrame,
    under: pd.DataFrame,
    outages: pd.DataFrame,
    drift: pd.Series,
    events: pd.DataFrame,
    ticket_leads: pd.DataFrame,
    ticket_validation: pd.DataFrame,
) -> None:
    meta = dict(zip(metadata["metric"], metadata["value"]))
    heatmap_img = choose_plot("heatmap_monthly_ratio")
    under_img = choose_plot("top_underperformers")
    event_img = choose_plot("event_timeline")
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Plant A Digital Twin Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2933; }}
h1, h2 {{ color: #102a43; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; }}
.kpi {{ border: 1px solid #d9e2ec; border-radius: 6px; padding: 12px; }}
.kpi strong {{ display: block; font-size: 22px; color: #0b7285; }}
img {{ max-width: 100%; border: 1px solid #d9e2ec; margin: 12px 0 24px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin-bottom: 24px; }}
th, td {{ border: 1px solid #d9e2ec; padding: 6px 8px; text-align: left; vertical-align: top; }}
th {{ background: #f0f4f8; }}
</style>
</head>
<body>
<h1>Plant A Digital Twin Report</h1>
<div class="kpis">
  <div class="kpi"><strong>{int(meta['monitoring_rows']):,}</strong>5-min rows</div>
  <div class="kpi"><strong>{int(meta['inverters'])}</strong>inverters</div>
  <div class="kpi"><strong>{float(meta['curtailed_pct']):.2f}%</strong>curtailed steps</div>
  <div class="kpi"><strong>{int(meta['matched_kwp'])}</strong>matched kWp records</div>
</div>
<h2>Performance Heatmap</h2>
<img src="{heatmap_img}" alt="Plant A heatmap">
<h2>Top Underperformers</h2>
<img src="{under_img}" alt="Top underperformers">
{html_table(under.reset_index(names='inverter').head(12))}
<h2>Ranked Events</h2>
<img src="{event_img}" alt="Event timeline">
{html_table(events.head(12))}
<h2>Ticket Lead Times</h2>
{html_table(ticket_leads.head(12))}
<h2>Ticket Validation</h2>
{html_table(ticket_validation.head(12))}
<h2>Outage Cleanup</h2>
{html_table(outages.reset_index(names='inverter').head(12))}
<h2>Drift Candidates</h2>
{html_table(drift.head(12).reset_index().rename(columns={'index': 'inverter', 0: 'drift_ratio_365d'}))}
</body>
</html>
"""
    (OUT / "report.html").write_text(html_doc, encoding="utf-8")


def choose_plot(stem: str) -> str:
    if plt is None:
        return f"{stem}.svg"
    if (OUT / f"{stem}.png").exists():
        return f"{stem}.png"
    return f"{stem}.svg"


def write_storyboard(events: pd.DataFrame, under: pd.DataFrame, ticket_leads: pd.DataFrame) -> None:
    active = events[events["active_now"]].head(4)["inverter"].tolist() if not events.empty else []
    missed = under.loc[under.index == "01.03.018"].iloc[0] if "01.03.018" in under.index else None
    lines = [
        "# 4-Minute Video Storyboard",
        "",
        "## 0:00-0:30 - Hook",
        "Show the heatmap. Say: this is a living model of 65 inverters over 9.4 years, not a static dashboard.",
        "",
        "## 0:30-1:30 - Live issue",
        "Zoom into the active red block near the latest months.",
        f"Call out active inverters: {', '.join(active) if active else 'see events_ranked.csv'}.",
        "",
        "## 1:30-2:30 - Missed issue",
    ]
    if missed is not None:
        lines.append(
            f"Show INV 01.03.018: mean ratio {missed['mean_ratio']:.2f}, "
            f"{missed['days_below_95']:.0f} days below 0.95, "
            f"about EUR {missed['lost_eur_365d']:.0f}/yr lost."
        )
    else:
        lines.append("Show the top un-ticketed chronic underperformer from underperformers.csv.")
    lines.extend([
        "",
        "## 2:30-3:20 - Validation",
        f"Show ticket lead-time table: {len(ticket_leads)} matched tickets have prior model flags.",
        "Explain that known ticket-heavy inverters also rank high in the model.",
        "",
        "## 3:20-4:00 - Why it matters",
        "Close on the EUR-ranked event table: operators get where, when, likely cause, and money impact.",
    ])
    (OUT / "VIDEO_STORYBOARD.md").write_text("\n".join(lines), encoding="utf-8")


def classify_event(err_code: int | None, ticket: dict, active: bool) -> str:
    if err_code:
        return "Known fault from inverter error code"
    if ticket.get("component"):
        return "Ticket-linked underperformance"
    if active:
        return "Active unclassified underperformance"
    return "Unclassified underperformance"


def top_error_for_window(
    errors: pd.DataFrame,
    error_desc: dict[int, str],
    inv: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[int | None, int, str | None]:
    if inv not in errors.columns:
        return None, 0, None
    mask = (errors.index >= start) & (errors.index < end + pd.Timedelta(days=1))
    values = errors.loc[mask, inv].dropna().round().astype("int64")
    values = values[values.ne(0)]
    if values.empty:
        return None, 0, None
    code = int(values.value_counts().idxmax())
    count = int(values.eq(code).sum())
    return code, count, error_desc.get(code)


def nearest_ticket(tickets: pd.DataFrame, inv: str, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    if tickets.empty:
        return {}
    component = f"INV {inv}"
    relevant = tickets[tickets["component"].isin([component, "Plant"])].copy()
    if relevant.empty:
        return {}
    relevant["overlap"] = (relevant["start"] <= end) & (relevant["end"] >= start)
    relevant["lead_days"] = (relevant["start"] - start).dt.days
    relevant["distance"] = relevant["lead_days"].abs()
    overlapping = relevant[relevant["overlap"]]
    if not overlapping.empty:
        row = overlapping.sort_values("distance").iloc[0]
    else:
        candidates = relevant[(relevant["lead_days"] >= 0) & (relevant["lead_days"] <= 180)]
        if candidates.empty:
            return {}
        row = candidates.sort_values("lead_days").iloc[0]
    return {
        "component": row["component"],
        "category": row["category"],
        "start": row["start"].date().isoformat(),
        "lead_days": int(row["lead_days"]),
    }


def consecutive_true_windows(series: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    windows = []
    current_start = None
    previous = None
    for ts, value in series.items():
        if bool(value) and current_start is None:
            current_start = ts
        if not bool(value) and current_start is not None:
            windows.append((current_start, previous))
            current_start = None
        previous = ts
    if current_start is not None:
        windows.append((current_start, previous))
    return windows


def last_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    if df.empty:
        return df
    return df.loc[df.index.max() - pd.Timedelta(days=days):]


def normalize_component(value: object) -> str:
    text = str(value or "").strip()
    m = re.search(r"INV\s+(\d{2}\.\d{2}\.\d{3})", text)
    if m:
        return f"INV {m.group(1)}"
    if text in {"Plant", "Gesamte Anlage", "Trafostation"}:
        return "Plant"
    return text or "(blank)"


def combine_date_time(date_series: pd.Series | None, time_series: pd.Series | None) -> pd.Series:
    if date_series is None:
        return pd.Series(dtype="datetime64[ns]")
    dates = pd.to_datetime(date_series, errors="coerce")
    if time_series is None:
        return dates
    times = time_series.fillna(pd.Timestamp("00:00").time()).astype(str)
    combined = dates.dt.strftime("%Y-%m-%d") + " " + times
    return pd.to_datetime(combined, errors="coerce")


def parse_datetime(values: pd.Series | None) -> pd.Series:
    if values is None:
        return pd.Series(dtype="datetime64[ns]")
    parsed = pd.to_datetime(values, errors="coerce", utc=True)
    return parsed.dt.tz_convert(None)


def inverter_id(column: object) -> str | None:
    match = re.search(r"INV\s+(\d{2}\.\d{2}\.\d{3})", str(column))
    return match.group(1) if match else None


def inverter_id_from_wr(value: object) -> str | None:
    match = re.search(r"WR\s+(\d+)\s*\.\s*(\d+)\s*\.\s*(\d+)", str(value))
    if not match:
        return None
    return f"{int(match.group(1)):02d}.{int(match.group(2)):02d}.{int(match.group(3)):03d}"


def find_column(columns, predicate, required: bool = True):
    for col in columns:
        if predicate(str(col)):
            return col
    if required:
        raise KeyError("required column not found")
    return None


def markdown_table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_None._"
    trimmed = df.copy()
    trimmed = trimmed.where(pd.notna(trimmed), "")
    headers = [str(c) for c in trimmed.columns]
    rows = [[str(value) for value in row] for row in trimmed.to_numpy()]
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


def html_table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "<p>None.</p>"
    cols = list(df.columns)
    rows = ["<table>", "<thead><tr>"]
    rows.extend(f"<th>{html.escape(str(c))}</th>" for c in cols)
    rows.append("</tr></thead><tbody>")
    for _, row in df.iterrows():
        rows.append("<tr>")
        for col in cols:
            rows.append(f"<td>{html.escape(str(row[col]))}</td>")
        rows.append("</tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


if __name__ == "__main__":
    main()
