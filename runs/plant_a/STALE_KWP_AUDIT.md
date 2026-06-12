# Stale kWp Register Audit

Method: if an inverter is persistently above peer ratio 1.1, estimate the corrected asset-register capacity as `registered_kWp * median_peer_ratio`.

## Clean Register Candidates (8)

| inverter  | registered_kwp | median_ratio | pct_days_above_1_1 | implied_kwp_from_median | kwp_gap | registered_understated_pct |
| --------- | -------------- | ------------ | ------------------ | ----------------------- | ------- | -------------------------- |
| 01.05.030 | 5.64           | 5.149        | 0.891              | 29.039                  | 23.399  | 80.578                     |
| 01.07.049 | 16.92          | 1.845        | 0.986              | 31.225                  | 14.305  | 45.813                     |
| 01.07.051 | 16.92          | 1.663        | 0.793              | 28.144                  | 11.224  | 39.88                      |
| 01.04.026 | 18.0           | 1.554        | 0.912              | 27.977                  | 9.977   | 35.661                     |
| 01.07.048 | 22.56          | 1.394        | 0.971              | 31.456                  | 8.896   | 28.282                     |
| 01.07.050 | 22.56          | 1.292        | 0.867              | 29.158                  | 6.598   | 22.628                     |
| 01.06.040 | 24.48          | 1.263        | 0.974              | 30.907                  | 6.427   | 20.794                     |
| 01.04.027 | 23.52          | 1.231        | 0.761              | 28.964                  | 5.444   | 18.795                     |

These are the strongest master-data candidates because they are outside the active 01.08/01.09 collapse section and stay high for most observed days.

## Operationally Confounded High-Ratio Units (2)

| inverter  | registered_kwp | median_ratio | pct_days_above_1_1 | implied_kwp_from_median | kwp_gap | registered_understated_pct |
| --------- | -------------- | ------------ | ------------------ | ----------------------- | ------- | -------------------------- |
| 01.08.059 | 16.56          | 1.751        | 0.953              | 28.991                  | 12.431  | 42.879                     |
| 01.08.052 | 17.28          | 1.676        | 0.953              | 28.965                  | 11.685  | 40.342                     |

These sit in sections 01.08/01.09, where the active collapse can distort peer ratios. Do not use them as register-only evidence without field inspection.

## Watch Only (2)

| inverter  | registered_kwp | median_ratio | pct_days_above_1_1 | implied_kwp_from_median | kwp_gap | registered_understated_pct |
| --------- | -------------- | ------------ | ------------------ | ----------------------- | ------- | -------------------------- |
| 01.08.054 | 28.2           | 1.107        | 0.533              | 31.212                  | 3.012   | 9.651                      |
| 01.09.061 | 27.6           | 1.102        | 0.509              | 30.414                  | 2.814   | 9.252                      |