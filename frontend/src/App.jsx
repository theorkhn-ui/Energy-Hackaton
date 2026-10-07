import { useEffect, useRef, useState } from 'react';
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BellRing,
  BookOpen,
  CalendarDays,
  ChevronDown,
  Download,
  ExternalLink,
  FlaskConical,
  GitFork,
  Grid2X2,
  LayoutDashboard,
  Leaf,
  Menu,
  ShieldCheck,
  Sun,
  TrendingDown,
  X,
  Zap,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import data from './results.json';

const REPO = 'https://github.com/theorkhn-ui/Energy-Hackaton';
const source = (path) => `${REPO}/blob/${data.sourceCommit}/${path}`;
const m = data.metrics;
const dateLabel = (date) =>
  new Date(`${date}T12:00:00Z`).toLocaleDateString('en-GB', {
    month: 'short',
    year: '2-digit',
    timeZone: 'UTC',
  });
const fullDate = (date) =>
  new Date(`${date}T12:00:00Z`).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  });
const euro = (value) =>
  new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value);
const COLORS = { TRIP: '#dd896a', DERATE: '#e5bb6b', NUISANCE: '#8ba897' };
const tabs = [
  { id: 'overview', name: 'Overview', icon: LayoutDashboard },
  { id: 'inverters', name: 'Inverter health', icon: Grid2X2 },
  { id: 'warnings', name: 'Early detection', icon: Activity },
  { id: 'faults', name: 'Alarm intelligence', icon: BellRing },
  { id: 'impact', name: 'Energy & impact', icon: TrendingDown },
  { id: 'soiling', name: 'Soiling & shading', icon: Sun },
  { id: 'validation', name: 'Model validation', icon: FlaskConical },
];
const titleFor = {
  overview: 'Solar intelligence, at a glance.',
  inverters: 'Every inverter tells a story.',
  warnings: 'See the fault before the ticket.',
  faults: 'Less noise. More signal.',
  impact: 'Put a value on the performance gap.',
  soiling: 'The losses hiding in plain sight.',
  validation: 'A twin you can put to the test.',
};
const descriptionFor = {
  overview:
    'A closer look at what the digital twin found in real solar-plant data.',
  inverters: 'Compare 65 inverters, then explore their historical performance.',
  warnings:
    'Historical performance flags, checked against the service-ticket log.',
  faults: 'Prioritize alarms by their measured power impact.',
  impact:
    'Separate historical losses, modeled run rates, and asset-register questions.',
  soiling: 'Decline-and-recovery patterns across 107 inverters at Plant B.',
  validation:
    'Physical baselines, independent checks, and a controlled loss scenario.',
};

function SourceLink({ path, children = 'View evidence' }) {
  return (
    <a
      className="source-link"
      href={source(path)}
      target="_blank"
      rel="noreferrer"
    >
      {children}
      <ArrowUpRight size={13} />
    </a>
  );
}

function Stat({ icon: Icon, label, value, suffix, foot, tag, tone = '' }) {
  return (
    <article className={`stat ${tone}`}>
      <div className="stat-label">
        <span>{label}</span>
        <Icon size={17} />
      </div>
      <div className="stat-value">
        {value}
        <span>{suffix}</span>
      </div>
      <div className="stat-foot">
        <span>{foot}</span>
        {tag ? <span className="small-tag">{tag}</span> : null}
      </div>
    </article>
  );
}

function ChartTip({ active, payload, label, percent = false }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <strong>
        {/^\d{4}-\d{2}-\d{2}$/.test(String(label)) ? fullDate(label) : label}
      </strong>
      {payload
        .filter((p) => p.value !== null)
        .map((p) => (
          <div key={p.dataKey}>
            <span style={{ background: p.color }} />
            {p.name}
            <b>
              {percent
                ? `${(p.value * 100).toFixed(1)}%`
                : Number(p.value).toLocaleString('en-GB')}
            </b>
          </div>
        ))}
    </div>
  );
}

function PanelHead({ eyebrow, title, children }) {
  return (
    <div className="panel-head">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h2>{title}</h2>
      </div>
      {children}
    </div>
  );
}

function PerformanceChart({ selected, setSelected, period, setPeriod }) {
  const cutoff = period === '18m' ? '2025-01-01' : '2017-01-01';
  const points = data.plant.dates.flatMap((date, i) =>
    date >= cutoff ? [{ date, ratio: data.plant.series[selected][i] }] : [],
  );
  const upper = Math.max(1.25, ...points.map((p) => p.ratio ?? 0)) * 1.04;
  const tickets = data.plant.tickets[selected] || [];
  const ratio = data.plant.grid[selected];
  const warning = ratio !== null && ratio < 0.8;
  const color = warning ? '#ce8865' : '#5d8b6d';
  const nearestWeek = (date) =>
    points.reduce(
      (best, p) =>
        Math.abs(Date.parse(p.date) - Date.parse(date)) <
        Math.abs(Date.parse(best.date) - Date.parse(date))
          ? p
          : best,
      points[0],
    ).date;
  return (
    <section className="panel performance-panel" id="performance">
      <PanelHead eyebrow="PERFORMANCE OVER TIME" title="Inverter performance">
        <div className="segmented" aria-label="Chart period">
          <button
            aria-pressed={period === '18m'}
            onClick={() => setPeriod('18m')}
          >
            18 months
          </button>
          <button
            aria-pressed={period === 'all'}
            onClick={() => setPeriod('all')}
          >
            Full history
          </button>
        </div>
      </PanelHead>
      <div className="chart-context">
        <label className="select-wrap">
          <span className="sr-only">Inverter</span>
          <select
            aria-label="Inverter"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {data.plant.inverters.map((inv) => (
              <option key={inv} value={inv}>
                INV {inv}
              </option>
            ))}
          </select>
          <ChevronDown size={14} />
        </label>
        <span className={`status-dot ${warning ? 'orange' : 'green'}`}>
          {warning
            ? 'Below peer output'
            : ratio > 1.3
              ? 'Check registered capacity'
              : 'Peer comparison'}
        </span>
        <div className="chart-legend">
          <span className="line-swatch" style={{ background: color }} />
          Peer ratio
          <span className="dotted-swatch" />
          Baseline
        </div>
      </div>
      <div
        className="performance-chart"
        role="img"
        aria-label={`Historical peer performance ratio of inverter ${selected}. A ratio of 1 equals the plant median.`}
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={points}
            margin={{ top: 14, right: 12, left: -22, bottom: 0 }}
          >
            <defs>
              <linearGradient id="performanceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.16} />
                <stop offset="100%" stopColor={color} stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid
              vertical={false}
              stroke="#e9ece5"
              strokeDasharray="3 4"
            />
            <XAxis
              dataKey="date"
              tickFormatter={dateLabel}
              tick={{ fill: '#879084', fontSize: 10 }}
              minTickGap={44}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, upper]}
              tickFormatter={(v) => `${Math.round(v * 100)}%`}
              tick={{ fill: '#879084', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              width={54}
            />
            <Tooltip content={<ChartTip percent />} />
            <ReferenceLine y={1} stroke="#9ea99b" strokeDasharray="5 5" />
            {tickets
              .filter((t) => t.date >= cutoff && t.date <= points.at(-1).date)
              .map((t, i) => (
                <ReferenceLine
                  key={`${t.date}-${i}`}
                  x={nearestWeek(t.date)}
                  stroke="#92a0bd"
                  strokeDasharray="2 5"
                  label={{
                    value: 'Ticket',
                    position: 'insideTopRight',
                    fill: '#74819b',
                    fontSize: 9,
                  }}
                />
              ))}
            <Area
              type="linear"
              dataKey="ratio"
              name="Peer ratio"
              stroke={color}
              strokeWidth={2.3}
              fill="url(#performanceFill)"
              connectNulls={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="panel-foot">
        <span>30-day rolling mean · weekly samples · 100% = plant median</span>
        <SourceLink path="runs/plant_a/dashboard/index.html" />
      </div>
    </section>
  );
}

function PriorityList({ onSelect, compact = false }) {
  const rows = compact ? data.watchlist.slice(0, 4) : data.watchlist;
  return (
    <section className="panel priority-panel">
      <PanelHead eyebrow="MAINTENANCE WATCHLIST" title="Needs a closer look">
        <span className="count-chip">{data.watchlist.length} flagged</span>
      </PanelHead>
      <div className="priority-list">
        {rows.map((inv) => (
          <button
            className="priority-row"
            key={inv.inverter}
            onClick={() => onSelect(inv.inverter)}
          >
            <span className={`priority-icon ${inv.severity.toLowerCase()}`}>
              <Zap size={16} />
            </span>
            <span className="priority-info">
              <strong>{inv.inverter}</strong>
              <small>
                {inv.severity.toLowerCase()} ·{' '}
                {inv.hasTicket ? 'recent ticket' : 'no recent ticket'}
              </small>
            </span>
            <span className="priority-ratio">
              {Math.round(inv.ratio * 100)}
              <small>%</small>
              <span>peer output</span>
            </span>
            <ArrowRight size={15} />
          </button>
        ))}
      </div>
      <div className="panel-foot">
        <span>Mean peer ratio · last 60 days</span>
        <SourceLink path="runs/plant_a/watchlist.csv" />
      </div>
    </section>
  );
}

function AlarmDonut() {
  const pie = ['NUISANCE', 'TRIP', 'DERATE'].map((name) => ({
    name,
    value: m.alarmCounts[name],
  }));
  return (
    <section className="panel alarm-panel">
      <PanelHead
        eyebrow="ALARM INTELLIGENCE"
        title="Find the signal in the noise"
      >
        <BellRing className="muted" size={19} />
      </PanelHead>
      <div className="donut-layout">
        <div className="donut-chart">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pie}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={58}
                outerRadius={75}
                startAngle={90}
                endAngle={-270}
                paddingAngle={4}
                cornerRadius={5}
                stroke="none"
                isAnimationActive={false}
              >
                {pie.map((p) => (
                  <Cell key={p.name} fill={COLORS[p.name]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value, name) => [
                  `${value} incidents`,
                  name.toLowerCase(),
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="donut-center">
            <strong>
              {Math.round((m.alarmCounts.NUISANCE / m.alarmIncidents) * 100)}
              <span>%</span>
            </strong>
            <small>nuisance</small>
          </div>
        </div>
        <div className="donut-legend">
          {pie.map((p) => (
            <div key={p.name}>
              <span
                className="legend-dot"
                style={{ background: COLORS[p.name] }}
              />
              <span>
                {p.name === 'NUISANCE'
                  ? 'Nuisance'
                  : p.name === 'TRIP'
                    ? 'Full trip'
                    : 'Derating'}
              </span>
              <b>{p.value}</b>
              <small>{Math.round((p.value / m.alarmIncidents) * 100)}%</small>
            </div>
          ))}
        </div>
      </div>
      <div className="panel-foot">
        <span>9,211 raw alarms → {m.alarmIncidents} incidents · 2017–19</span>
        <SourceLink path="runs/plant_a/faults/FAULT_CLASSIFICATION.md" />
      </div>
    </section>
  );
}

function InverterMap({ selected, onSelect }) {
  const sections = Object.groupBy(
    data.plant.inverters,
    (inv) => inv.split('.')[1],
  );
  return (
    <section className="panel map-panel">
      <PanelHead
        eyebrow="PLANT A · 65 INVERTERS"
        title="A plant-wide perspective"
      >
        <span className="map-count">9 sections</span>
      </PanelHead>
      <div className="map-legend">
        <span>
          <i className="health low" />
          Below 80%
        </span>
        <span>
          <i className="health mid" />
          80–95%
        </span>
        <span>
          <i className="health good" />
          95–130%
        </span>
        <span>
          <i className="health high" />
          Above 130%
        </span>
        <span>
          <i className="health nodata" />
          No data
        </span>
      </div>
      <div className="inverter-map">
        {Object.entries(sections).map(([section, inverters]) => (
          <div className="inverter-section" key={section}>
            <span className="section-label">Section {section}</span>
            <div className="inverter-tiles">
              {inverters.map((inv) => {
                const ratio = data.plant.grid[inv];
                const health =
                  ratio === null
                    ? 'nodata'
                    : ratio < 0.8
                      ? 'low'
                      : ratio < 0.95
                        ? 'mid'
                        : ratio > 1.3
                          ? 'high'
                          : 'good';
                return (
                  <button
                    key={inv}
                    className={`inverter-tile ${health} ${inv === selected ? 'selected' : ''}`}
                    aria-pressed={inv === selected}
                    aria-label={`Inverter ${inv}, ${ratio === null ? 'no data' : Math.round(ratio * 100) + '% of peer output'}`}
                    title={`INV ${inv} · ${ratio === null ? 'No data' : (ratio * 100).toFixed(1) + '%'}`}
                    onClick={() => onSelect(inv)}
                  >
                    {inv.split('.')[2]}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <div className="map-note">
        <Activity size={14} />
        <span>
          Select an inverter to inspect its history. High ratios can reflect
          stale capacity records.
        </span>
      </div>
      <div className="panel-foot">
        <span>Mean peer ratio · last 90 days of the snapshot</span>
        <SourceLink path="runs/plant_a/dashboard/index.html" />
      </div>
    </section>
  );
}

function Findings() {
  return (
    <div className="findings-grid">
      <article className="insight-card">
        <div className="insight-icon">
          <ShieldCheck size={21} />
        </div>
        <span className="eyebrow">A MONITORING BLIND SPOT</span>
        <h3>The data saw what the alarms missed.</h3>
        <p>
          Error telemetry ends in November 2019 and never covered sections
          08/09. Performance analysis exposed the later collapse.
        </p>
        <SourceLink path="runs/plant_a/FINDINGS.md">
          Inspect the finding
        </SourceLink>
      </article>
      <article className="insight-card olive">
        <div className="insight-icon">
          <Leaf size={21} />
        </div>
        <span className="eyebrow">PLANT B · SOILING & SHADING</span>
        <h3>37 inverters. One recurring pattern.</h3>
        <p>
          Decline-and-recovery signals suggest soiling or seasonal shading. The
          clearest inverter shows 21 episodes over 8.5 years.
        </p>
        <SourceLink path="runs/plant_b/SOILING_FINDINGS.md">
          Explore the evidence
        </SourceLink>
      </article>
      <article className="insight-card dark">
        <div className="insight-icon">
          <FlaskConical size={21} />
        </div>
        <span className="eyebrow">BEYOND PEER COMPARISONS</span>
        <h3>Make the invisible loss visible.</h3>
        <p>
          A uniform 10% loss leaves relative performance unchanged. The absolute
          twin detects the drop against its own baseline.
        </p>
        <SourceLink path="runs/plant_a/twin/TWIN.md">
          See model validation
        </SourceLink>
      </article>
    </div>
  );
}

function EarlyWarnings() {
  const histogram = [
    { range: '1–14 days', low: 1, high: 14 },
    { range: '15–30 days', low: 15, high: 30 },
    { range: '31–45 days', low: 31, high: 45 },
    { range: '46–60 days', low: 46, high: 60 },
  ].map((b) => ({
    ...b,
    tickets: data.tickets.filter(
      (t) => t.leadDays !== null && t.leadDays >= b.low && t.leadDays <= b.high,
    ).length,
  }));
  const [onlyMissed, setOnlyMissed] = useState(false);
  const rows = data.tickets.filter((t) => !onlyMissed || t.leadDays === null);
  return (
    <>
      <div className="warning-summary">
        <div>
          <span className="eyebrow">VALIDATED AGAINST SERVICE TICKETS</span>
          <h2>
            Seven weeks to plan.
            <br />
            <span>Before a ticket was opened.</span>
          </h2>
          <p>
            42 of 46 inverter-specific service tickets had an earlier
            performance flag. This is historical recall; sparse tickets do not
            establish flag precision.
          </p>
        </div>
        <div
          className="recall-bars"
          aria-label="42 flagged tickets and 4 without an earlier flag"
        >
          <div className="recall-tiles">
            {data.tickets.map((t, i) => (
              <span
                key={i}
                className={t.leadDays === null ? 'missed' : ''}
                title={`${t.inverter}: ${t.leadDays === null ? 'No prior flag' : t.leadDays + ' days early'}`}
              />
            ))}
          </div>
          <span>
            <i className="legend-dot" />
            42 flagged early <i className="legend-dot missed" />4 without prior
            flag
          </span>
        </div>
      </div>
      <section className="panel">
        <PanelHead
          title="How early did the flags appear?"
          eyebrow="LEAD-TIME DISTRIBUTION"
        />
        <div className="standard-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={histogram}
              margin={{ top: 15, left: -20, right: 20 }}
            >
              <CartesianGrid vertical={false} stroke="#e9ece5" />
              <XAxis
                dataKey="range"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                allowDecimals={false}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <Tooltip content={<ChartTip />} />
              <Bar
                dataKey="tickets"
                name="Tickets"
                fill="#74967c"
                radius={[5, 5, 0, 0]}
                maxBarSize={110}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel-foot">
          <span>42 tickets with prior flags · median 51.5 days</span>
          <SourceLink path="runs/plant_a/ticket_leadtimes.csv" />
        </div>
      </section>
      <section className="panel">
        <PanelHead eyebrow="TICKET-LEVEL EVIDENCE" title="Behind the headline">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={onlyMissed}
              onChange={(e) => setOnlyMissed(e.target.checked)}
            />
            Show unflagged tickets
          </label>
        </PanelHead>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Inverter</th>
                <th>Ticket opened</th>
                <th>Category in source</th>
                <th>Prior warning</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t, i) => (
                <tr key={`${t.inverter}-${t.date}-${i}`}>
                  <td className="mono">{t.inverter}</td>
                  <td>{fullDate(t.date)}</td>
                  <td>{t.category === '--' ? 'Not recorded' : t.category}</td>
                  <td>
                    <span
                      className={`pill ${t.leadDays === null ? 'orange' : 'green'}`}
                    >
                      {t.leadDays === null
                        ? 'No prior flag'
                        : `${t.leadDays} days early`}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function Faults() {
  const names = {
    'grid-side': 'Grid-side / ENS',
    'power-stage': 'Power-stage',
    'dc-link': 'DC-link',
    insulation: 'Insulation',
    other: 'Other',
  };
  const families = data.families.map((f) => ({
    ...f,
    name: names[f.family] || f.family,
  }));
  return (
    <>
      <div className="two-column">
        <AlarmDonut />
        <article className="insight-card fault-insight">
          <span className="eyebrow">ENERGY IMPACT</span>
          <h2>Grid-side alarms are the ones to watch.</h2>
          <p>
            Undervoltage and ENS incidents account for approximately 1.35 MWh of
            the estimated 2.60 MWh lost during classified incidents.
          </p>
          <div className="impact-number">
            52<span>% of estimated incident losses</span>
          </div>
          <SourceLink path="runs/plant_a/faults/FAULT_CLASSIFICATION.md" />
        </article>
      </div>
      <section className="panel">
        <PanelHead
          eyebrow="CODE FAMILY × POWER IMPACT"
          title="What is actually stopping production?"
        />
        <div className="standard-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={families}
              margin={{ top: 20, left: -15, right: 20 }}
            >
              <CartesianGrid vertical={false} stroke="#e9ece5" />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <Tooltip content={<ChartTip />} />
              <Legend
                iconType="circle"
                iconSize={7}
                wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
              />
              {['TRIP', 'DERATE', 'NUISANCE'].map((k) => (
                <Bar
                  key={k}
                  name={
                    k === 'TRIP'
                      ? 'Full trip'
                      : k === 'DERATE'
                        ? 'Derating'
                        : 'Nuisance'
                  }
                  dataKey={k}
                  stackId="incidents"
                  fill={COLORS[k]}
                  maxBarSize={80}
                  isAnimationActive={false}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel-foot">
          <span>
            Trip: below 30% of baseline · derating: 30–90% · nuisance: above 90%
            or outside daylight
          </span>
          <SourceLink path="runs/plant_a/faults/incidents.csv" />
        </div>
      </section>
    </>
  );
}

function EnergyImpact() {
  const clean = data.capacityAudit.filter(
    (r) => r.classification === 'clean_register_candidate',
  );
  const historicalLoss = data.collapse.reduce((sum, r) => sum + r.lossEur, 0);
  return (
    <>
      <div className="soiling-stats">
        <Stat
          icon={TrendingDown}
          label="08/09 historical loss estimate"
          value={historicalLoss.toLocaleString('en-GB')}
          suffix="€"
          foot="14 inverters · since August 2025"
        />
        <Stat
          icon={Activity}
          label="Current annual loss estimate"
          value={data.currentLossEurPerYear.toLocaleString('en-GB')}
          suffix="€/yr"
          foot="Absolute twin · two degraded units"
        />
        <Stat
          icon={Grid2X2}
          label="Clean capacity-register candidates"
          value={clean.length}
          suffix="inverters"
          foot="Sustained peer-ratio audit · not field-verified"
        />
      </div>
      <section className="panel">
        <PanelHead
          eyebrow="SECTIONS 08/09 · HISTORICAL TARIFF ESTIMATES"
          title="Where the estimated losses accumulated"
        />
        <div className="standard-chart impact-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data.collapse}
              layout="vertical"
              margin={{ left: 15, right: 25 }}
            >
              <CartesianGrid horizontal={false} stroke="#e9ece5" />
              <XAxis
                type="number"
                tickFormatter={(v) => `€${v}`}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                type="category"
                dataKey="inverter"
                width={85}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10 }}
              />
              <Tooltip formatter={(v) => euro(v)} />
              <Bar
                name="Estimated loss since Aug 2025"
                dataKey="lossEur"
                fill="#ce9b7f"
                maxBarSize={18}
                radius={[0, 4, 4, 0]}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel-foot">
          <span>
            {euro(historicalLoss)} total from the committed collapse-cost CSV ·
            excludes future risk
          </span>
          <SourceLink path="runs/plant_a/collapse_cost.csv" />
        </div>
      </section>
      <div className="two-column">
        <article className="insight-card">
          <span className="eyebrow">HISTORICAL TICKETING GAP</span>
          <h3>
            {m.unticketedEpisodes} episodes had no inverter-specific ticket.
          </h3>
          <p>
            Only {m.episodes - m.unticketedEpisodes} of {m.episodes} material
            underperformance episodes were ticketed. Estimated unticketed loss
            totals {euro(m.unticketedLossEur)} over the 9.4-year record.
          </p>
          <SourceLink path="runs/plant_a/flag_episodes_material.csv" />
        </article>
        <article className="insight-card olive">
          <span className="eyebrow">
            FORWARD SCENARIO · FULL SECTION FAILURE
          </span>
          <h3>Approximately €29,000 a year at risk.</h3>
          <p>
            The absolute twin's scenario assumes all 14 inverters in sections
            08/09 fail completely. This is a modeled ceiling, separate from
            recorded historical loss or the current annual run rate.
          </p>
          <SourceLink path="runs/plant_a/twin/TWIN.md" />
        </article>
      </div>
      <section className="panel">
        <PanelHead
          eyebrow="MASTER-DATA AUDIT"
          title="When the capacity register needs a second look"
        />
        <p className="panel-description">
          Eight clean candidates, two operationally confounded units, and two
          watch cases. Implied capacities are audit estimates; confirm on site
          before changing the register.
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Inverter</th>
                <th>Registered capacity</th>
                <th>Implied capacity</th>
                <th>Audit classification</th>
              </tr>
            </thead>
            <tbody>
              {data.capacityAudit.map((r) => (
                <tr key={r.inverter}>
                  <td className="mono">{r.inverter}</td>
                  <td>{r.registeredKwp.toFixed(2)} kWp</td>
                  <td>{r.impliedKwp.toFixed(2)} kWp</td>
                  <td>
                    <span
                      className={`pill ${r.classification === 'clean_register_candidate' ? 'green' : 'orange'}`}
                    >
                      {r.classification === 'clean_register_candidate'
                        ? 'Clean candidate'
                        : r.classification === 'operationally_confounded'
                          ? 'Operationally confounded'
                          : 'Watch'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel-foot">
          <span>INV 01.05.030: 5.64 kWp registered vs 29.04 kWp implied</span>
          <SourceLink path="runs/plant_a/stale_kwp_audit.csv" />
        </div>
      </section>
    </>
  );
}

function Soiling() {
  const [orientation, setOrientation] = useState('all');
  const rows = data.soiling.filter(
    (r) =>
      r.episodes > 0 &&
      (orientation === 'all' || r.orientation === orientation),
  );
  return (
    <>
      <div className="soiling-stats">
        <Stat
          icon={Sun}
          label="Inverters with sawtooth patterns"
          value={m.soilingInverters}
          suffix={`/ ${m.plantBInverters}`}
          foot="Plant B · full historical analysis"
        />
        <Stat
          icon={Activity}
          label="Clearest repeated signal"
          value="21"
          suffix="episodes"
          foot="INV 05.08.106 · 8.5-year history"
        />
        <Stat
          icon={ArrowDownRight}
          label="Largest decline in headline case"
          value="16.46"
          suffix="%"
          foot="INV 05.08.106 · observed episode"
        />
      </div>
      <section className="panel">
        <PanelHead
          eyebrow="DECLINE & RECOVERY"
          title="Repeated patterns, ranked by inverter"
        >
          <label className="select-wrap">
            <span className="sr-only">Orientation</span>
            <select
              aria-label="Orientation"
              value={orientation}
              onChange={(e) => setOrientation(e.target.value)}
            >
              <option value="all">All orientations</option>
              <option value="W">West</option>
              <option value="O">East</option>
              <option value="M">Middle</option>
            </select>
            <ChevronDown size={14} />
          </label>
        </PanelHead>
        <div className="standard-chart soiling-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={rows.slice(0, 10)}
              layout="vertical"
              margin={{ left: 18, right: 25 }}
            >
              <CartesianGrid horizontal={false} stroke="#e9ece5" />
              <XAxis
                type="number"
                allowDecimals={false}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                type="category"
                dataKey="inverter"
                width={85}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <Tooltip content={<ChartTip />} />
              <Bar
                name="Episodes"
                dataKey="episodes"
                fill="#8ea578"
                radius={[0, 4, 4, 0]}
                maxBarSize={20}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel-foot">
          <span>
            {rows.length} inverters with signals in this orientation · highest
            10 shown
          </span>
          <SourceLink path="runs/plant_b/soiling_per_inverter.csv" />
        </div>
      </section>
      <div className="two-column">
        <article className="insight-card">
          <span className="eyebrow">HOW TO READ THE SIGNAL</span>
          <h3>A clue for field inspection.</h3>
          <p>
            The heuristic finds declines above 3% over at least 14 days,
            followed by recovery above 2% within 7 days. Seasonal vegetation
            shading can resemble soiling; these are candidate patterns, not
            confirmed causes.
          </p>
          <SourceLink path="runs/plant_b/SOILING_FINDINGS.md" />
        </article>
        <article className="insight-card olive">
          <span className="eyebrow">WINTER INTER-ROW SHADING</span>
          <h3>Season matters.</h3>
          <p>
            The findings report up to 25% winter shading for a typical interior
            row from November to February. Irradiance and field checks provide
            context for cleaning and vegetation decisions.
          </p>
          <SourceLink path="runs/plant_b/SOILING_FINDINGS.md" />
        </article>
      </div>
    </>
  );
}

function Validation() {
  const [days, setDays] = useState(91);
  const delayPoint = data.delay.reduce(
    (best, r) =>
      Math.abs(r.days - days) < Math.abs(best.days - days) ? r : best,
    data.delay[0],
  );
  return (
    <>
      <div className="two-column">
        <section className="panel">
          <PanelHead
            eyebrow="CONTROLLED VALIDATION"
            title="A uniform 10% loss"
          />
          <p className="panel-description">
            Synthetic loss applied to every inverter. The absolute model detects
            what peer comparisons cannot.
          </p>
          <div className="validation-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.uniformLoss.map((r) => ({
                  ...r,
                  name:
                    r.metric === 'relative_peer'
                      ? 'Relative peer ratio'
                      : 'Absolute twin index',
                }))}
                margin={{ top: 18, right: 20, left: -10 }}
              >
                <CartesianGrid vertical={false} stroke="#e9ece5" />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11 }}
                />
                <YAxis
                  domain={[0, 1.1]}
                  tickFormatter={(v) => v.toFixed(1)}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip formatter={(v) => Number(v).toFixed(4)} />
                <Legend
                  iconType="circle"
                  iconSize={7}
                  wrapperStyle={{ fontSize: 11 }}
                />
                <Bar
                  name="Before injected loss"
                  dataKey="before"
                  fill="#9fb09b"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={false}
                />
                <Bar
                  name="After −10% loss"
                  dataKey="after"
                  fill="#d39576"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={false}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="panel-foot">
            <span>Absolute index: 0.8998 → 0.8098</span>
            <SourceLink path="runs/plant_a/twin/twin_uniform_loss.csv" />
          </div>
        </section>
        <article className="insight-card dark model-card">
          <span className="eyebrow">PHYSICAL EXPECTED-OUTPUT MODEL</span>
          <h2>Grounded in healthy performance.</h2>
          <div className="model-number">
            0.957<span>R² · healthy daily energy</span>
          </div>
          <p>
            Calibrated per inverter on its healthy baseline, using irradiance
            and module temperature. Out-of-sample healthy-control MAPE: 7.2%.
          </p>
          <code>P = k · G · (1 + γ(T − 25))</code>
          <SourceLink path="runs/plant_a/twin/TWIN.md" />
        </article>
      </div>
      <section className="panel delay-panel">
        <PanelHead
          eyebrow="MODELED SCENARIO · SECTIONS 08/09"
          title="The cost of waiting"
        />
        <div className="delay-layout">
          <div>
            <p>
              Estimated cumulative loss on the currently degraded units, based
              on the committed cost-of-delay model.
            </p>
            <label htmlFor="repair-delay">
              Repair in <b>{delayPoint.days} days</b>
            </label>
            <input
              id="repair-delay"
              type="range"
              min={data.delay[0].days}
              max={data.delay.at(-1).days}
              step="7"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            />
            <div className="range-labels">
              <span>Repair now</span>
              <span>{data.delay.at(-1).days} days</span>
            </div>
          </div>
          <div className="delay-value">
            {euro(delayPoint.loss)}
            <span>estimated avoidable loss</span>
            <small>Tariff-based model · not realized revenue</small>
          </div>
        </div>
        <div className="panel-foot">
          <span>Discrete weekly estimates from the original model</span>
          <SourceLink path="runs/plant_a/twin/twin_cost_of_delay.csv" />
        </div>
      </section>
      <div className="method-note">
        <BookOpen size={20} />
        <div>
          <h3>Keep the limits in view</h3>
          <p>
            Historical replay on a single plant. Winter estimates are noisy, and
            sensor drift can resemble a plant-wide loss. Financial impact is
            estimated from energy and tariffs. Field checks remain necessary.
          </p>
        </div>
      </div>
    </>
  );
}

function EvidenceDialog({ onClose }) {
  const dialog = useRef(null);
  useEffect(() => {
    const el = dialog.current;
    el.showModal();
    return () => el.close();
  }, []);
  return (
    <dialog
      ref={dialog}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="evidence-dialog"
    >
      <div className="dialog-header">
        <div>
          <span className="eyebrow">THE EVIDENCE TRAIL</span>
          <h2>Real results, traceable sources.</h2>
        </div>
        <button
          className="icon-button"
          aria-label="Close evidence"
          onClick={onClose}
        >
          <X size={20} />
        </button>
      </div>
      <p>
        This dashboard uses a committed historical snapshot. Charts and totals
        are derived from the repository artifacts below; it does not connect to
        live telemetry.
      </p>
      <div className="source-list">
        {data.provenance.map((p) => (
          <a
            key={p.path}
            href={source(p.path)}
            target="_blank"
            rel="noreferrer"
          >
            <BookOpen size={16} />
            <span>
              {p.path.replace('runs/', '')}
              <small>SHA-256: {p.sha256.slice(0, 16)}…</small>
            </span>
            <ExternalLink size={14} />
          </a>
        ))}
      </div>
      <div className="dialog-caveat">
        <strong>Interpretation</strong>
        <p>
          Recall is measured against 46 tickets; precision is unmeasured. Loss
          estimates use tariffs. The 60-day watchlist and 90-day map use
          different windows. Soiling signals can also reflect shading, and the
          uniform-loss test is synthetic.
        </p>
      </div>
    </dialog>
  );
}

function downloadSnapshot() {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'plant-sentinel-results.json';
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function App() {
  const [tab, setTab] = useState('overview');
  const [selected, setSelected] = useState('01.08.053');
  const [period, setPeriod] = useState('18m');
  const [evidence, setEvidence] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const isB = tab === 'soiling';
  const selectInverter = (inv) => {
    setSelected(inv);
    if (tab !== 'inverters') setTab('inverters');
    requestAnimationFrame(() =>
      document
        .getElementById('performance')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
    );
  };
  const goTo = (id) => {
    setTab(id);
    setMobileMenu(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to results
      </a>
      <aside className={`sidebar ${mobileMenu ? 'open' : ''}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            goTo('overview');
          }}
        >
          <span className="brand-mark">
            <Zap size={23} fill="currentColor" />
          </span>
          <span>
            plant<span>sentinel</span>
            <small>SOLAR INTELLIGENCE</small>
          </span>
        </a>
        <div className="workspace-badge">
          <span className="workspace-mark">
            <Sun size={16} />
          </span>
          <div>
            Energy Hack Munich<small>Team Syz · 2026</small>
          </div>
        </div>
        <span className="nav-label">WORKSPACE</span>
        <nav aria-label="Results views">
          {tabs.map(({ id, name, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${tab === id ? 'active' : ''}`}
              onClick={() => goTo(id)}
              aria-current={tab === id ? 'page' : undefined}
            >
              <Icon size={18} />
              <span>{name}</span>
              {tab === id ? <span className="nav-active-dot" /> : null}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="snapshot-note">
            <span className="pulse-dot" />
            <span>
              Historical snapshot<small>Data through June 2026</small>
            </span>
          </div>
          <a className="repo-link" href={REPO} target="_blank" rel="noreferrer">
            <GitFork size={17} />
            View repository
            <ArrowUpRight size={15} />
          </a>
          <div className="team-credit">
            <div className="avatars">
              <span>OK</span>
              <span>MI</span>
            </div>
            <span>
              Built by Team Syz<small>Orkhan & Maxat</small>
            </span>
          </div>
        </div>
      </aside>
      {mobileMenu ? (
        <button
          className="sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setMobileMenu(false)}
        />
      ) : null}
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-only"
              aria-label="Toggle navigation"
              aria-expanded={mobileMenu}
              onClick={() => setMobileMenu(!mobileMenu)}
            >
              <Menu size={21} />
            </button>
            <span>Workspace</span>
            <span className="breadcrumb-slash">/</span>
            <strong>{tabs.find((t) => t.id === tab).name}</strong>
          </div>
          <div className="topbar-right">
            <span className="historical-pill">
              <span />
              Historical analysis
            </span>
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="icon-button"
              aria-label="GitHub repository"
            >
              <GitFork size={19} />
            </a>
          </div>
        </header>
        <main id="main">
          <div className="page-heading">
            <div>
              <div className="page-eyebrow">
                <span className="eyebrow-dot" />
                ENERPARC CHALLENGE · DIGITAL TWIN
              </div>
              <h1>{titleFor[tab]}</h1>
              <p>{descriptionFor[tab]}</p>
            </div>
            <button className="button outline" onClick={downloadSnapshot}>
              <Download size={15} />
              Export results
            </button>
          </div>
          <div className="scope-bar">
            <div>
              <span className="plant-icon">
                <Sun size={17} />
              </span>
              <strong>Plant {isB ? 'B' : 'A'}</strong>
              <span className="scope-divider" />
              <span>{isB ? '107' : '65'} inverters</span>
              <span className="scope-divider" />
              <span className="scope-period">
                <CalendarDays size={13} />
                {isB ? 'Jan 2018' : 'Dec 2016'} – Jun 2026
              </span>
            </div>
            <button onClick={() => setEvidence(true)}>
              <BookOpen size={14} />
              Data & methodology
              <ArrowUpRight size={14} />
            </button>
          </div>
          {tab === 'overview' || tab === 'warnings' ? (
            <div className="stats-grid">
              <Stat
                icon={ShieldCheck}
                label="Tickets flagged in advance"
                value={((m.earlyTickets / m.tickets) * 100).toFixed(1)}
                suffix="%"
                foot="Historical ticket recall"
                tag="42 / 46"
                tone="highlight"
              />
              <Stat
                icon={Activity}
                label="Median warning time"
                value={m.medianLeadDays}
                suffix="days"
                foot="Before a service ticket opened"
              />
              <Stat
                icon={Zap}
                label="Unticketed energy loss"
                value="64,247"
                suffix="€"
                foot="Tariff estimate · 9.4-year history"
              />
              <Stat
                icon={BellRing}
                label="Alarms without power impact"
                value={Math.round(
                  (m.alarmCounts.NUISANCE / m.alarmIncidents) * 100,
                )}
                suffix="%"
                foot="582 of 823 merged incidents"
              />
            </div>
          ) : null}
          {tab === 'overview' ? (
            <>
              <div className="overview-grid">
                <PerformanceChart
                  selected={selected}
                  setSelected={setSelected}
                  period={period}
                  setPeriod={setPeriod}
                />
                <PriorityList onSelect={selectInverter} compact />
              </div>
              <div className="lower-grid">
                <InverterMap selected={selected} onSelect={selectInverter} />
                <AlarmDonut />
              </div>
              <div className="section-title">
                <h2>What the numbers are telling us</h2>
                <span>From detection to decision</span>
              </div>
              <Findings />
            </>
          ) : null}
          {tab === 'inverters' ? (
            <>
              <PerformanceChart
                selected={selected}
                setSelected={setSelected}
                period={period}
                setPeriod={setPeriod}
              />
              <div className="lower-grid">
                <InverterMap selected={selected} onSelect={selectInverter} />
                <div>
                  <PriorityList onSelect={selectInverter} compact />
                  <div className="inverter-detail">
                    <span className="eyebrow">
                      SELECTED INVERTER · {selected}
                    </span>
                    <div>
                      <span>Last-90-day peer output</span>
                      <strong>
                        {data.plant.grid[selected] === null
                          ? 'No data'
                          : `${(data.plant.grid[selected] * 100).toFixed(1)}%`}
                      </strong>
                    </div>
                    <div>
                      <span>Recorded service tickets</span>
                      <strong>
                        {(data.plant.tickets[selected] || []).length}
                      </strong>
                    </div>
                    <div>
                      <span>Outage hours · last 365 days</span>
                      <strong>
                        {data.plant.outage[
                          selected
                        ]?.outage_h_last365d?.toLocaleString('en-GB') ??
                          'Not listed'}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : null}
          {tab === 'warnings' ? <EarlyWarnings /> : null}
          {tab === 'faults' ? <Faults /> : null}
          {tab === 'impact' ? <EnergyImpact /> : null}
          {tab === 'soiling' ? <Soiling /> : null}
          {tab === 'validation' ? <Validation /> : null}
          <footer className="page-footer">
            <span>
              <Leaf size={14} />
              Plant Sentinel · Energy Hack Munich 2026
            </span>
            <button onClick={() => setEvidence(true)}>
              Evidence, assumptions & limitations
              <ArrowUpRight size={13} />
            </button>
          </footer>
        </main>
      </div>
      {evidence ? <EvidenceDialog onClose={() => setEvidence(false)} /> : null}
    </div>
  );
}
