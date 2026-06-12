# Clean-room verification — Plant A headline statistics

Independent recomputation from raw data only (`data/raw/EP-Challenge-Final -/Plant A (start here)/`).
No team analysis code (`src/twin/*.py`) or team output files were read.
Script: `runs/plant_a/verify_clean.py` (run from repo root with `.venv/bin/python`;
caches: `verify_cache.parquet`, `verify_cache_outage.parquet`). Date of check: 2026-06-13.

**Method (mine, chosen independently).** Daily energy per inverter = sum(P_AC) x 5/60 from the
5-min parquet (65 `INV xx.xx.xxx / P_AC (kW)` columns). Daily plant irradiation energy from
`Plant / Irradiation_average (W/m²)` x 5/60 / 1000. kWp per inverter from System_Overview
(header=2, `PDC (kWp)`; sub-entries like "WR 01 .01. 004.02" added to their parent inverter).
PI = daily_kWh / (kWp x irr_kWh); peer ratio = PI / cross-inverter median PI that day (>=30
inverters reporting required). Two filter variants:
**primary** = days with irr >= 0.2 kWh/m², zero-production sunny days count as ratio 0;
**alt (conservative)** = irr >= 1.0 kWh/m², zero-production days treated as unobserved.
Inverter tickets: all 46 dated `INV xx.xx.xxx` rows are in the '2020-2026' sheet (47 rows,
1 without startdate dropped); the '2019-2020' sheet has no inverter-specific IDs, so no
cross-sheet dedupe was needed.

## Results

| # | Claim | My result (primary) | My result (conservative) | Verdict |
|---|-------|--------------------|--------------------------|---------|
| 1 | 42/46 inverter tickets preceded within 60 d by a peer-ratio < 0.8 day; median lead 51.5 d | **41/46**, median lead 48.0 d (lead = days to earliest bad day in window) | 35/46, median lead 41.0 d | **CONFIRMED** (-1 ticket, lead within 3.5 d). Note: count is filter-sensitive — drops to 34-35/46 if zero-production days are excluded from the ratio; the qualitative claim (large majority of tickets had a visible precursor) holds in every variant (>= 74%). |
| 2 | INV 01.03.018: 272 of 317 observed days < 0.95 peer ratio in last year; lost ~ EUR 400/yr at 11.5 ct/kWh | **264 of 303 days (87%)**; lost 4,493 kWh = **EUR 517/yr** | 205 of 230 days (89%); EUR 523/yr | **CONFIRMED with caveat.** Day counts and below-0.95 share match (87% vs claimed 86%). The euro figure is a **DISCREPANCY in the point estimate: my EUR ~517-523/yr is ~30% above the claimed ~400** (outside +-10%), but stable across variants and in the conservative direction — the claim *understates* the loss; "on the order of EUR 400/yr" is defensible, EUR ~500/yr is more accurate. |
| 3 | Sections 01.08+01.09 collapse since Aug 2025; multiple inverters with 60-d mean peer ratio < 0.7 at end of data; ~740-840 outage hours each in last 365 d for 01.08.053/057/058 | Outage hours: **053 = 840 h, 057 = 784 h, 058 = 742 h** — all inside the claimed range. Below-0.7 at end: **2 inverters** (053 = 0.55, 058 = 0.58) | Below-0.7 at end: 1 inverter (053 = 0.62) | **CONFIRMED.** Outage hours reproduce almost exactly (filter-independent count: P_AC <= 0.01, irr > 100 W/m², plant median P_AC > 1, DV/EVU >= 99, data present, after first production). "Multiple < 0.7" is the weakest part: I find 2 (minimally "multiple"); 01.08.057 recovered in May 2026 (60-d mean 0.98). The collapse itself is unambiguous — 053/057/058 plus 01.09.060/062 show monthly peer ratios at or near 0 from Aug 2025 through spring 2026. |

## Side observations

- 01.08.052 and 01.08.059 show end-of-data 60-d mean peer ratios of ~1.72 — physically implausible
  for normalized peers and worth a kWp/string-reallocation audit (possibly strings re-routed during
  the 01.08 repairs, or wrong kWp attribution in System_Overview for that section).
- "Median lead" is ambiguous; my 48-51 d match assumes lead = ticket date minus the *earliest*
  bad day in the 60-d window. Measured to the *latest* bad day the median lead is ~7 d.
- Data span: 2016-12-31 to 2026-06-01; "last year" = 365 d ending 2026-06-01 throughout.

## Bottom line

All three headline claims reproduce from raw data. Claim 3's outage hours are an exact match.
Claim 1 reproduces within 1 ticket under a comparable filter (flag the filter sensitivity if
quoted precisely). Claim 2's euro loss appears understated by ~30% — quote "~EUR 500/yr" or
"EUR 400-550/yr" to be safe.
