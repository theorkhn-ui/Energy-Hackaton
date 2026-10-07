"""Create the frontend's deterministic snapshot from committed analysis outputs."""
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    'runs/plant_a/dashboard/index.html',
    'runs/plant_a/ticket_leadtimes.csv',
    'runs/plant_a/watchlist.csv',
    'runs/plant_a/flag_episodes_material.csv',
    'runs/plant_a/faults/incidents.csv',
    'runs/plant_b/soiling_per_inverter.csv',
    'runs/plant_a/twin/twin_uniform_loss.csv',
    'runs/plant_a/twin/twin_cost_of_delay.csv',
    'runs/plant_a/collapse_cost.csv',
    'runs/plant_a/stale_kwp_audit.csv',
    'runs/plant_a/twin/twin_collapse_cohort.csv',
    'runs/plant_a/twin/TWIN.md',
]


def rows(path):
    with (ROOT / path).open(newline='') as f:
        return list(csv.DictReader(f))


html = (ROOT / SOURCES[0]).read_text()
match = re.search(r'<script[^>]*id="twin-data"[^>]*>(.*?)</script>', html, re.S)
if not match:
    raise ValueError('Missing original dashboard data')
plant = json.loads(match.group(1))
tickets = rows(SOURCES[1])
leads = [float(r['flag_lead_days']) for r in tickets if r['flag_lead_days']]
episodes = rows(SOURCES[3])
unticketed = [r for r in episodes if r['ticket'] == 'False']
incidents = rows(SOURCES[4])
counts = Counter(r['classification'] for r in incidents)
families = defaultdict(lambda: {'TRIP': 0, 'DERATE': 0, 'NUISANCE': 0, 'lostKwh': 0})
for r in incidents:
    families[r['family']][r['classification']] += 1
    families[r['family']]['lostKwh'] += float(r['lost_kwh'] or 0)
soiling = rows(SOURCES[5])
snapshot = {
    'sourceCommit': subprocess.check_output(
        ['git', 'log', '-1', '--format=%H', '--', 'runs'], cwd=ROOT, text=True).strip(),
    'plant': plant,
    'metrics': {
        'tickets': len(tickets), 'earlyTickets': len(leads),
        'medianLeadDays': statistics.median(leads),
        'episodes': len(episodes), 'unticketedEpisodes': len(unticketed),
        'unticketedLossEur': sum(float(r['lost_eur']) for r in unticketed),
        'alarmIncidents': len(incidents), 'alarmCounts': dict(counts),
        'soilingInverters': sum(int(r['n_episodes']) > 0 for r in soiling),
        'plantBInverters': len(soiling),
    },
    'watchlist': [{
        'inverter': r['inverter'], 'ratio': float(r['ratio_last60d']),
        'trend': r['trend'], 'severity': r['severity'],
        'lossEur': float(r['est_eur_per_yr']) if r['est_eur_per_yr'] else None,
        'hasTicket': r['ticket_last_120d'] == 'True', 'action': r['action'],
    } for r in rows(SOURCES[2])],
    'tickets': [{
        'inverter': r['inverter'], 'date': r['ticket_date'],
        'category': r['category'],
        'leadDays': float(r['flag_lead_days']) if r['flag_lead_days'] else None,
    } for r in tickets],
    'families': [{'family': k, **v} for k, v in families.items()],
    'soiling': [{
        'inverter': r['inverter'], 'orientation': r['orient'],
        'episodes': int(r['n_episodes']),
        'maxDecline': float(r['max_episode_decline_pct']) if r['max_episode_decline_pct'] else None,
    } for r in soiling],
    'uniformLoss': [{
        'metric': r['metric'], 'before': float(r['before']), 'after': float(r['after']),
    } for r in rows(SOURCES[6])],
    'delay': [{'days': int(r['repair_in_days']), 'loss': float(r['cumulative_loss_eur'])}
              for r in rows(SOURCES[7])],
    'collapse': [{'inverter': r['inverter'], 'lossEur': float(r['lost_eur_since_aug25']),
                  'ratio': float(r['mean_ratio_since_aug25'])} for r in rows(SOURCES[8])],
    'capacityAudit': [{'inverter': r['inverter'], 'registeredKwp': float(r['registered_kwp']),
                       'impliedKwp': float(r['implied_kwp_from_median']),
                       'classification': r['classification']} for r in rows(SOURCES[9])],
    'currentLossEurPerYear': sum(float(r['realized_loss_eur_yr']) for r in rows(SOURCES[10])),
    'provenance': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
                   for p in SOURCES],
}
assert (len(tickets), len(leads), statistics.median(leads)) == (46, 42, 51.5)
assert (len(episodes), len(unticketed), snapshot['metrics']['unticketedLossEur']) == (477, 444, 64247)
assert counts == {'TRIP': 204, 'DERATE': 37, 'NUISANCE': 582}
assert snapshot['metrics']['soilingInverters'] == 37
assert len(plant['inverters']) == 65
assert len(soiling) == 107
content = json.dumps(snapshot, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'
target = ROOT / 'frontend/src/results.json'
if '--check' in sys.argv:
    if not target.exists() or target.read_text() != content:
        raise SystemExit('Snapshot is stale. Run npm run data.')
    print('Snapshot verified against all %s source artifacts; headline metrics reconciled.' % len(SOURCES))
else:
    target.write_text(content)
    print('Wrote', target.relative_to(ROOT))
