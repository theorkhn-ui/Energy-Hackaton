# Plant Sentinel results explorer

A responsive React frontend for the Energy Hack Munich results. It presents the committed
analysis outputs as interactive charts, a 65-inverter map, a maintenance watchlist, ticket
validation, alarm triage, financial estimates, capacity audits, and Plant B soiling findings.

## Run locally

Requires Node.js 22.12 or newer. From this directory:

```bash
npm ci
npm run dev
```

Vite prints the local preview URL. This is a static historical results explorer; it does
not connect to live plant telemetry and requires no API keys or backend.

## Build and check

```bash
npm run data:check
npm run build
npm run preview

# Browser tests (install Chromium once if needed):
npx playwright install chromium
npm test
```

The production output is `dist/`. Serve it with any static host. Relative asset paths
allow deployment in a subdirectory. The optional Google Fonts stylesheet has a system-font
fallback if the browser is offline.

## Source data

`src/results.json` is a deterministic snapshot built from **12 committed artifacts** in
`../runs/`. Regenerate it inside a full repository checkout with `npm run data` (Python 3.9+).
`npm run data:check` verifies the snapshot, source hashes, and key measurements against those
artifacts. Raw challenge monitoring data is unnecessary for the frontend.

Evidence links use the source commit rather than a moving branch. Every chart names its
window and unit. The 60-day watchlist differs from the 90-day plant map. Null chart points
remain gaps, and missing values are not converted to zero. Financial amounts are tariff-based
estimates; future section-failure risk and synthetic validation are labeled separately.
Ticket recall is measurable, but sparse tickets do not establish flag precision.

## Interactions

- Select an inverter on the map or maintenance list to inspect its history.
- Compare 18 months with the complete available history.
- Show the four tickets without an earlier performance flag.
- Filter Plant B soiling patterns by orientation.
- Explore the original model's weekly cost-of-delay estimates.
- Open the evidence dialog or export the source-backed JSON snapshot.

React, Recharts, Lucide, and Vite power the interface. 21st.dev MCP was unavailable in the
authoring session, so no components were generated through that service.
