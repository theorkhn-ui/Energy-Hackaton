"""Forward-looking maintenance watchlist: 'inspect these on Monday'.

Run: PYTHONPATH=src/twin .venv/bin/python src/twin/watchlist.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("runs/plant_a")
TARIFF = 0.115  # EUR/kWh fallback


def main():
    ratio = (pd.read_csv(OUT / "daily_peer_ratio.csv", index_col=0, parse_dates=True)
             .replace([np.inf, -np.inf], np.nan))
    tk = pd.read_csv(OUT / "ticket_leadtimes.csv")
    under = pd.read_csv(OUT / "underperformers.csv", index_col=0)

    end = ratio.index.max()
    last60 = ratio.loc[end - pd.Timedelta(days=60):]
    prev60 = ratio.loc[end - pd.Timedelta(days=120):end - pd.Timedelta(days=61)]

    recent_ticket = set(tk[pd.to_datetime(tk.ticket_date) > end - pd.Timedelta(days=120)].inverter)

    rows = []
    for inv in ratio.columns:
        cur, prev = last60[inv].mean(), prev60[inv].mean()
        if pd.isna(cur) or cur >= 0.93:
            continue
        eur = float(under["lost_eur_365d"].get(inv, np.nan))
        sev = ("CRITICAL" if cur < 0.5 else "MAJOR" if cur < 0.8 else "MINOR")
        trend = "worsening" if (pd.notna(prev) and cur < prev - 0.02) else \
                "improving" if (pd.notna(prev) and cur > prev + 0.02) else "stable"
        rows.append({
            "inverter": inv,
            "ratio_last60d": round(float(cur), 2),
            "trend": trend,
            "severity": sev,
            "est_eur_per_yr": None if pd.isna(eur) else round(eur),
            "ticket_last_120d": inv in recent_ticket,
            "action": ("site inspection / replacement assessment" if cur < 0.5 else
                       "diagnostic check (DC strings, fuses)" if cur < 0.8 else
                       "monitor; clean/inspect if persists"),
        })
    wl = (pd.DataFrame(rows)
          .sort_values(["severity", "ratio_last60d"]) )
    wl.to_csv(OUT / "watchlist.csv", index=False)

    md = ["# Maintenance Watchlist (generated " + str(end.date()) + ")",
          "",
          f"Inverters currently below 0.93 peer ratio (60-day mean). "
          f"{len(wl)} flagged; {int((~wl.ticket_last_120d).sum())} have NO ticket in the last 120 days.",
          "",
          wl.to_markdown(index=False)]
    (OUT / "WATCHLIST.md").write_text("\n".join(md))
    print(wl.to_string(index=False))
    print(f"\n-> {OUT/'WATCHLIST.md'}")


if __name__ == "__main__":
    main()
