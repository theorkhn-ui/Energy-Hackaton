"""Stage 2 analysis: honest outages, ticket lead-times, error-code classification.

Run:  python src/twin/deep_analysis.py outages
      python src/twin/deep_analysis.py tickets
      python src/twin/deep_analysis.py errors
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("data/raw/EP-Challenge-Final -/Plant A (start here)")
OUT = Path("runs/plant_a")
STEP_H = 5 / 60


def _load_pac():
    from run_plant_a import load
    return load()


def stage_outages():
    """Honest outage hours: NaN = data gap (not outage); mask pre-commissioning."""
    pac, irrad, dv, evu = _load_pac()
    curtailed = pd.Series(False, index=pac.index)
    for sig in (dv, evu):
        if sig is not None:
            curtailed |= sig.fillna(100) < 99

    sun = irrad > 100
    peers_on = pac.median(axis=1) > 1.0
    valid_t = sun & peers_on & ~curtailed

    rows = []
    cutoff_recent = pac.index.max() - pd.Timedelta(days=365)
    for inv in pac.columns:
        s = pac[inv]
        first_prod = s[s > 0.5].index.min()          # commissioning
        live = s.loc[first_prod:]
        v = valid_t.loc[first_prod:] & live.notna()  # data present, conditions valid
        zero = live.le(0.01) & v
        rows.append({
            "inverter": inv,
            "first_production": str(first_prod.date()) if pd.notna(first_prod) else None,
            "outage_h_total": round(float(zero.sum()) * STEP_H, 1),
            "outage_pct_of_valid": round(float(zero.sum() / max(v.sum(), 1)) * 100, 2),
            "outage_h_last365d": round(float(zero.loc[cutoff_recent:].sum()) * STEP_H, 1),
            "datagap_pct": round(float(live.isna().mean()) * 100, 1),
        })
    df = pd.DataFrame(rows).sort_values("outage_h_last365d", ascending=False)
    df.to_csv(OUT / "outage_hours_honest.csv", index=False)
    print(df.head(15).to_string(index=False))


def stage_tickets():
    """For each inverter-specific ticket: when did our daily flag first fire before it?"""
    ratio = pd.read_csv(OUT / "daily_peer_ratio.csv", index_col=0, parse_dates=True)
    tk = pd.ExcelFile(BASE / "2. Additional Data/Tickets.xlsx")
    tickets = pd.concat([tk.parse(s) for s in tk.sheet_names], ignore_index=True)
    tickets["start"] = pd.to_datetime(tickets["startdate"], errors="coerce", utc=True).dt.tz_localize(None)
    inv_tk = tickets[tickets["component"].astype(str).str.startswith("INV")].copy()
    inv_tk["inverter"] = inv_tk["component"].str.extract(r"INV\s*([\d.]+)")[0]

    rows = []
    for _, t in inv_tk.dropna(subset=["start"]).iterrows():
        inv = t["inverter"]
        if inv not in ratio.columns:
            continue
        r = ratio[inv]
        win = r.loc[t["start"] - pd.Timedelta(days=60): t["start"]]
        flagged = win[win < 0.8]
        lead = (t["start"] - flagged.index.min()).days if len(flagged) else None
        rows.append({"inverter": inv, "ticket_date": str(t["start"].date()),
                     "category": t.get("category"),
                     "flag_lead_days": lead,
                     "min_ratio_in_window": round(float(win.min()), 3) if len(win.dropna()) else None})
    df = pd.DataFrame(rows).sort_values("ticket_date")
    df.to_csv(OUT / "ticket_leadtimes.csv", index=False)
    print(df.to_string(index=False))
    got = df.flag_lead_days.notna()
    print(f"\ntickets with our flag firing BEFORE the ticket: {got.sum()}/{len(df)}"
          f" | median lead: {df.flag_lead_days.median()} days")


def stage_errors():
    """Sparse error events from errorcodes.csv + German descriptions; focus 08/09."""
    desc = pd.read_excel(BASE / "3. Errorcodes/errorcodes description (important).xlsx")
    desc.columns = [str(c).strip() for c in desc.columns]
    dec_col = next(c for c in desc.columns if "ez" in c.lower())
    txt_col = desc.columns[-1]
    code_map = dict(zip(desc[dec_col].astype(str).str.strip(),
                        desc[txt_col].astype(str).str.slice(0, 80)))

    events = []
    usecols = None
    for chunk in pd.read_csv(BASE / "3. Errorcodes/errorcodes.csv", sep=";",
                             chunksize=300_000, low_memory=False,
                             usecols=lambda c: c == "timestamp" or c.endswith("/ Error")):
        melted = chunk.melt(id_vars="timestamp", var_name="col", value_name="code").dropna(subset=["code"])
        melted = melted[melted["code"].astype(str).str.strip().ne("")]
        if len(melted):
            events.append(melted)
    ev = pd.concat(events, ignore_index=True)
    ev["inverter"] = ev["col"].str.extract(r"INV\s*([\d.]+)")[0]
    ev["ts"] = pd.to_datetime(ev["timestamp"], format="%Y.%m.%d %H:%M")
    ev["code"] = ev["code"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    ev["meaning"] = ev["code"].map(code_map).fillna("unknown code")
    ev[["ts", "inverter", "code", "meaning"]].to_csv(OUT / "error_events.csv", index=False)
    print(f"error events total: {len(ev):,}")

    print("\n== top error codes overall ==")
    print(ev.groupby(["code", "meaning"]).size().sort_values(ascending=False).head(10).to_string())

    sec89 = ev[(ev["inverter"].str.startswith(("01.08", "01.09"))) & (ev["ts"] >= "2025-08-01")]
    print(f"\n== sections 08/09 since 2025-08: {len(sec89):,} events ==")
    print(sec89.groupby(["code", "meaning"]).size().sort_values(ascending=False).head(10).to_string())
    print("\nby inverter:")
    print(sec89.groupby("inverter").size().sort_values(ascending=False).head(12).to_string())


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    {"outages": stage_outages, "tickets": stage_tickets, "errors": stage_errors}[sys.argv[1]]()
