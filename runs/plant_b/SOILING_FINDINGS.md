# Plant B — Soiling Findings

**Data**: 5-min monitoring 2018-01 .. 2026-06, 107 inverters (55–74 kWp each, 7.87 MWp total),
on-site pyranometer `Plant / Irradiation_average` present. Timestamps are **UTC** (verified against
the recorded sun-altitude column). Location 53.269N 12.121E (Silmersdorf, DE) from Coordinate.txt.

## Method
- Clear-sky candidates: pvlib Ineichen GHI > 200 W/m², measured/modelled ratio 0.85–1.15,
  grid curtailment (EVU < 99 %) removed, inverter clipping (>97 % of P99.9) and outages excluded.
- Performance index PI = P_AC / (kWp x G_meas/1000) per inverter, daily median (>=1 h of samples).
- Peer ratio = inverter PI / plant-median PI -> cancels weather, season and sensor drift.
- Sawtooth heuristic on 14-day rolling mean: decline >3 % over >=14 d, recovery >2 % within 7 d.

## Findings
- **Per-inverter soiling sawtooth**: 37 of 107 inverters show at least one
  decline-and-recovery episode. Best example: **INV 05.08.106** with
  21 episodes (max decline 16.46 %):
  2018-06-15->2018-09-05 -5.71%/+7.42%; 2019-04-09->2019-04-27 -11.73%/+9.17%; 2019-06-30->2019-09-06 -7.47%/+3.66%; 2019-06-30->2019-09-22 -3.51%/+4.05%; 2020-06-06->2020-07-26 -4.17%/+3.52%; 2020-06-06->2020-08-30 -5.58%/+4.06%; 2021-04-19->2021-05-10 -4.73%/+5.06%; 2021-07-30->2021-08-19 -5.46%/+6.11%; 2022-05-26->2022-07-13 -4.07%/+3.88%; 2022-07-19->2022-08-25 -10.76%/+8.91%; 2022-09-06->2022-09-29 -4.04%/+5.71%; 2023-04-13->2023-05-16 -3.16%/+3.76%; 2023-06-02->2023-08-30 -10.57%/+7.17%; 2024-03-31->2024-05-05 -9.93%/+4.7%; 2024-03-31->2024-05-31 -5.3%/+4.77%; 2024-06-05->2024-09-02 -14.37%/+3.64%; 2024-07-24->2024-09-16 -16.46%/+2.05%; 2025-05-01->2025-05-16 -5.13%/+6.28%; 2025-07-22->2025-09-05 -14.47%/+10.39%; 2026-04-04->2026-05-08 -14.69%/+8.43%; 2026-04-04->2026-05-26 -5.38%/+4.33%
- **Relative drift** (peer ratio trend): median +0.002 %/month across inverters.
  Fastest-degrading vs peers: INV 02.01.029 (-0.12 %/mo), INV 02.08.043 (-0.06 %/mo), INV 04.01.074 (-0.06 %/mo), INV 02.08.042 (-0.05 %/mo), INV 02.07.040 (-0.05 %/mo).
- **Plant-wide pattern**: plant PI vs the (sensor-independent) clear-sky model shows
  21 de-seasonalized decline/recovery episodes: 2018-04-07->2018-05-14 -8.65%; 2018-04-07->2018-05-28 -3.5%; 2018-04-11->2018-07-10 -8.97%; 2018-06-02->2018-07-24 -3.14%; 2018-08-08->2018-09-05 -5.91%; 2019-02-26->2019-04-08 -7.76%; 2019-07-14->2019-09-05 -4.89%; 2019-09-15->2019-10-05 -3.02%; 2020-04-24->2020-05-21 -12.03%; 2020-08-26->2020-09-27 -4.73%; 2021-07-02->2021-09-30 -6.54%; 2023-03-09->2023-04-11 -7.05%; 2023-06-16->2023-09-03 -6.64%; 2024-03-16->2024-05-06 -11.69%; 2024-03-16->2024-05-20 -5.32%; 2024-06-08->2024-09-06 -3.28%; 2025-04-29->2025-07-06 -9.57%; 2025-04-29->2025-07-20 -4.35%; 2025-09-05->2025-10-01 -10.54%; 2025-09-05->2025-10-28 -5.21%; 2026-03-25->2026-04-30 -5.17%.
- **Winter shading fingerprint**: peer ratios fan out strongly in Nov–Feb. Edge inverters
  outperform the plant median by up to 25 % in winter
  (INV 03.03.048 +25%, INV 01.13.025 +25%, INV 03.14.070 +25%, INV 01.08.015 +25%, INV 05.01.092 +24%) — i.e. the *typical*
  row loses that much to low-sun inter-row shading. December has no clear-sky qualifying days at 53 N.
- **Interpretation of the headline case**: INV 05.08.106/107 are the last row (C.003, west edge).
  Their decline starts each spring, deepens through July/August and snaps back every September —
  consistent with seasonal vegetation growth shading (or edge-of-field soiling) cleared in early
  autumn, repeating every year of the 8.5-year record. This is the clearest sawtooth in the plant.
- **Pyranometer health**: measured/model clear-sky ratio drifted from
  0.993 (2018) to 1.025 (2026)
  — keep in mind when reading absolute PI levels (peer ratios are immune to this).

See `soiling_per_inverter.csv` for all inverters and `soiling_chart.png` for the headline chart.
