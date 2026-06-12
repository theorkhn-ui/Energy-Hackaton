"""Price the 08/09 active collapse + flag-precision analysis.

Run: PYTHONPATH=src/twin .venv/bin/python src/twin/collapse_cost.py
"""
from pathlib import Path

import pandas as pd

BASE = Path("data/raw/EP-Challenge-Final -/Plant A (start here)")
OUT = Path("runs/plant_a")
STEP_H = 5 / 60

COLLAPSE_START = "2025-08-01"


def main():
    from run_plant_a import load, load_kwp
    pac, irrad, dv, evu = load()
    kwp, _ = load_kwp(list(pac.columns))

    day_e = pac.resample("D").sum() * STEP_H
    ratio = pd.read_csv(OUT / "daily_peer_ratio.csv", index_col=0, parse_dates=True)

    # tariffs (recent mean per inverter, ct/kWh)
    tar = pd.read_excel(BASE / "2. Additional Data/feed-in-tarrifs.xlsx", header=None)
    tar_inv = tar.iloc[1:, 0].astype(str).str.extract(r"INV\s*([\d.]+)")[0]
    mean_tariff = pd.Series(
        tar.iloc[1:, -100:].apply(pd.to_numeric, errors="coerce").mean(axis=1).values,
        index=tar_inv.values).dropna()

    # ---- collapse cost since Aug 2025 ----
    r = ratio.loc[COLLAPSE_START:]
    e = day_e.loc[r.index.min():r.index.max()]
    sec = [c for c in ratio.columns if c.startswith(("01.08", "01.09"))]
    rows = []
    for inv in sec:
        rr = r[inv].clip(lower=0.05)
        lost = ((e[inv] / rr) - e[inv]).clip(lower=0)
        # only count days actually below 0.95 (be conservative)
        lost = lost[r[inv] < 0.95]
        kwh = float(lost.sum())
        eur = kwh * float(mean_tariff.get(inv, mean_tariff.mean())) / 100
        rows.append({"inverter": inv, "lost_kwh_since_aug25": round(kwh),
                     "lost_eur_since_aug25": round(eur),
                     "mean_ratio_since_aug25": round(float(r[inv].mean()), 3)})
    df = pd.DataFrame(rows).sort_values("lost_eur_since_aug25", ascending=False)
    df.to_csv(OUT / "collapse_cost.csv", index=False)
    months = (r.index.max() - r.index.min()).days / 30.4
    tot = df.lost_eur_since_aug25.sum()
    print(f"== 08/09 collapse cost since {COLLAPSE_START} ({months:.1f} months) ==")
    print(df.head(12).to_string(index=False))
    print(f"\nTOTAL: €{tot:,.0f} over {months:.1f} months -> annualized ≈ €{tot/months*12:,.0f}/yr")

    # ---- flag precision: episodes vs tickets ----
    tk = pd.read_csv(OUT / "ticket_leadtimes.csv")
    tk["ticket_date"] = pd.to_datetime(tk["ticket_date"])
    monthly = ratio.resample("ME").mean()
    episodes = []
    for inv in monthly.columns:
        bad = monthly[inv] < 0.8
        # group consecutive bad months into episodes
        grp = (bad != bad.shift()).cumsum()
        for _, g in monthly[inv][bad].groupby(grp[bad]):
            episodes.append({"inverter": inv, "start": g.index.min(), "end": g.index.max()})
    ep = pd.DataFrame(episodes)
    if len(ep):
        def matched(row):
            t = tk[tk.inverter == row.inverter]
            if not len(t):
                return False
            near = t[(t.ticket_date >= row.start - pd.Timedelta(days=30)) &
                     (t.ticket_date <= row.end + pd.Timedelta(days=90))]
            return len(near) > 0
        ep["ticket_matched"] = ep.apply(matched, axis=1)
        ep.to_csv(OUT / "flag_episodes.csv", index=False)
        n, m = len(ep), int(ep.ticket_matched.sum())
        print(f"\n== flag precision ==")
        print(f"flag episodes (monthly ratio<0.8): {n} | matched to a ticket: {m} "
              f"({m/n*100:.0f}%) | candidate unreported: {n-m}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src/twin")
    main()
