# Voiceover script — Team Syz submission video

Read-aloud script for the narration, split line by line between **Orkhan** and
**Maxat**. The wording is word-for-word identical to the burned-in subtitles in
`src/Captions.tsx`, so the voice and the on-screen captions stay in sync.

- **Total runtime:** 3:50 (230 s) at 30 fps, 1920×1080.
- **Speakers alternate at scene boundaries.** Scene 9 is shared.
- **Delivery:** read it like you are explaining it to a friend, not presenting.
  Short pause at each period. The captions auto-pace by word count, so don't
  rush — every scene has a little slack at the end.
- **Numbers stay exact:** 42/46, 51.5 days, ~€500/yr (INV 01.03.018),
  €42k/yr at risk, 9.4 years, 65 inverters, 71% nuisance, telemetry dead
  since 2019.

Legend: 🟦 **ORKHAN**  ·  🟧 **MAXAT**

---

## Scene 1 — Cold open (0:00–0:10) · 🟦 ORKHAN

> Forty two of the last forty six inverter failures here were visible in the
> data first.
>
> A median of fifty one and a half days before anyone opened a ticket.

---

## Scene 2 — The problem (0:10–0:35) · 🟧 MAXAT

> This is nine point four years of real monitoring data from a solar plant
> with sixty five inverters.
>
> A reading every five minutes, from every inverter.
>
> Hidden inside it are failures the plant's own monitoring never caught.
>
> We are team Syz. For Enerparc's digital twin challenge, we built the layer
> that catches them.

---

## Scene 3 — The method (0:35–1:10) · 🟦 ORKHAN

> Our method is simple on purpose.
>
> Every five minutes, we compare each inverter to the plant median.
>
> What is left is a peer ratio. One point zero means healthy.
>
> This one just dropped to zero point five five. Below one point zero means
> trouble.
>
> Clouds and seasons hit every inverter at once, so they cancel out.
>
> One trap though. Grid curtailment looks exactly like a fault.
>
> So we filter the EVU and DV signals out, or we would flag healthy inverters
> all day.

---

## Scene 4 — Finding 1: it works (1:10–1:45) · 🟧 MAXAT

> Does it actually work? We back tested it against the plant's real service
> history.
>
> Of forty six inverter specific tickets, things like broken capacitors,
> boards and insulation faults,
>
> forty two were flagged by our method in advance.
>
> The median lead time was fifty one and a half days.
>
> That is seven weeks of warning.
>
> Seven weeks to order the part, schedule the crew, and fix it on your terms
> instead of the inverter's.

---

## Scene 5 — Finding 2: the invisible fault (1:45–2:15) · 🟦 ORKHAN

> Sometimes there is no ticket at all.
>
> Inverter zero one, zero three, zero one eight has been running at seventy
> percent of its peers for a full year.
>
> No service ticket exists. Nobody noticed.
>
> That is roughly five hundred euros a year, gone, from one inverter.
>
> Our flag caught it from the data alone.

---

## Scene 6 — Finding 3: failure in progress (2:15–2:50) · 🟧 MAXAT

> This one is not history. It is happening right now.
>
> Sections one zero eight and one zero nine started collapsing in August
> twenty twenty five.
>
> Two inverters are still below seventy percent of their peers.
>
> The worst unit lost around eight hundred forty hours in the last year.
>
> In total, about forty two thousand euros of yearly revenue is at risk.
>
> And no alarm fired, because the plant's error telemetry has been dead since
> twenty nineteen.
>
> If we were on call, this would be ticket number one, written today.

---

## Scene 7 — Bonus findings (2:50–3:10) · 🟦 ORKHAN

> Two bonus findings.
>
> About eight inverters sit permanently above a ratio of one point one.
>
> That is not better hardware. That is a stale kilowatt peak value in the
> asset register.
>
> We also sorted the old alarms. Seventy one percent of them were nuisance.

---

## Scene 8 — The limit, and how we close it (3:10–3:29) · 🟧 MAXAT

> One honest limit, and how we close it.
>
> Our peer ratio is relative, so a loss that hits every inverter equally could
> slip through.
>
> So we also built an absolute twin. Each inverter against its own healthy
> baseline, from irradiance and temperature.
>
> We tested it. We dimmed every inverter by ten percent. The peer ratio never
> moved. The twin caught all of it.

---

## Scene 9 — Close (3:29–3:59) · 🟦 ORKHAN → 🟧 MAXAT

**🟦 ORKHAN:**

> We are Orkhan and Maxat, team Syz.
>
> In one day, with your data, we found a failure in progress, a fault nobody
> had noticed, and a seven week warning signal checked against your own
> tickets.

**🟧 MAXAT:**

> Next, we want to wire this into live monitoring, finish the root cause work,
> and auto draft the service tickets.
>
> Less downtime, caught earlier, with math your engineers can check line by
> line.
>
> Thanks for watching.

---

### Speaker balance

| Speaker | Scenes | Approx. words |
|---|---|---|
| 🟦 Orkhan | 1, 3, 5, 7, 9a | ~246 |
| 🟧 Maxat  | 2, 4, 6, 8, 9b | ~274 |
