# Q&A Prep: Tough Questions from Solar Engineers (Jury)

Team Syz · Enerparc digital twin · Plant A (65 inverters, 9.4 yrs of 5-min data) plus Plant B soiling.
Rule of thumb when answering: concede honest limitations fast, then pivot to the validated number.

---

## 1. "If an inverter is always bad, flag-before-ticket is trivial. What's your false-positive rate?"

We deliberately report recall against your ticket log (**42 of 46 inverter tickets were preceded by our flag, median lead 51.5 days**) because that is the stat we can ground-truth. Classic precision is unmeasurable here: our flags fire roughly 10× more often than tickets exist, but that is because tickets are sparse, not because the flags are wrong. We found 477 material problem-episodes and only 33 (7%) were ever ticketed. The unticketed episodes are not noise: they sum to €64k of measurable lost energy, including a chronic 0.70-ratio inverter (01.03.018) with zero tickets in nine years. That gap between what the plant loses and what reaches the ticket system is the product, not a bug in the validation.

## 2. "Peer normalization can't detect plant-wide degradation. Every inverter could be dirty or degrading together."

Correct, and we say so explicitly: a peer-relative index is blind to common-mode effects like uniform soiling, module degradation, or plant-wide derating. That is a deliberate trade-off: peer normalization needs no irradiance model and isolates single-unit faults cleanly, which is where the actionable tickets are. The complement is an absolute, irradiation-based performance index: Plant B has a pyranometer we already validated against pvlib clear-sky modeling (**+3% drift over 8.5 years**), so the absolute-PR layer is a straightforward addition on the same pipeline. In production we would run both: peer index for unit-level triage, irradiance-referenced PR for fleet-level health.

## 3. "Your € numbers: what tariff assumptions are you making?"

No assumed tariff at all. We computed per-inverter feed-in revenue rates directly from **your own weekly feed-in tariff data**, using recent-period means per inverter. So the €64k historic figure and the €42k/yr at-risk figure for the 08/09 collapse are priced at what Enerparc actually receives, not at a generic German EEG or spot assumption. Where we extrapolate forward (the at-risk number), we say "revenue at risk", not realized loss. Realized loss on the collapse so far is only ~€1.2k/yr and we keep those two numbers strictly separate. The one number to defend: **€42,325/yr of revenue at risk** on sections 08/09.

## 4. "How do you handle curtailment? Grid-operator setpoints would look exactly like underperformance."

We check the EVU/DV curtailment signals in the SCADA data and exclude every timestep where the setpoint is below 99% from all outage and underperformance logic. In Plant A that was only **0.27% of all 5-min steps**, so curtailment cannot explain the findings, but the exclusion is unconditional, so a heavily curtailed plant would not produce false flags either. Also note that curtailment is plant-wide while our index is peer-relative, so even an unflagged curtailment event would mostly cancel out in the ratio. Both layers of protection are in the code, not a manual cleaning step.

## 5. "Why didn't the inverter error codes explain the 08/09 section collapse?"

Because they can't: **error-code telemetry for Plant A ends in November 2019** (9,211 real error events from 2017 to 2019, then zero for six and a half years) and the error stream never covered sections 08 and 09 at all. That is itself one of our findings: the active collapse (inverters at 0.35 to 0.50 peer ratio, ~840 outage hours/yr on the worst unit) is structurally invisible to the existing alarm system, and only production-data analysis catches it. We'd flag the dead telemetry feed as an O&M action item in its own right. If the jury knows why the feed died, we genuinely want to hear it; that's a conversation, not a gotcha.

## 6. "Your stale-kWp claim: couldn't your System_Overview parsing simply be wrong?"

Honestly: possible, and we'd want a joint audit of the asset register against as-built documentation before anyone acts on it. But the pattern argues for a register issue, not a parser bug: **exactly 8 inverters** (e.g. 01.04.026/027, 01.05.030/031, 01.07.048-051) sit at peer ratios above 1.1 sustained for years, in contiguous groups, while the other 57 parse to physically sensible ratios. A parsing error would scatter, not cluster. The likely cause is repowering or string reconfiguration that never made it back into System_Overview. Either way the conclusion stands: the digital record disagrees with physical reality for those units, and that corrupts any kWp-normalized KPI Enerparc runs, not just ours.

## 7. "Winter performance ratios are notoriously noisy at low irradiation. How much of your flagging is winter noise?"

Stale-register audit backup for Q6: `runs/plant_a/STALE_KWP_AUDIT.md` lists 8 clean
register candidates (`01.05.030`, `01.07.049`, `01.07.051`, `01.04.026`,
`01.07.048`, `01.07.050`, `01.06.040`, `01.04.027`) with registered kWp, median
peer ratio, implied kWp, and gap. It separates 2 high-ratio units in 01.08/01.09 as
operationally confounded, so we are not mixing the active-collapse section into the
clean master-data claim.

We handle it in two passes. First, low-irradiation days are down-weighted via minimum-energy thresholds: a day has to produce enough fleet energy for the peer ratio to be statistically meaningful before it can contribute to a flag. Second, the money and validation numbers only count *material episodes*: sustained, multi-day deviations with quantifiable energy loss, not single noisy days. The headline findings survive this filter: the 08/09 collapse spans **August 2025 to now** across all seasons, and 01.03.018 was below 0.95 on 272 of 317 evaluated days. Irradiation-weighted ratios are on our roadmap as a further refinement and we list that openly in FINDINGS.md.

## 8. "Nice hackathon analysis, but would this actually scale and run live?"

Yes, because it is deliberately boring technology: pure pandas on resampled SCADA exports, no GPU, no model training, no external services. The full 9.4-year, 990k-row, 65-inverter backfill runs in minutes on a laptop; incremental daily operation is a batch job at well **under 1 minute per plant per day**, so a fleet of hundreds of plants fits on one small VM. The peer method needs no irradiance sensors or digital-twin physics model per site, only what every Enerparc plant already logs. The hard part of productionizing is data plumbing (which we've already proven against your real exports, tickets and tariffs), not compute.

## 9. "Soiling versus vegetation shading versus inter-row shading: can your sawtooth detector actually distinguish them?"

Not perfectly, and we won't pretend otherwise: from production data alone these are partially degenerate. Our heuristics use shape and calendar: classic soiling shows a gradual sawtooth with recovery aligned to rain or cleaning events; the recurring Plant B case (**INV 05.08.106/107, 3 to 16% loss building spring to August with a September snap-back every single year**) recovers on a fixed seasonal date, which points to vegetation growth or edge shading rather than dust; winter inter-row shading shows up only Nov to Feb on interior rows at low sun angles. The honest resolution is ground truth: cross-reference our detected episodes against cleaning and mowing logs, which is exactly the validation loop we already ran with service tickets on Plant A. Even unresolved, the €-quantified episode list tells O&M where to look.

## 10. "What is actually novel here versus standard PR monitoring that every O&M provider already runs?"

Three things, all proven on *your* data rather than claimed in the abstract. First, ticket-validated early warning: 42/46 real service tickets preceded by our flag with a **median 51.5-day lead**. We have not seen standard PR dashboards publish a lead-time stat against their own ticket log. Second, a curtailment-aware peer method that needs no irradiance model, which is what let us run 9.4 years across two plants in a weekend. Third, alarm-noise quantification: we classified 823 historic incidents and showed 71% are nuisance alarms, which is a concrete triage recommendation, not a dashboard. The pitch is not "we monitor PR", it's "we measured the gap between what your plant loses and what your processes see, and it's €64k plus €42k/yr."

## 11. "71% nuisance alarms: by whose definition? Maybe those alarms are doing their job."

Fair challenge. We define nuisance operationally, not subjectively: an incident is nuisance if it caused no measurable production deficit in the surrounding window, versus TRIP (production stops) and DERATE (production drops). By that energy-grounded definition, **823 incidents split 25% TRIP / 4% DERATE / 71% nuisance**, with DC-link and insulation alarms almost pure noise while grid-undervoltage (ENS) events were the costliest class (~1.4 MWh). Some no-loss alarms may still be useful leading indicators, and we'd test that by checking whether nuisance classes statistically precede later TRIPs, which the same dataset supports. The recommendation is alarm *triage* and prioritization, not deletion.

## 12. "Sections 08 and 09 are failing right now, what would you actually tell our O&M team to do on Monday?"

Concrete and ranked. (1) Dispatch to sections 01.08/01.09 this month: 14 inverters and 368 kWp are trending toward zero, worst units at 0.35 to 0.50 peer ratio and 700 to 840 outage hours in the last year. That's the **€42k/yr at-risk** item, and the ticket history there (defective capacitors, boards, insulation faults) suggests a common-cause hardware or string-level issue worth a section-wide inspection rather than unit-by-unit fixes. (2) Restore the error-code telemetry feed dead since Nov 2019 and extend coverage to 08/09. (3) Audit the 8 stale-kWp register entries. (4) Inspect chronic quiet losers led by 01.03.018 (€432/yr, never ticketed). Items 2 to 4 cost almost nothing and permanently raise what your monitoring can see.

## 13. "Why peer median instead of a trained ML model? This is 2026."

Because 65 inverters under identical sky are a better reference model than anything we could train in a weekend: the fleet *is* the physics model, updated every 5 minutes for free. A peer-normalized index is interpretable to a technician ("this unit makes 70% of its neighbors"), needs no labeled training data, no retraining as the plant ages, and degrades gracefully when sensors fail, which matters at a plant whose error telemetry has been dead since 2019. We did use modeling where it adds value: pvlib clear-sky simulation to validate the Plant B pyranometer. ML earns its place later, on top of this baseline (for example learning which flag patterns precede which ticket causes), and our 9.4-year flag-vs-ticket dataset is exactly the labeled corpus you'd train it on.

---

## Numbers cheat-sheet (memorize these)

| Stat | Value |
|---|---|
| Ticket validation | 42/46 flagged before ticket, median lead 51.5 days |
| Active 08/09 collapse | €42,325/yr revenue at risk (14 inverters, 368 kWp) |
| Unticketed underperformance | €64,247 over 9.4 yrs (444 episodes; only 7% of episodes ever ticketed) |
| Curtailment excluded | 0.27% of 5-min steps (EVU/DV < 99%) |
| Telemetry blind spot | error codes dead since Nov 2019; never covered sections 08/09 |
| Fault classification | 823 incidents: 25% TRIP / 4% DERATE / 71% nuisance |
| Plant B soiling | 37/107 inverters; 05.08.106/107 lose 3 to 16% with annual Sept snap-back |
| Stale register | 8 clean candidates at ratio >1.1 sustained for years; see STALE_KWP_AUDIT |
| Runtime | < 1 min per plant per day, pure pandas |


## 14. "What about the 4 tickets you missed?"

All four are partial failures: three single-string outages (Strangausfall) and one early-stage capacitor case, with peer ratios of 0.81-0.94 in the window, losses of 6-19%, below our 0.8 inverter-level flag threshold. They are exactly the cases that string-level detection catches: the dataset contains per-inverter I_DC_SUM, so extending the same peer method to string currents is the natural next step and is on our roadmap. **The misses define the product roadmap, not a method failure.**
