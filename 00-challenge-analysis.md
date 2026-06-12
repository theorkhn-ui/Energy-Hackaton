# Energy Hack — Challenge Selection (2026-06-12)

Team: **Syz** (Orkhan Karimov, Maxat Issaliyev) · Prize: €1000 · Deliverable: **4-min video, hard cap**

## Competition snapshot (registration sheet)

| Challenge | Declared teams |
|---|---|
| #1.1 Invertix: Data-Center Siting & Power | Syz, OptimalPrime (3p), Rishabh/Vinayak — **3 teams** |
| #1.2 Invertix: Open Track | 0 |
| #2.1/#2.2 Enerparc: Digital Twin | StealthDetection.Ai (4p) — 1 team |
| #2.3 Enerparc: Open Track | 0 |
| #3.1 E.ON: Grid Operation Agents | Fero Hatami (solo, unclear) |
| #3.2 E.ON: Open Track | 0 |

~8 more teams undecided; Data-Center Siting likely gets the most pile-on (lowest entry barrier).

## Recommendation: switch to **#3.1 E.ON Grid Operation Agents**

- Perceived as hard (N-1 security, power flow) → scares teams off → least competition
- Actually feasible: **pandapower** handles all physics; IEEE test grids built in
- Blueprint provided: **arXiv:2512.20789 (X-GridAgent)** — LLM agent driving pandapower via MCP tools
- Killer 4-min demo: line trips → agent reasons step-by-step → grid back to safe state, narrated
- Judges = E.ON grid engineers; explainability is exactly what they ask for

### Pointers from the challenge guide
- Grid simulator: pandapower (power-flow + contingency engine, IEEE grids)
- European grids: PyPSA-Eur prebuilt network, Zenodo 18619025
- Pretrained model: Microsoft GridSFM_Open (small, CPU-runnable)
- RL prior art: Grid2Op, L2RPN competitions
- Real data: SMARD.de (German TSO)

### MVP plan sketch
1. pandapower + IEEE 30/118 grid, script N-1 contingency screening
2. LLM agent with tools: run_powerflow, switch_line, redispatch_gen, curtail — loop until no overloads
3. Baseline comparison: rule-based vs agent (judges love honest evals)
4. Simple grid visualization (before/after, overloaded lines in red) for the video

## Backup: #2.1 Enerparc Digital Twin
Real plant data, tractable (anomaly/soiling detection), but data-cleaning heavy and StealthDetection.Ai (4p) is on the twin topic.

## Avoid
- #1.1: crowded, hard to differentiate
- Open tracks: no rubric anchor, scope-definition burns time
