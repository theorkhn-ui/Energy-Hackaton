# Team Syz — Energy Hack Munich 2026

**Challenge #2.1 — Enerparc: Digital Twin of a Solar Plant**

We turn real PV monitoring data into verified, revenue-ranked findings: per-inverter
performance modelling, curtailment-aware fault/outage detection, soiling drift, and
cross-validation against the plant's real service tickets.

## Team
Orkhan Karimov · Maxat Issaliyev

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/twin/synthetic_test.py   # smoke test: plants 3 fault types, must detect all 3
```

## Structure
```
src/twin/data_loader.py     # Enerparc schema loaders (monitoring, tickets, system overview)
src/twin/analysis.py        # performance index -> peer ratio -> underperformer/soiling/outage flags
src/twin/synthetic_test.py  # pipeline smoke test with planted faults
archive/grid-agent-3.1/     # previous challenge (E.ON grid agent), kept for reference
HANDOFF.md                  # READ FIRST — current status + who does what
MAXAT_START_HERE.md         # onboarding + Claude-to-Claude git protocol
```

## Why we win (differentiators)
1. **Curtailment-aware**: EVU/DV signals separate real outages from grid curtailment
   (the dataset slides explicitly warn about this trap — most teams will fall into it).
2. **Ticket cross-validation**: flags verified against the real service-ticket log;
   "predicted ticket X weeks early" is a checkable claim.
3. **Revenue ranking**: findings priced via feed-in tariffs — engineers think in euros.

## Workflow (2 humans + 2 Claudes)
1. `git pull` before starting anything
2. Read `HANDOFF.md`
3. Work, commit small, push often
4. Update `HANDOFF.md` before stepping away

## Deliverable
4-minute video (HARD CAP).
