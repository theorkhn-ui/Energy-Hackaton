# Maxat (+ Maxat's Claude) — onboarding

Written by Orkhan's Claude. We coordinate Claude-to-Claude through this repo — read this once, then `HANDOFF.md` is the living sync point.

## 1. Human setup (Maxat, ~10 min)

```bash
git clone https://github.com/theorkhn-ui/Energy-Hackaton.git
cd Energy-Hackaton
python -m venv .venv && source .venv/bin/activate   # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
python src/n1_screening.py    # should print a table of dangerous line outages
```

If using **Cowork**: mount the cloned folder. If using **Claude Code**: just `claude` inside the repo.
Ask Orkhan for collaborator access if push fails (github.com/theorkhn-ui/Energy-Hackaton → he invites you).

## 2. Install the same skills (so both Claudes are equally equipped)

In Claude Code, one at a time:
```
/plugin marketplace add https://github.com/Power-Agent/PowerSkills
/plugin install powerskills-tool@powerskills
/plugin install powerskills-engineering@powerskills
/plugin marketplace add https://github.com/anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
/reload-plugins
```

In a terminal (bash; for fish drop nothing, commands are compatible):
```bash
npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices
git clone --depth 1 https://github.com/tvhahn/matplotlib-skill /tmp/mpl-skill
mkdir -p ~/.claude/skills
cp -r /tmp/mpl-skill/skills/matplotlib ~/.claude/skills/
git clone --depth 1 https://github.com/EveryInc/product-launch-video /tmp/plv
cp -r /tmp/plv/.claude/skills/* ~/.claude/skills/
cp -r ~/.agents/skills/remotion-best-practices ~/.claude/skills/  # if the installer skipped Claude Code
```

## 3. Instructions for Maxat's Claude (paste this to your Claude)

> You are working with another Claude (Orkhan's) on this repo. Protocol:
> 1. **Start of every session:** `git pull`, read `HANDOFF.md` fully, read `00-challenge-analysis.md` once for context.
> 2. Claim a task: edit HANDOFF "Next up", put your name on it, commit `handoff: claiming <task>`, push — this prevents duplicate work.
> 3. Work in small commits with clear messages. Push often — pushes are our messages to each other.
> 4. **End of every session:** update HANDOFF (status / next / blockers / decisions), commit `handoff: <summary>`, push.
> 5. Questions for Orkhan's Claude go in HANDOFF under "## Questions" — it checks on every pull.
> 6. Never force-push. If push is rejected: pull --rebase, resolve, push.

## 4. Project state in one paragraph

Challenge **#2.1 Enerparc: Digital Twin of a Solar Plant** (pivoted from #3.1 on June 12 — #3.1 got crowded, digital twin has only 2 rival teams). We turn real PV monitoring data into findings: per-inverter performance index → peer-normalized ratio → flags for chronic underperformance, soiling drift, and outages (curtailment-aware), then cross-reference with service tickets and error codes. Pipeline in `src/twin/` is built and verified on synthetic data (`synthetic_test.py` — all planted faults detected). Old #3.1 grid-agent code is in `archive/grid-agent-3.1/`. Waiting on the real Plant A dataset. Deliverable: 4-min video (hard cap). Open tasks live in `HANDOFF.md`.
