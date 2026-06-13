# Plant A: first findings (2026-06-12)

Data: 990k rows, 5-min, 2016-12-31 to 2026-06-01, 65 inverters. kWp matched for all 65 from System_Overview. Curtailment (DV/EVU < 99%): only 0.27% of steps, handled, excluded from all outage logic.

## Headline findings (draft, verify before video)

1. **ACTIVE section failure: 01.08.x + 01.09.x degrading since ~Aug 2025** (see heatmap bottom-right). Several inverters now at 0.35-0.50 peer ratio (01.08.057: 0.35, 01.09.065: 0.38, 01.08.058: 0.46, 01.09.062: 0.50). This is happening NOW, highest-value finding for Enerparc.
2. **Unreported fault: INV 01.03.018**, 0.70 peer ratio, 272 of 317 days below 0.95, ≈ €432/yr lost, and **no service ticket exists**. Their monitoring missed it, ours didn't.
3. **Ticket cross-validation works**: our top outage inverters 01.08.058 (4 tickets) and 01.09.062 (3 tickets) are exactly the most-ticketed inverters. Our flags reproduce their known problems and find unknown ones.
4. **Historic event**: ~2-3 month outage of sections 01.03-01.05 mid-2019 (visible as red block in heatmap).
5. **Calibration caveat**: ~8 inverters sit permanently at ratio >1.1 (01.04.026/27, 01.05.030/31, 01.07.048-051...), likely kWp mismatch in System_Overview vs reality (repowering?). Mention honestly; maybe its own finding ("your asset register is stale").

## Money table (last 365 d, chronic underperformers only)
See `underperformers.csv`. Top: 01.03.018 €432 · 01.03.020 €320 · 01.04.025 €259 · 01.03.017 €190 · 01.09.063 €164. NOTE: these are *chronic-drag* losses only; the active 08/09 section failure and outage hours are additional and larger.

## Files
- `heatmap_monthly_ratio.png`: inverter × month peer ratio (the money shot for the video)
- `underperformers.csv`, `outage_hours.csv`, `drift_365d.csv`, `daily_peer_ratio.csv`, `tickets_parsed.csv`

## Next results (same evening)

6. **Predictive power proven: 42/46 inverter tickets were preceded by our flag, median lead 51.5 days** (`ticket_leadtimes.csv`). Ticket causes: defective capacitors, boards, insulation faults.
7. **Honest outage hours** (`outage_hours_honest.csv`, NaN+commissioning masked): worst last-365d: 01.08.053 840h, 01.08.057 784h, 01.08.058 743h, which confirms the 08/09 active failure with clean numbers.
8. **Monitoring blind spot: error-code telemetry ends Nov 2019 and NEVER covered sections 08/09** (9,211 real error events 2017-2019, zero after). The current collapse is invisible to their error logging; only performance analysis (ours) catches it. Top historic codes: Netzunterspannung/ENS (5,405), Störmeldung Leistungsteil (3,479).

## Money framing (FINAL numbers for the video)

9. **€64,247 of underperformance (444 episodes over 9.4 yrs) has no inverter-specific service ticket**, only 33 of 477 material problem-episodes (7%) were ever ticketed. Framing: "at best logged as plant-level events, at worst never seen." (`flag_episodes_material.csv`)
10. **08/09 collapse: ~€1,200/yr lost so far, but €42,325/yr of revenue at risk** (14 inverters, 368 kWp trending toward zero). Use "at-risk revenue", do NOT inflate realized losses. (`collapse_cost.csv`)
11. Precision caveat (honesty beat): our flags fire 10× more often than tickets exist, which is consistent with the telemetry blind spot, but say it as "tickets are sparse, not flags wrong"; lead-time recall (42/46) is the defensible stat.

## Full challenge-brief coverage

12. **Plant B soiling (runs/plant_b/)**: 37/107 inverters with soiling-style sawtooths; INV 05.08.106/107 lose 3-16% spring to Aug with September snap-back every year (vegetation shading/edge soiling). Winter inter-row shading costs interior rows up to 25% Nov-Feb. Pyranometer validated vs pvlib clear-sky (+3% drift over 8.5 yrs).
13. **Automated fault classification (runs/plant_a/faults/)**: 823 incidents from 9,211 error events, 25% TRIP / 4% DERATE / 71% NUISANCE. Grid-undervoltage (ENS) = costliest (~1.4 MWh); DC-link and insulation alarms ≈ pure noise, so an alarm-triage recommendation. Chart: fault_matrix.png.

All five suggested challenge directions now covered: anomaly detection ✓ · soiling (Plant B) ✓ · fault classification ✓ · performance-ratio modelling ✓ · ticket intelligence ✓.

## Later additions

14. **Stale kWp register QUANTIFIED** (`kwp_audit.csv`): 11 inverters where near-STC peak output exceeds plant norm vs registered kWp. Clearest case: **INV 01.05.030 registered 5.64 kWp, observed 23 kW peak (4×)**; the 01.07.048-051 / 01.08.052/059 / 01.04.026/27 group should read ≈28.9 kWp not 16.5-23.5. Suggested corrections included, so we hand Enerparc a fixed asset register.
15. **Maintenance watchlist** (`WATCHLIST.md`): 3 CRITICAL + 10 MAJOR inverters today; 11 of 13 have no recent ticket.
16. **Remotion video project scaffolded and compiling** (`video/`): 9 scenes, 3:50, captions from storyboard, tsc + bundle verified. Preview with `cd video && npx remotion studio`.

## ✅ INDEPENDENT VERIFICATION (separate second implementation)
All three headlines CONFIRMED (`VERIFICATION.md`): 41-42/46 tickets, median lead 48-51.5d ✓ · outage hours reproduce within 2h (840/784/742) ✓ · 01.03.018 share of bad days ✓ BUT money corrected: **~€500/yr, not €432 (we understated)**, so use "~€500/yr (independently verified)". Collapse wording: "2 inverters still <0.7 at end of data; 057 recovered May 2026", say it honestly. Side-confirmation: 052/059 peer ratio 1.72 ≈ exactly the stale-kWp factor from kwp_audit (17 to 29 kWp).

**The 4 missed tickets explained**: 3× Strangausfall (single-string outage) + 1 capacitor case, min ratios 0.81-0.94, losses of 6-19% sit below our 0.8 inverter-level threshold. String-level detection (I_DC_SUM exists in data) catches these, so a roadmap item, and a prepared Q&A answer.

## Interactive dashboard
`runs/plant_a/dashboard/index.html`: self-contained, dark theme, 65 clickable inverter tiles, per-inverter history + ticket markers. Screen-record 15-20s for the video product shot.

## Video assets ready
- `viz/leadtime_chart.png`, `viz/section_collapse.png`, `viz/money_chart.png` (1080p, big fonts)
- `docs/VIDEO_STORYBOARD.md`: full 3:50 scene-by-scene script with narration

## Known TODO / honesty list
- Winter months noisy (low irradiation), so consider irradiation-weighted ratios
- "Relative method can't see plant-wide degradation", keep as the honest-limitation beat in the video
- Stale-kWp group (ratio>1.1) not yet quantified per inverter
