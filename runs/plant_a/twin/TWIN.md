# Absolute-baseline digital twin: closing the one honest limitation

Our headline method is the **peer ratio** (each inverter ÷ the plant median at
the same timestamp). It is stable and curtailment-aware, but it is *relative*:
a loss that hits **every** inverter equally cancels out and is invisible. That
is the one limitation we call out honestly in the video.

This module closes it. It builds a per-inverter **absolute** expected-output
model, a living baseline of what each inverter *should* produce from the
physical drivers, so the plant can be compared to itself, not just to its
neighbours. With that, the twin can also run **what-if** scenarios. Together
that is the difference between "analytics on PV data" and a "digital twin".

Code: `src/twin/twin_baseline.py` (model), `twin_validate.py` (validation +
proof), `twin_whatif.py` (scenarios). Run each from the repo root.

---

## The model

For each inverter *i*, calibrated on its **first ~365 production days** (its
healthy youth):

```
P_exp[i,t] = k_i · G_t · (1 + γ · (T_mod_t - 25))
```

- `G_t` = plane irradiance (W/m²), `T_mod` = module temperature (°C), 25 °C ref.
- `γ` = module power temperature coefficient, **fit globally** from healthy data
  (we get -0.0025/°C; the module-temp sensor reads warmer than the cell, so the
  effective coefficient is smaller than the -0.004 cell-level literature value).
- `k_i` = the inverter's temperature-corrected healthy response, fit
  **energy-weighted** so the index reads exactly 1.0 on its own baseline.

It is deliberately **kWp-free** and **self-referential**: each inverter is
judged against its own healthy history, never against the register. So it is
immune to the stale-kWp problem we found separately, and a uniform plant-wide
loss cannot hide in it.

**Health index** (daily): `HI[i,d] = Σ P_actual / Σ P_exp` over strong-sun
(`G > 300 W/m²`), non-curtailed steps. `HI = 1.0` means behaving like its healthy
self; below 1.0 is absolute loss.

---

## Validation

| Check | Result |
|---|---|
| Healthy daily-energy accuracy (R²) | **0.957** (n = 16,472 inverter-days) |
| Out-of-sample healthy control, MAPE | **7.2%** |
| Baseline self-check (must be ~1.0 by construction) | **1.015**, IQR [1.00, 1.03] |
| Independently re-finds 01.08.053 (active collapse) | HI **0.34** |
| Independently re-finds 01.08.058 (active collapse) | HI **0.48** |
| Independently re-finds 01.03.018 (unreported fault) | HI **0.88** |
| 01.08.057 (verification said "recovered May 2026") | last-90d HI **~1.0** ✓ |

The twin re-derives every known fault from physical first principles, without
ever looking at the peer-ratio output or the ticket log.

---

## The proof: `twin_uniform_loss.png`

Inject a **synthetic uniform -10%** on *every* inverter for the last 365 days
(a plant-wide soiling / degradation / sensor-drift event) and recompute both
metrics over that window:

| Metric | Healthy | After uniform -10% | Verdict |
|---|---|---|---|
| Relative peer metric (inverter ÷ plant median) | 1.00 | **1.00** | **blind** |
| Absolute twin index (vs own baseline) | 0.90 | **0.81** | **detected (-10%)** |

The relative metric is mathematically invariant to a common-mode loss; the
absolute twin drops by the full 10%. This is exactly the failure mode the
video's honest-limitation beat describes, now demonstrated and closed.

### Bonus finding it surfaces

Without any injection, the twin already shows a **real plant-wide gap of
~7 to 10%** versus the commissioned baseline (`twin_health_timeline.png`). Part is
genuine module degradation/soiling; part may be the **+3% pyranometer drift**
we measured separately. Either way it is revenue the relative method
structurally cannot see, and a concrete recommendation: **field-check module
soiling and recalibrate the irradiance sensor.** (Stated as a hypothesis to
verify, not a hard number, see limits below.)

---

## What-if: `twin_whatif_collapse.png`

Because the twin is a model, we can run the active 01.08/01.09 collapse forward:

- **Tier 1, bleeding now:** the currently-degraded units (01.08.053 at HI 0.52,
  01.08.058 at 0.76) are losing **~€1,550/yr** at today's run-rate.
- **Tier 2, section ceiling:** if the whole 14-inverter 08/09 section completes
  its collapse to zero, **~€29,000/yr** of revenue is at risk (twin-derived,
  full-daylight; consistent with the €42k upper bound from `collapse_cost.py`).
- **Cost of delay:** every 90 days of waiting ≈ **€380** of avoidable loss on the
  units already degraded, the number behind "fix it on your terms".

This is the conservative, twin-grounded version of the at-risk figure: it
separates what is *bleeding today* from the *tail risk*, instead of quoting the
ceiling as a realized loss.

---

## Honest limits of the twin (kept, on purpose)

- **Winter noise.** Few strong-sun steps in deep winter make HI noisier
  Nov to Feb; we smooth with a 75-day median for the timeline.
- **Sensor drift vs real loss.** The twin cannot, by itself, separate a real
  plant-wide generation loss from irradiance-sensor drift; both look like a
  common-mode HI drop. That is *why* the recommendation is a field check, not a
  euro claim.
- **€ are strong-sun-based, grossed up.** Energy is summed over `G > 300` and
  grossed to full daylight by the irradiation ratio (×1.24); it is an estimate,
  not metered settlement.
- **Still single-plant, historical replay.** This is the absolute-baseline core
  of a twin and a what-if engine, not yet a live-streaming deployment. Wiring it
  to live telemetry is the funded next step.

---

## Reproduce

```bash
python src/twin/twin_baseline.py     # fit + daily health index
python src/twin/twin_validate.py     # accuracy, reproduce, uniform-loss proof
python src/twin/twin_whatif.py       # 08/09 forward projection + cost of delay
```

Outputs (this folder): `twin_health_index.csv`, `twin_calibration.csv`,
`twin_reproduce.csv`, `twin_uniform_loss.{csv,png}`, `twin_health_timeline.png`,
`twin_collapse_cohort.csv`, `twin_cost_of_delay.csv`, `twin_whatif_collapse.png`.
