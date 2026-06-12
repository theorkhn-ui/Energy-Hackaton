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

## Stage 5 (Orkhan's Claude): judge-facing layer done
- Maxat verification update (2026-06-13): independent verification pass complete. Reran `src/twin/run_plant_a.py`, `deep_analysis.py outages`, and `deep_analysis.py tickets`; confirmed 65 inverters / 990,442 rows, 42/46 tickets with 51.5d median lead, INV 01.03.018 at 0.701 ratio / EUR432/yr / no ticket, and the 01.08/01.09 collapse story.
- Maxat stale-kWp audit complete: `runs/plant_a/STALE_KWP_AUDIT.md` quantifies 8 clean register candidates plus 2 operationally confounded 08/09 units. Video production remains intentionally pending.
- README.md rewritten as evidence trail ("Plant Sentinel"), docs/ONE_PAGER.md, docs/QA_PREP.md (13 prepared answers)
- runs/plant_a/WATCHLIST.md — forward-looking "inspect Monday" list (3 CRITICAL, 10 MAJOR; 11 of 13 have NO recent ticket) → closes the brief's "predict future failures" item
- Loader cross-check: Maxat's CSV loader vs parquet = 0.0 diff on 22,854 rows → implementations consistent
- Maxat's verification of headline numbers still pending — DO IT before final render

## Stage 4 (Orkhan's Claude): FULL BRIEF COVERAGE — Plant B soiling done (37/107 inverters, recurring 05.08.106/107 sawtooth) + automated fault classification (823 incidents, 71% nuisance alarms). New video-ready charts: runs/plant_b/soiling_chart.png, runs/plant_a/faults/fault_matrix.png. Storyboard option: add a 20s "we covered all five challenge directions" beat or swap the weakest scene.

## ⚡ STORYBOARD NUMBER UPDATES (Orkhan's Claude, stage 3 — fold into narration before render)
- Add: "€64k of underperformance over 9 years never got an inverter ticket" (finding 9)
- Collapse scene: say "€42k/yr of revenue at risk" not realized losses (finding 10)
- Honesty beat: add "our flags fire 10× more often than tickets exist — that's the blind spot, not noise"
- Product shot: screen-record runs/plant_a/dashboard/index.html (open in browser, click 2-3 red tiles)

## Sync note (Max, 2026-06-12 late)
- Rebased Max's local work on top of Orkhan stage 2/3. Kept Orkhan's dashboard/storyboard/final numbers as the narrative source of truth.
- `src/twin/run_plant_a.py` now supports this local workspace layout via sibling `../Data/Plant A (start here)` and does not require pyarrow for Max's machine.

## 🎬 MAXAT'S CLAUDE — CURRENT TASK LIST (updated after clean-room verification)
Analysis is FROZEN — numbers verified by an independent third implementation (runs/plant_a/VERIFICATION.md). Your verification assignment is DONE/superseded. Remaining work is 100% production:

1. **Video numbers pass**: in video/src/, update Scene 5: €432 → **~€500/yr** (verified); Scene 6 wording: "2 inverters still below 0.7; one recovered in May" (honest phrasing); check every on-screen number against VERIFICATION.md + FINDINGS.md stages 5-6.
2. **Voiceover**: record narration from docs/VIDEO_STORYBOARD.md (or pick a clean TTS), drop as video/public/voiceover.mp3, set HAS_VOICEOVER flag (see video/VoiceoverNote.md), hand-sync caption timings.
3. **Preview & render**: `cd video && npm install && npx remotion studio` → review all 9 scenes → `npx remotion render MainVideo out/video.mp4`. Watch it END TO END at least twice. Confirm ≤4:00.
4. **Dashboard screen-capture**: open runs/plant_a/dashboard/index.html, record ~20s clicking 2-3 red tiles, embed per video/README.md (optional but recommended — it's the product shot).
5. **kWp scene polish** (optional): kwp_audit.csv now has the smoking gun (01.05.030: 5.64 registered vs 23 kW peak) — Scene 7 can show the actual table.
6. **Submission logistics**: find out where/how the video is submitted and the exact deadline. Tell Orkhan. Do this FIRST — it bounds everything.

## Orkhan's Claude next (in progress)
- Maxat 2026-06-13 note: analysis-side assignment items 2 and 3 are done; only video production remains pending on Maxat's side.
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
