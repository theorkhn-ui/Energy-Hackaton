# Plant Sentinel: a digital twin that pays for itself

**Team Syz · Energy Hack Munich 2026 · Challenge #2.1, Enerparc: Digital Twin of a Solar Plant**

## Problem

Plant A's error-code telemetry stopped in Nov 2019 and never covered sections 08/09.
Result: only 33 of 477 material underperformance episodes (7%) over 9.4 years ever got an
inverter-specific service ticket, and a section-level failure is unfolding right now without
an alarm. The data to catch all of it was already being recorded, every 5 minutes.

## Method

- **Peer ratio:** each inverter's kWp-normalized output ÷ plant median at the same timestamp.
  Weather, season, and rain cancel out; 1.0 = healthy, below = trouble.
- **Curtailment-aware:** EVU/DV grid-curtailment intervals are filtered explicitly, so
  curtailment is never mistaken for a fault.
- **Ticket-validated:** every flag back-tested against the real service log. 42 of 46
  inverter tickets were preceded by our flag, median lead 51.5 days.

## Findings (Plant A unless noted)

| # | Finding | Numbers | € impact |
|---|---|---|---|
| 1 | Failures predictable before ticketing | 42/46 tickets flagged early, median 51.5 d | 7 weeks to plan repairs instead of reacting |
| 2 | ACTIVE collapse, sections 01.08+01.09 (since Aug 2025) | inverters at 0.35 to 0.50 of peers; 740 to 840 outage h/365d each | ~€1,200/yr realized; **€42,325/yr at risk** (368 kWp) |
| 3 | Unreported fault INV 01.03.018 | ratio 0.70 for 12 months, 0 tickets | ≈ €432/yr |
| 4 | Unticketed underperformance, plant-wide | 444 episodes / 9.4 yrs, no ticket | **€64,247 cumulative** |
| 5 | Alarm triage: 9,211 events into 823 incidents | 25% TRIP / 4% DERATE / 71% NUISANCE; ENS costliest | 1.4 of 2.6 MWh lost energy from one code family |
| 6 | Plant B soiling/shading | 37/107 inverters sawtooth; worst case 21 episodes, -16.5%; winter inter-row shading up to -25% | cleaning/vegetation schedule per inverter |
| 7 | Stale asset register | ~8 inverters at ratio >1.1 mean wrong kWp on file | every yield calc on the plant off |

All €: lost energy × feed-in tariff (estimates). Honest limits: tickets are sparse ground
truth, so recall (42/46) is the defensible stat. The relative method's one blind spot,
plant-wide degradation that hits every inverter equally, is now closed by an absolute-baseline
twin (`runs/plant_a/twin/TWIN.md`): R² 0.957 on healthy output, and on a synthetic uniform -10%
the peer metric stays 1.00 (blind) while the twin drops to 0.81 (detected); it also flags a real
~7 to 10% plant-wide gap and runs the 08/09 collapse forward (cost-of-delay).

## What Enerparc should do next Monday

Stale-register audit backup: the quantified pass found 8 clean candidates and gives
implied kWp values in `runs/plant_a/STALE_KWP_AUDIT.md`.

1. **Dispatch to sections 01.08/01.09.** The collapse is active, €42,325/yr at risk;
   restore error telemetry coverage for these sections while the crew is there.
2. **Open a ticket for INV 01.03.018.** One year at 70% output, never reported.
3. **Re-rank the alarm list and audit the kWp register.** Deprioritize the 71% nuisance
   codes (DC-link, insulation), escalate grid-undervoltage trips, and field-verify the
   ~8 suspect kWp entries.

## Team & contact

Orkhan Karimov · Maxat Issaliyev · **theorkhn@gmail.com**
Repo: README and `runs/` contain every chart and CSV behind the numbers above; analysis is
reproducible with `src/twin/run_plant_a.py` and `run_plant_b.py`.
