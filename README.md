# Team Syz — Energy Hack Munich 2026

**Challenge #3.1 — E.ON: Grid Operation Agents** (keeping a stressed grid N-1 secure)

An LLM agent that takes an overloaded power grid back to a safe state and explains its reasoning step by step. Physics via [pandapower](https://www.pandapower.org/); blueprint: X-GridAgent (arXiv:2512.20789).

## Team
Orkhan Karimov · Maxat Issaliyev

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/n1_screening.py   # smoke test: N-1 scan on IEEE 30-bus grid
python src/baseline_agent.py case30 9
```

Optional tuning:
```bash
python src/n1_screening.py case30 1.00 80
python src/baseline_agent.py case30 9 1.00 80
```

The last two values are load scale and normalized intact-grid max loading (%).

## Structure
```
src/grid_tools.py     # grid actions exposed as agent tools (powerflow, switch, redispatch)
src/n1_screening.py   # N-1 contingency scan — finds dangerous line outages
src/baseline_agent.py # rule-based fixer (the baseline our LLM agent must beat)
notes/                # per-person scratch notes
HANDOFF.md            # READ FIRST — current status + who does what
```

## Workflow (2 humans + 2 Claudes)
1. `git pull` before starting anything
2. Read `HANDOFF.md`
3. Work, commit small, push often
4. Update `HANDOFF.md` before stepping away

## Deliverable
4-minute video (HARD CAP). Demo: line trips → grid overloads → agent reasons + acts → grid safe again.
