# Fault classification: Plant A

Source: 9211 raw error events (2017-01 .. 2019-11), merged into **823 incidents** (same inverter + code, gaps <= 2 h).

Classification = mean 5-min P_AC during incident vs the inverter's own median power at the same time-of-day over +/-14 days (daylight only): **TRIP** < 30% of normal, **DERATE** 30-90%, **NUISANCE** > 90% (incl. incidents fully outside daylight hours, which by definition cost no energy).

## Code family x classification

| Code family | TRIP | DERATE | NUISANCE | Total | Mean duration (h) | Est. lost energy (MWh) |
|---|---|---|---|---|---|---|
| Grid-side (undervoltage / ENS) | 106 | 0 | 15 | 121 | 3.86 | 1.35 |
| Power-stage fault | 70 | 5 | 411 | 486 | 0.66 | 1.21 |
| DC-link | 27 | 32 | 145 | 204 | 0.34 | 0.04 |
| Insulation | 0 | 0 | 11 | 11 | 0.08 | 0.00 |
| Other | 1 | 0 | 0 | 1 | 0.08 | 0.00 |
| **All** | **204** | **37** | **582** | **823** | **1.04** | **2.60** |

## Per-code breakdown

| Code | Meaning (EN) | Family | Incidents | TRIP | DERATE | NUISANCE | Lost MWh |
|---|---|---|---|---|---|---|---|
| 655616 | power-stage fault | power-stage | 486 | 70 | 5 | 411 | 1.21 |
| 655626 | grid undervoltage (ENS) | grid-side | 118 | 105 | 0 | 13 | 1.35 |
| 655363 | DC-link asymmetry low | dc-link | 107 | 10 | 5 | 92 | 0.03 |
| 655366 | DC-link (pos.) below nominal | dc-link | 33 | 10 | 11 | 12 | 0.01 |
| 655365 | DC-link (pos.) below nominal | dc-link | 28 | 3 | 14 | 11 | 0.00 |
| 655372 | DC-link (neg. boosted) exceeded | dc-link | 23 | 2 | 2 | 19 | 0.00 |
| 655379 | insulation test failure | insulation | 11 | 0 | 0 | 11 | 0.00 |
| 655371 | DC-link (pos. boosted) exceeded | dc-link | 7 | 1 | 0 | 6 | 0.00 |
| 655369 | DC-link (neg.) below nominal | dc-link | 6 | 1 | 0 | 5 | 0.00 |
| 655385 | grid voltage too low too long | grid-side | 2 | 0 | 0 | 2 | 0.00 |
| 655373 | grid overvoltage (ENS) | grid-side | 1 | 1 | 0 | 0 | 0.00 |
| 663565 | device over-temperature | other | 1 | 1 | 0 | 0 | 0.00 |

## Takeaway

Grid-side (undervoltage / ENS) incidents are the real energy killers: they account for 1.4 MWh of the 2.6 MWh total estimated loss, with 88% of them being full trips. By contrast, 71% of all incidents are NUISANCE events that show no measurable power impact and can be deprioritised in O&M alarm handling. Cross-referencing error codes with power drops thus turns ~9,200 raw alarms into a short, ranked work list of incidents that actually cost energy.
