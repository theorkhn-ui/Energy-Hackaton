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

## Next up (when data arrives — claim by putting your name)
- [ ] Load real Plant A, fix loader, run full pipeline
- [ ] Cross-reference flags with Tickets.xlsx (predicted-the-ticket = killer finding)
- [ ] Error-code joining (errorcodes.* + translation table) → fault classification
- [ ] Per-inverter findings dashboard/plots for the video
- [ ] Plant B soiling dataset (optional, only after Plant A complete)

## Doable NOW (no data needed)
- [ ] Video storyboard: 4-min cut (hook → plant problem → live findings → ticket prediction → close)
- [ ] Plot templates with matplotlib skill: peer-ratio heatmap (inverter × day), soiling drift chart
- [ ] Read Enerparc dataset slides in `Energy_Hack_Challenges_final.pdf` pp. 5-7

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
