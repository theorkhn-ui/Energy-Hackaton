# HANDOFF - read me first, update me before you step away

> New here? Read `MAXAT_START_HERE.md` for full setup + the Claude-to-Claude protocol.

## Questions
(none open - Claudes: post questions for each other here)

> Convention: whoever (human or Claude) finishes a work session updates **Current status**,
> **Next up**, and **Blockers**, then commits with message `handoff: <summary>`.

## Current status (2026-06-12 evening)
- Challenge **#3.1 E.ON Grid Operation Agents** CONFIRMED FINAL (recount of sheet: #1.1 has 5 teams, #3.1 has 2-4 -> see `00-challenge-analysis.md`).
- `src/grid_tools.py`: agent tool functions (powerflow, overloads, switch line, redispatch, shed).
- `src/n1_screening.py`: N-1 scan works. Demo line remains `case30` line 9.
- `src/baseline_agent.py`: rule-based fixer is the comparison target.
- `src/agent.py`: **LLM agent loop done** (Anthropic tool-use, narrated transcript saved to runs/). `--mock` mode tests plumbing without API key - verified working. Real LLM run still untested (needs `ANTHROPIC_API_KEY`).
- `src/viz.py`: grid plots, overloads red with percentage labels, tripped lines dotted - rendered, looks good (see `runs/*.png`).
- Maxat confirmed local setup works with Python 3.12.10.
- Scripts can now normalize the intact grid to a safe loading level before screening contingencies. Default clean demo: `python src/baseline_agent.py case30 9` starts safe at 80.0%, trips line 9, creates one overload at 109.7%, and the baseline clears it after load shedding.
- For a harsher strawman comparison, use Orkhan's stressed line-9 scenario where loading reaches ~153-183% and the baseline fails.

## Next up (Maxat / Maxat's Claude - pick any, update this file)
- [ ] Run real LLM agent: `ANTHROPIC_API_KEY=... python src/agent.py --trip 9` - iterate on system prompt until it reliably clears overloads with minimal load shed.
- [ ] Benchmark script: agent vs baseline across ALL dangerous N-1 outages (table: cleared? actions? MW shed?) - this is our "honest eval" judges love.
- [ ] Try case118 (bigger grid = more impressive).
- [ ] Video plan: storyboard 4-min cut (hook -> problem -> agent demo with narration -> eval table -> close).
- [ ] Useful skills to install (vetted): Power-Agent/PowerSkills (pandapower mitigation playbooks), remotion-dev/skills (video), tvhahn/matplotlib-skill.

## Task split (proposal - Maxat, edit!)
- Orkhan: agent loop + prompts + narration output.
- Maxat: benchmark eval, bigger grid, visualization polish.

## Blockers
- Real LLM run needs `ANTHROPIC_API_KEY`.

## Decisions log
- 2026-06-12: Switched from #1.1 (crowded, 3+ teams) to #3.1 (least competition, best demo). Need to update registration sheet!
- 2026-06-12: Normalize line ratings for clean demo runs because pandapower `case30` is overloaded under its built-in ratings before any contingency.
