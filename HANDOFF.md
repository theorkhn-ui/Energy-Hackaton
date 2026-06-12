# HANDOFF - read me first, update me before you step away

> New here? Read `MAXAT_START_HERE.md` for full setup + the Claude-to-Claude protocol.

## Questions
- **To Maxat's Claude (from Orkhan's Claude):** sorry — your normalize-scenario work landed mid-pivot (good work, it's preserved in `archive/grid-agent-3.1/` with your changes intact). We are NOT on #3.1 anymore, see below. Please `git pull`, read the pivot note, and pick a task from the new "Next up".

> Convention: whoever (human or Claude) finishes a work session updates **Current status**,
> **Next up**, and **Blockers**, then commits with message `handoff: <summary>`.

## ⚠️ PIVOT (2026-06-12 late evening): challenge is now **#2.1 Enerparc Digital Twin**
Sheet recount: #3.1 ballooned to 5-6 teams (GridFlow.ai, Voltify, winsortf, Fero, mahanc); Enerparc digital twin has only 2 (StealthDetection.Ai 4p + solo Pyra). Fewer rivals + real-data analysis suits a 2p Claude-assisted team → switched. Orkhan confirmed "whatever optimizes winning".

- 3.1 code moved to `archive/grid-agent-3.1/` (incl. Maxat's scenario-normalization improvements — reusable if anything changes)
- NEW `src/twin/`: data_loader.py (Enerparc schema per dataset slides), analysis.py
  (performance index → peer-normalized ratio → underperformer / soiling / outage flags),
  synthetic_test.py — **all 3 planted fault types detected ✓**
- Waiting on real Plant A data from Orkhan. First job when it lands: fix column regexes
  in data_loader.py, then rerun the same analysis.

## 🔥 DATA IS IN — first results live (see runs/plant_a/FINDINGS.md)
Plant A analyzed end-to-end: 65 inverters, 9.4 years. Headlines: (1) ACTIVE section failure 01.08-01.09 since Aug 2025, (2) unreported fault 01.03.018 (€432/yr, no ticket!), (3) our flags match their ticket history (058: 4 tickets, 062: 3). Pipeline: `src/twin/run_plant_a.py`. NOTE: raw data NOT in git (data/raw is gitignored, ~3GB) — Maxat: get the zips from Orkhan or the Drive link, extract to `data/raw/`.

## Stage 2 DONE (Orkhan's Claude): 42/46 tickets predicted (median lead 51.5d) · honest outage table · error-telemetry blind-spot finding · 3 video charts in runs/plant_a/viz/ · full storyboard in docs/VIDEO_STORYBOARD.md

## ⚡ STORYBOARD NUMBER UPDATES (Orkhan's Claude, stage 3 — fold into narration before render)
- Add: "€64k of underperformance over 9 years never got an inverter ticket" (finding 9)
- Collapse scene: say "€42k/yr of revenue at risk" not realized losses (finding 10)
- Honesty beat: add "our flags fire 10× more often than tickets exist — that's the blind spot, not noise"
- Product shot: screen-record runs/plant_a/dashboard/index.html (open in browser, click 2-3 red tiles)

## Sync note (Max, 2026-06-12 late)
- Rebased Max's local work on top of Orkhan stage 2/3. Kept Orkhan's dashboard/storyboard/final numbers as the narrative source of truth.
- `src/twin/run_plant_a.py` now supports this local workspace layout via sibling `../Data/Plant A (start here)` and does not require pyarrow for Max's machine.

## 🎬 MAXAT'S CLAUDE — your assignments (everything analysis-side is done)
1. **PRODUCE THE VIDEO** from docs/VIDEO_STORYBOARD.md using the remotion-best-practices skill (installed via MAXAT_START_HERE.md §2). Assets: runs/plant_a/viz/*.png + runs/plant_a/heatmap_monthly_ratio.png. 1080p30, burned-in captions, HARD CAP 4:00 (storyboard is 3:50).
2. **Independent verification pass**: re-run `src/twin/run_plant_a.py` + `deep_analysis.py outages|tickets`, confirm the three headline numbers (42/46 & 51.5d; 01.03.018 €432 no-ticket; 08/09 collapse) — we must not show a wrong number to engineers.
3. If time remains: quantify stale-kWp group (which inverters, how far off, what correct kWp would be).

## Orkhan's Claude next (in progress)
- [ ] Findings one-pager for submission (if a written deliverable is allowed)
- [ ] Optional: Plant B soiling quick-pass (only if video is on track)

## Old status (#3.1, archived 2026-06-12)
- LLM agent loop mock-verified; viz rendered; N-1 scan working.
- Maxat: setup confirmed (Python 3.12.10); added grid normalization — clean demo starts safe at 80%, line-9 trip → 109.7% overload, baseline clears it; Orkhan's stressed variant (153-183%) makes the baseline fail.

## Task split (proposal — edit!)
- Orkhan's Claude: data pipeline, real-data analysis when it lands
- Maxat's Claude: video storyboard + plot templates (doable now), then tickets/errorcode cross-ref

## Blockers
- Real Plant A data not yet received (Orkhan fetching).

## Decisions log
- 2026-06-12: #1.1 → #3.1 (competition).
- 2026-06-12: Normalize line ratings for clean demo runs (case30 overloaded under built-in ratings).
- 2026-06-12 late: #3.1 → **#2.1 Enerparc Digital Twin** (competition recount; FINAL — sheet updated by Orkhan? VERIFY).
