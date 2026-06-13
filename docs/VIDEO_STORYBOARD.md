# Video Storyboard: Energy Hack Munich 2026

**Team Syz** (Orkhan + Maxat) · Challenge #2.1 Enerparc: Digital Twin of a Solar Plant
**Format:** 4-minute video, HARD CAP (judges stop at 4:00) · **Planned runtime: 3:50** (10s safety buffer)
**Audience:** Enerparc engineers, technical, skeptical, allergic to hype. Lead with evidence, stay honest.
**Pacing:** ~140 words/minute narration. Word counts per scene are calibrated to the time slot.

---

## Scene-by-Scene Breakdown

| # | Time | Dur | Scene | Visual | Narration (word-for-word) | On-Screen Text Overlays |
|---|------|-----|-------|--------|---------------------------|------------------------|
| 1 | 0:00-0:10 | 10s | **Cold open: the hook** | Black screen, then lead-time lollipop chart snaps in, one lollipop at a time, fast. No logo, no title, straight to the stat. | "Forty-two of the last forty-six inverter failures at this solar plant were visible in the data, a median of fifty-one days before anyone opened a ticket." | **42 / 46 failures predicted** · **51.5 days median lead time** |
| 2 | 0:10-0:35 | 25s | **The problem** | Monthly heatmap (65 inverters × 113 months) slowly zooming out, red failure streaks become visible against the green. End frame: team name + challenge title appear small in corner. | "This is nine point four years of real monitoring data from a sixty-five-inverter PV plant. A reading every five minutes, from every inverter. And hidden inside it: failures the operator's own monitoring never caught. We're team Syz, and for Enerparc's digital twin challenge, we built the layer that catches them." | 9.4 years · 65 inverters · 5-min resolution, then "Team Syz, Challenge #2.1: Digital Twin of a Solar Plant" |
| 3 | 0:35-1:10 | 35s | **Method (no math jargon)** | Simple animated diagram: 65 small inverter bars, plant median line drawn across them, one bar dips below and turns red. Then a cloud icon passes over ALL bars at once, all dip together, ratio stays flat (visual proof of cancellation). Final beat: "EVU/DV curtailment" rows get crossed out. | "Our method is deliberately simple. Every five minutes, we compare each inverter to the plant median at that exact moment. Clouds, seasons, soiling rain, they hit every inverter at once, so they cancel out. What's left is a clean peer ratio: one point zero means healthy, anything below means trouble. One trap, though: grid curtailment looks exactly like a fault. We filter the EVU and DV curtailment signals out explicitly. Skip that step, and you'll flag perfectly healthy inverters all day." | **Peer ratio = inverter ÷ plant median (same timestamp)** · Weather cancels out · ⚠ Curtailment (EVU/DV) excluded, the trap |
| 4 | 1:10-1:45 | 35s | **Finding 1: predictive power** | Lead-time lollipop chart, full version: 46 tickets on a timeline, flags shown landing before each ticket. Highlight the median marker. Ticket category labels fade in (capacitors / boards / insulation). | "But does it actually work? We back-tested against the plant's real service history. Of forty-six inverter-specific tickets, defective capacitors, defective boards, insulation faults, forty-two were preceded by our performance flag. Median lead time: fifty-one and a half days. That's seven weeks of warning. Seven weeks to order the part, schedule the crew, and fix it on your terms instead of the inverter's." | **42 of 46 tickets flagged in advance** · Median lead: **51.5 days** · capacitors · boards · insulation faults |
| 5 | 1:45-2:15 | 30s | **Finding 2: the invisible fault** | Single-inverter ratio line for INV 01.03.018: flat at ~0.70 for 12 months. A search animation over the ticket log returns "0 results". Then the money bar chart: €432/yr highlighted. | "And sometimes there is no ticket at all. Inverter zero-one, zero-three, zero-one-eight has been running at seventy percent of its peers for a full year. No service ticket exists. Nobody noticed. That's roughly four hundred and thirty euros a year quietly evaporating, from a single inverter. Our flag caught it from the data alone." | **INV 01.03.018, peer ratio 0.70 for 12 months** · Service tickets found: **0** · **≈ €432 / year lost** |
| 6 | 2:15-2:50 | 35s | **Finding 3: failure in progress** | Section-collapse line chart: sections 01.08 + 01.09 ratio lines bending down from Aug 2025 to now. Zoom to the worst inverters at 0.35 to 0.50. Outage-hours counter ticks up to ~800. | "This one isn't history, it's happening right now. Sections one-oh-eight and one-oh-nine started collapsing in August twenty twenty-five. Today, several inverters there are producing at just thirty-five to fifty percent of their peers, each with roughly seven hundred fifty to eight hundred forty outage hours in the last twelve months. We're classifying the error codes to pin down the root cause. If we were on call, this would be ticket number one, written today." | **ACTIVE: sections 01.08 + 01.09** · collapsing since **Aug 2025** · inverters at **35-50% of peers** · **~740-840 outage hrs / 365d each** |
| 7 | 2:50-3:10 | 20s | **Bonus: stale asset register** | Heatmap filtered to the ~8 permanently-dark-blue (>1.1) inverters, ratio histogram beside it with the >1.1 tail highlighted. | "One bonus finding: about eight inverters sit permanently above a ratio of one point one. That's not overperformance, that's a stale kilowatt-peak value in the asset register. Fix the master data, and every yield calculation on this plant gets sharper." | **~8 inverters > 1.1 ratio**, **stale kWp register, not magic panels** |
| 8 | 3:10-3:20 | 10s | **Honest limitation** | Calm, static frame: the method diagram from Scene 3, dimmed, with one caption line. No animation, let the sentence land. | "To be fully honest about the limits: because we measure inverters against each other, a plant-wide degradation that hits every inverter equally would be invisible to this method." | Known limit: **relative method, plant-wide degradation needs an absolute baseline** |
| 9 | 3:20-3:50 | 30s | **Close: team + next steps** | Split screen: Orkhan + Maxat (photos or short clips), then a 3-item roadmap animating in. End card: Team Syz · contact · challenge #2.1. Hold end card 3s. | "We're Orkhan and Maxat, team Syz. In one weekend, with your data, we found one failure in progress, one failure nobody had noticed, and a seven-week early-warning signal validated against your own ticket history. With Enerparc, our next steps are clear: wire this into live monitoring, finish error-code root-cause classification, and auto-draft the service tickets. Less downtime, caught earlier, with math your engineers can audit line by line. Thanks for watching." | **Team Syz, Orkhan + Maxat** · Next: ① live monitoring integration ② error-code root-cause ③ auto-drafted tickets |

**Runtime check:** 10 + 25 + 35 + 35 + 30 + 35 + 20 + 10 + 30 = **230s = 3:50** ✓ (10s buffer before the 4:00 hard cap)
**Word-count check:** ~540 narration words / 3.83 min ≈ 141 wpm ✓

---

## Narration Delivery Notes

- One narrator throughout (pick whoever sounds more natural in English); the other appears in Scene 9. Or split 50/50 at Scene 5, both are fine, but don't alternate every scene.
- Record narration FIRST, then cut visuals to the audio. Timing the voice to pre-rendered video is much harder than the reverse.
- Numbers are written out in the narration the way they should be spoken ("fifty-one and a half days"). Don't read digits.
- Scene 8 (limitation): slow down, drop the energy slightly. A sincerity beat. Engineers will respect it more than any claim in the video.
- If a take runs long, cut from Scene 2 (problem) first, never from Scenes 4 to 6 (the evidence).

---

## Production Notes

### Remotion vs. screen capture (team has remotion-best-practices skill installed)

| Aspect | Remotion | Screen capture (OBS + matplotlib/dash) |
|---|---|---|
| Chart animations (Scenes 1, 3-7) | Frame-perfect, declarative, easy to retime when narration changes | Re-record everything on any timing change |
| Real-data charts | Must port chart data into React (export CSV/JSON, render with d3 or recharts) | Already exists, record the notebook/dashboard as-is |
| Captions burned in | Trivial, captions are just components, perfectly synced | Needs a video editor pass afterwards |
| Time cost for 2 people | Higher upfront, near-zero iteration cost | Low upfront, expensive iteration |
| Credibility with engineer judges | Polished, but can look "produced" | Raw dashboard footage reads as "this is real and it runs" |

**Recommendation, hybrid:**
- **Remotion** for the skeleton: cold open, method animation (Scene 3), all stat overlays, captions, transitions, end card. This is where the skill pays off and where timing precision against the 4:00 cap matters.
- **Screen capture** embedded inside Remotion (`<OffthreadVideo>`) for 1 to 2 short clips of the actual dashboard/notebook scrolling (best spots: Scene 2 heatmap, Scene 6 live section view). Real-tool footage signals "this works today", which lands well with operator judges.
- Build the Remotion composition at exactly 230s × 30fps = 6,900 frames; the hard cap is then enforced by construction.

### Technical spec

- **Resolution:** 1920×1080, 30 fps, H.264, target bitrate 10 to 12 Mbps.
- **Captions: burned in, always on.** Judges may watch muted in a noisy judging room. Use the narration text verbatim, max 2 lines, bottom-center, high-contrast (white on 60%-opacity dark band). In Remotion: render captions as a component driven by the same timing constants as the scenes.
- **Stat overlays are not captions:** overlays (the third column above) are large, persistent, and positioned near the relevant chart element; captions are the spoken text. Both must coexist without overlap, so keep overlays in the upper two-thirds.
- **Chart legibility at 1080p:** minimum ~28px font for axis labels, thicken line strokes to 3 to 4px. Re-export matplotlib figures at figsize/dpi that match, or rebuild key charts natively in Remotion.
- **Audio:** record narration in a quiet room, phone mic in a closet beats laptop mic in a hall. Normalize to -16 LUFS. Light background music at -28 dB or none. Judges are engineers, not a festival audience.
- **Color language:** red = fault, green/neutral = healthy, consistently across ALL charts. The heatmap already follows this; keep the lollipop and line charts consistent.
- **End card** holds the final 3 seconds with team name + contact, so a paused last frame is still useful.

### Asset checklist

- [ ] Monthly heatmap (inverter × month, 9.4 yrs), export hi-res plus a filtered >1.1 version for Scene 7
- [ ] Lead-time lollipop chart, short version (Scene 1) plus full annotated version (Scene 4)
- [ ] Section-collapse line chart for 01.08 + 01.09 (Scene 6)
- [ ] Money bar chart with €432/yr highlight (Scene 5)
- [ ] INV 01.03.018 single-inverter ratio line, 12 months (Scene 5)
- [ ] Method explainer animation (Scene 3), build in Remotion
- [ ] 1 to 2 dashboard/notebook screen recordings, 10 to 15s each, 1080p, cursor hidden
- [ ] Team photos or 3 to 5s clips (Scene 9)
- [ ] Narration recording (~540 words, single take per scene is fine)
- [ ] If error-code classification lands before the deadline: add the root cause as one overlay line in Scene 6, do NOT add runtime

### Risk buffers

- The 10s buffer is for encoding drift and a breath at the end, so do not script content into it.
- Dry-run the final export and watch it muted once: if the story still works with captions only, you're safe.
