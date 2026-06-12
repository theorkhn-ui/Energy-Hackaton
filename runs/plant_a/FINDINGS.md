# Plant A — first findings (2026-06-12, Orkhan's Claude)

Data: 990k rows, 5-min, 2016-12-31 → 2026-06-01, 65 inverters. kWp matched for all 65 from System_Overview. Curtailment (DV/EVU < 99%): only 0.27% of steps — handled, excluded from all outage logic.

## Headline findings (draft — verify before video)

1. **ACTIVE section failure: 01.08.x + 01.09.x degrading since ~Aug 2025** (see heatmap bottom-right). Several inverters now at 0.35-0.50 peer ratio (01.08.057: 0.35, 01.09.065: 0.38, 01.08.058: 0.46, 01.09.062: 0.50). This is happening NOW — highest-value finding for Enerparc.
2. **Unreported fault: INV 01.03.018** — 0.70 peer ratio, 272 of 317 days below 0.95, ≈ €432/yr lost, and **no service ticket exists** → their monitoring missed it, ours didn't.
3. **Ticket cross-validation works**: our top outage inverters 01.08.058 (4 tickets) and 01.09.062 (3 tickets) are exactly the most-ticketed inverters. Our flags reproduce their known problems + find unknown ones.
4. **Historic event**: ~2-3 month outage of sections 01.03-01.05 mid-2019 (visible as red block in heatmap).
5. **Calibration caveat**: ~8 inverters sit permanently at ratio >1.1 (01.04.026/27, 01.05.030/31, 01.07.048-051...) — likely kWp mismatch in System_Overview vs reality (repowering?). Mention honestly; maybe its own finding ("your asset register is stale").

## Money table (last 365 d, chronic underperformers only)
See `underperformers.csv`. Top: 01.03.018 €432 · 01.03.020 €320 · 01.04.025 €259 · 01.03.017 €190 · 01.09.063 €164. NOTE: these are *chronic-drag* losses only; the active 08/09 section failure and outage hours are additional and larger.

## Files
- `heatmap_monthly_ratio.png` — inverter × month peer ratio (the money shot for the video)
- `underperformers.csv`, `outage_hours.csv`, `drift_365d.csv`, `daily_peer_ratio.csv`, `tickets_parsed.csv`

## Known TODO / honesty list
- Outage hours currently count NaN as outage and include pre-commissioning periods → numbers overstated; recompute with first-production masking (in progress)
- Ticket time-window overlap analysis (flag date vs ticket startdate) not yet automated
- Error codes (3. Errorcodes) not yet integrated → fault classification pending
- Winter months have noisy ratios (low irradiation) → consider masking Dec/Jan or weighting by irradiation
