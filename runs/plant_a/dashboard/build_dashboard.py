#!/usr/bin/env python
"""Build a self-contained HTML dashboard for the Plant A digital twin demo.

Reads CSVs from runs/plant_a/ and writes runs/plant_a/dashboard/index.html
with all data inlined as JSON. Plotly is loaded from CDN.

Usage (from repo root):
    .venv/bin/python runs/plant_a/dashboard/build_dashboard.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent          # runs/plant_a/dashboard
DATA = HERE.parent                              # runs/plant_a
OUT = HERE / "index.html"

DEFAULT_INVERTER = "01.08.057"


def build_data():
    # ---- daily peer ratio ------------------------------------------------
    df = pd.read_csv(DATA / "daily_peer_ratio.csv", parse_dates=["timestamp"],
                     index_col="timestamp").sort_index()
    df = df.replace([np.inf, -np.inf], np.nan)
    # clip absurd outliers (sunrise/sunset division artifacts) for display
    df = df.clip(upper=3.0)
    inverters = list(df.columns)

    # tile color metric: mean peer ratio over the last 90 days of data
    last90 = df.loc[df.index >= df.index.max() - pd.Timedelta(days=90)]
    grid = {}
    for inv in inverters:
        s = last90[inv].dropna()
        grid[inv] = round(float(s.mean()), 4) if len(s) >= 10 else None

    # detail series: 30-day rolling mean, downsampled to weekly means
    roll = df.rolling(30, min_periods=10).mean()
    weekly = roll.resample("W").mean()
    dates = [d.strftime("%Y-%m-%d") for d in weekly.index]
    series = {}
    for inv in inverters:
        vals = weekly[inv].round(4)
        series[inv] = [None if pd.isna(v) else float(v) for v in vals]

    # ---- underperformers -------------------------------------------------
    up = pd.read_csv(DATA / "underperformers.csv")
    up = up.rename(columns={up.columns[0]: "inverter"})
    under = {}
    for _, r in up.iterrows():
        under[r["inverter"]] = {
            "mean_ratio": round(float(r["mean_ratio"]), 3),
            "days_below_95": int(r["days_below_95"]),
            "lost_kwh_365d": float(r["lost_kwh_365d"]),
            "lost_eur_365d": float(r["lost_eur_365d"]),
        }

    # ---- outage hours ----------------------------------------------------
    oh = pd.read_csv(DATA / "outage_hours_honest.csv")
    outage = {}
    for _, r in oh.iterrows():
        outage[r["inverter"]] = {
            "outage_h_total": round(float(r["outage_h_total"]), 1),
            "outage_h_last365d": round(float(r["outage_h_last365d"]), 1),
            "datagap_pct": round(float(r["datagap_pct"]), 1),
        }

    # ---- tickets ----------------------------------------------------------
    tk = pd.read_csv(DATA / "ticket_leadtimes.csv")
    tickets = {}
    for _, r in tk.iterrows():
        lead = None if pd.isna(r["flag_lead_days"]) else int(r["flag_lead_days"])
        tickets.setdefault(r["inverter"], []).append({
            "date": str(r["ticket_date"]),
            "category": str(r["category"]),
            "lead_days": lead,
        })

    return {
        "inverters": inverters,
        "dates": dates,
        "series": series,
        "grid": grid,
        "under": under,
        "outage": outage,
        "tickets": tickets,
        "default": DEFAULT_INVERTER,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plant A Digital Twin — Team Syz</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root {
    --bg: #0d1117;
    --panel: #161b22;
    --panel2: #1c2330;
    --border: #2d3645;
    --text: #e6edf3;
    --muted: #8b98a9;
    --accent: #58a6ff;
    --green: #2ea05f;
    --yellow: #d4a72c;
    --red: #e5484d;
    --gray: #3a4250;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: "Segoe UI", "Inter", -apple-system, Roboto, sans-serif;
    padding: 24px 28px 40px;
  }
  header { margin-bottom: 20px; }
  header h1 { font-size: 26px; font-weight: 650; letter-spacing: .3px; }
  header h1 .team { color: var(--accent); }
  header .sub { color: var(--muted); font-size: 13px; margin-top: 4px; }

  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 18px 0 26px; }
  .kpi {
    background: linear-gradient(160deg, var(--panel2), var(--panel));
    border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px;
  }
  .kpi .big { font-size: 20px; font-weight: 700; line-height: 1.25; }
  .kpi .lbl { color: var(--muted); font-size: 12px; margin-top: 6px; text-transform: uppercase; letter-spacing: .8px; }
  .kpi.alert .big { color: var(--red); }
  .kpi.good .big { color: var(--green); }

  h2 { font-size: 15px; font-weight: 600; color: var(--muted); text-transform: uppercase;
       letter-spacing: 1.2px; margin: 26px 0 12px; }

  .plant { display: flex; flex-wrap: wrap; gap: 14px; }
  .section { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px 12px; }
  .section h3 { font-size: 11px; color: var(--muted); font-weight: 600; margin-bottom: 8px; letter-spacing: .6px; }
  .section .tiles { display: grid; grid-template-columns: repeat(4, 46px); gap: 6px; }
  .tile {
    width: 46px; height: 40px; border-radius: 6px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #0d1117;
    border: 2px solid transparent; transition: transform .08s ease;
    user-select: none;
  }
  .tile:hover { transform: scale(1.1); }
  .tile.selected { border-color: #fff; box-shadow: 0 0 0 2px var(--accent); }
  .tile.green { background: var(--green); }
  .tile.yellow { background: var(--yellow); }
  .tile.red { background: var(--red); color: #fff; }
  .tile.gray { background: var(--gray); color: var(--muted); }
  .legend { display: flex; gap: 18px; margin-top: 10px; color: var(--muted); font-size: 12px; align-items: center; }
  .legend .sw { width: 12px; height: 12px; border-radius: 3px; display: inline-block; margin-right: 6px; vertical-align: -1px; }

  .detail { display: grid; grid-template-columns: 1fr 320px; gap: 14px; align-items: stretch; }
  .chartbox, .statbox { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; }
  .chartbox { padding: 6px; min-height: 380px; }
  .statbox { padding: 18px; font-size: 13px; }
  .statbox h3 { font-size: 17px; margin-bottom: 12px; }
  .statbox .row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); }
  .statbox .row:last-of-type { border-bottom: none; }
  .statbox .k { color: var(--muted); }
  .statbox .v { font-weight: 600; }
  .statbox .v.bad { color: var(--red); }
  .statbox .v.ok { color: var(--green); }
  .statbox .tickets { margin-top: 10px; }
  .statbox .tickets h4 { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 6px; }
  .statbox .ticket { font-size: 12px; padding: 5px 8px; background: var(--panel2); border-radius: 6px; margin-bottom: 5px; border-left: 3px solid var(--red); }
  .statbox .ticket .lead { color: var(--accent); }

  .findings { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  .finding { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; border-top: 3px solid var(--accent); }
  .finding.red { border-top-color: var(--red); }
  .finding.yellow { border-top-color: var(--yellow); }
  .finding h3 { font-size: 14px; margin-bottom: 6px; }
  .finding p { color: var(--muted); font-size: 13px; line-height: 1.5; }

  @media (max-width: 1100px) {
    .kpis, .findings { grid-template-columns: repeat(2, 1fr); }
    .detail { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <h1>Plant A Digital Twin — <span class="team">Team Syz</span></h1>
  <div class="sub">65 inverters · 5-minute telemetry 2017–2026 · peer-normalized performance ratio (1.0 = plant median)</div>
</header>

<div class="kpis">
  <div class="kpi"><div class="big">65 inverters · 9.4 years</div><div class="lbl">Fleet under digital twin</div></div>
  <div class="kpi good"><div class="big">42/46 tickets predicted</div><div class="lbl">Median 51.5 days early warning</div></div>
  <div class="kpi alert"><div class="big">8 inverters failing NOW</div><div class="lbl">Sections 08–09 · active collapse</div></div>
  <div class="kpi"><div class="big">€-losses ranked live</div><div class="lbl">Chronic drag quantified per inverter</div></div>
</div>

<h2>Plant grid — mean peer ratio, last 90 days (click a tile)</h2>
<div class="plant" id="plant"></div>
<div class="legend">
  <span><span class="sw" style="background:var(--green)"></span>&ge; 0.97 healthy</span>
  <span><span class="sw" style="background:var(--yellow)"></span>0.80 – 0.97 degraded</span>
  <span><span class="sw" style="background:var(--red)"></span>&lt; 0.80 failing</span>
  <span><span class="sw" style="background:var(--gray)"></span>no data</span>
</div>

<h2>Inverter detail — full history (30-day rolling mean, weekly)</h2>
<div class="detail">
  <div class="chartbox"><div id="chart" style="width:100%;height:420px"></div></div>
  <div class="statbox" id="stats"></div>
</div>

<h2>Key findings</h2>
<div class="findings">
  <div class="finding red">
    <h3>Sections 08/09: active collapse</h3>
    <p>Eight inverters degrading since Aug 2025 — 01.08.057 at 0.35, 01.09.065 at 0.38 peer ratio.
       Worst outage hours last 365&nbsp;d: 01.08.053 (840&nbsp;h), 01.08.057 (784&nbsp;h). Happening right now.</p>
  </div>
  <div class="finding yellow">
    <h3>01.03.018: unreported fault, €432/yr</h3>
    <p>272 of 317 days below 0.95 peer ratio, ≈ €432 lost per year — and <b>no service ticket exists</b>.
       Their monitoring missed it; the digital twin didn't.</p>
  </div>
  <div class="finding">
    <h3>Error telemetry blind since 2019</h3>
    <p>Error-code logging ended Nov 2019 and never covered sections 08/09. The current collapse is
       invisible to plant error logs — only performance analysis catches it.</p>
  </div>
</div>

<script type="application/json" id="twin-data">__DATA_JSON__</script>
<script>
const D = JSON.parse(document.getElementById('twin-data').textContent);

const css = getComputedStyle(document.documentElement);
const C = {
  green: css.getPropertyValue('--green').trim(),
  yellow: css.getPropertyValue('--yellow').trim(),
  red: css.getPropertyValue('--red').trim(),
  gray: css.getPropertyValue('--gray').trim(),
  accent: css.getPropertyValue('--accent').trim(),
  muted: css.getPropertyValue('--muted').trim(),
  text: css.getPropertyValue('--text').trim(),
  border: css.getPropertyValue('--border').trim(),
};

function bucket(v) {
  if (v === null || v === undefined) return 'gray';
  if (v >= 0.97) return 'green';
  if (v >= 0.80) return 'yellow';
  return 'red';
}

// ---- build plant grid -----------------------------------------------------
const plant = document.getElementById('plant');
const sections = {};
D.inverters.forEach(inv => {
  const sec = inv.split('.').slice(0, 2).join('.');
  (sections[sec] = sections[sec] || []).push(inv);
});
Object.keys(sections).sort().forEach(sec => {
  const box = document.createElement('div');
  box.className = 'section';
  const h = document.createElement('h3');
  h.textContent = 'Section ' + sec;
  box.appendChild(h);
  const tiles = document.createElement('div');
  tiles.className = 'tiles';
  sections[sec].forEach(inv => {
    const t = document.createElement('div');
    const v = D.grid[inv];
    t.className = 'tile ' + bucket(v);
    t.id = 'tile-' + inv;
    t.textContent = inv.split('.')[2];
    t.title = inv + ' — 90d mean ratio: ' + (v === null ? 'n/a' : v.toFixed(2));
    t.addEventListener('click', () => select(inv));
    tiles.appendChild(t);
  });
  box.appendChild(tiles);
  plant.appendChild(box);
});

// ---- detail panel -----------------------------------------------------------
function nearestValue(dateStr) {
  // y position for a ticket marker: nearest non-null weekly value
  const target = new Date(dateStr).getTime();
  let best = null, bestDist = Infinity;
  for (let i = 0; i < D.dates.length; i++) {
    const v = cur.series[i];
    if (v === null) continue;
    const dist = Math.abs(new Date(D.dates[i]).getTime() - target);
    if (dist < bestDist) { bestDist = dist; best = v; }
  }
  return best === null ? 1.0 : best;
}

let cur = { inv: null, series: null };

function select(inv) {
  if (cur.inv) {
    const prev = document.getElementById('tile-' + cur.inv);
    if (prev) prev.classList.remove('selected');
  }
  cur = { inv, series: D.series[inv] };
  const tile = document.getElementById('tile-' + inv);
  if (tile) tile.classList.add('selected');
  drawChart(inv);
  drawStats(inv);
}

function drawChart(inv) {
  const traces = [{
    x: D.dates, y: cur.series, mode: 'lines', name: 'peer ratio (30d roll)',
    line: { color: C.accent, width: 2 }, connectgaps: false,
    hovertemplate: '%{x|%Y-%m-%d}<br>ratio %{y:.3f}<extra></extra>',
  }];
  const tk = D.tickets[inv] || [];
  if (tk.length) {
    traces.push({
      x: tk.map(t => t.date),
      y: tk.map(t => nearestValue(t.date)),
      mode: 'markers', name: 'service ticket',
      marker: { color: C.red, size: 11, symbol: 'diamond', line: { color: '#fff', width: 1 } },
      text: tk.map(t => t.category + (t.lead_days !== null ? ' · flagged ' + t.lead_days + ' d earlier' : '')),
      hovertemplate: '%{x|%Y-%m-%d}<br>%{text}<extra>ticket</extra>',
    });
  }
  Plotly.react('chart', traces, {
    title: { text: inv + ' — peer-normalized performance ratio', font: { size: 15, color: C.text } },
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: C.muted, size: 11 },
    margin: { l: 50, r: 20, t: 46, b: 40 },
    xaxis: { gridcolor: C.border, zeroline: false },
    yaxis: { gridcolor: C.border, zeroline: false, title: { text: 'peer ratio' }, rangemode: 'tozero' },
    shapes: [{
      type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 1.0, y1: 1.0,
      line: { color: C.green, width: 1.5, dash: 'dash' },
    }],
    annotations: [{
      xref: 'paper', x: 1, y: 1.0, xanchor: 'right', yanchor: 'bottom',
      text: 'plant median', showarrow: false, font: { color: C.green, size: 10 },
    }],
    legend: { orientation: 'h', y: -0.18 },
    hovermode: 'closest',
  }, { responsive: true, displayModeBar: false });
}

function fmtEur(v) { return '€' + Math.round(v).toLocaleString('en-US'); }

function drawStats(inv) {
  const u = D.under[inv];
  const o = D.outage[inv];
  const tk = D.tickets[inv] || [];
  const g = D.grid[inv];

  let html = '<h3>' + inv + '</h3>';
  const row = (k, v, cls) => '<div class="row"><span class="k">' + k +
    '</span><span class="v' + (cls ? ' ' + cls : '') + '">' + v + '</span></div>';

  html += row('90-day mean ratio', g === null ? 'no data' : g.toFixed(2),
              g === null ? '' : (g >= 0.97 ? 'ok' : (g < 0.8 ? 'bad' : '')));
  if (u) {
    html += row('365d mean ratio', u.mean_ratio.toFixed(2), u.mean_ratio < 0.8 ? 'bad' : '');
    html += row('Days below 0.95', u.days_below_95 + ' / 317', 'bad');
    html += row('Lost energy (365d)', Math.round(u.lost_kwh_365d).toLocaleString('en-US') + ' kWh', 'bad');
    html += row('Lost revenue (365d)', fmtEur(u.lost_eur_365d), 'bad');
  } else {
    html += row('Chronic underperformer', 'no', 'ok');
  }
  if (o) {
    html += row('Outage hours (total)', o.outage_h_total.toLocaleString('en-US') + ' h');
    html += row('Outage hours (365d)', o.outage_h_last365d.toLocaleString('en-US') + ' h',
                o.outage_h_last365d > 300 ? 'bad' : '');
    html += row('Data gaps', o.datagap_pct.toFixed(1) + ' %');
  }

  html += '<div class="tickets"><h4>Service tickets (' + tk.length + ')</h4>';
  if (tk.length) {
    tk.forEach(t => {
      html += '<div class="ticket">' + t.date + ' · ' + t.category +
        (t.lead_days !== null
          ? '<br><span class="lead">⚑ our flag came ' + t.lead_days + ' days earlier</span>'
          : '') + '</div>';
    });
  } else {
    html += '<div style="color:var(--muted);font-size:12px">none on record' +
            (u ? ' — <b style="color:var(--yellow)">losing ' + fmtEur(u.lost_eur_365d) + '/yr unreported</b>' : '') +
            '</div>';
  }
  html += '</div>';
  document.getElementById('stats').innerHTML = html;
}

select(D.default);
</script>
</body>
</html>
"""


def main():
    data = build_data()
    blob = json.dumps(data, separators=(",", ":"), allow_nan=False)
    html = HTML_TEMPLATE.replace("__DATA_JSON__", blob)
    OUT.write_text(html, encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT} ({size/1e6:.2f} MB, {len(data['inverters'])} inverters, "
          f"{len(data['dates'])} weekly points)")
    assert size < 6_000_000, "index.html exceeds 6 MB budget"


if __name__ == "__main__":
    main()
