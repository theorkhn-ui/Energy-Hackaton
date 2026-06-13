# Team Syz: Submission Video (Remotion)

3:50 video for Energy Hack Munich 2026, Challenge #2.1 (Enerparc digital
twin). 1920×1080 @ 30 fps, 6900 frames, so the 4:00 hard cap is enforced by
construction. Storyboard: `../docs/VIDEO_STORYBOARD.md`.

Visual style: **Neo-Grid Bold** (paper/ink/neon-lemon editorial poster
system). Tokens and the scene-by-scene design map are in
`DESIGN_NOTES.md`. The speaker-split narration script is in
`../docs/VOICEOVER_TRANSCRIPT.md` and matches `src/Captions.tsx` word for
word.

## Quick start

```bash
cd video
npm install            # once
npx remotion studio    # live preview in the browser, scrub the timeline
```

Render the final MP4 (needs Chrome/Chromium on the machine; Remotion
downloads a headless one automatically on first render):

```bash
npx remotion render MainVideo out/video.mp4
```

Sanity-check a single frame without a full render:

```bash
npx remotion still MainVideo --frame=2200 --scale=0.5 out/still.png
```

Type-check after edits:

```bash
npm run typecheck
```

## Scene map

| # | Time | Frames | File |
|---|------|--------|------|
| 1 | 0:00-0:10 | 0-299 | `src/scenes/Scene1ColdOpen.tsx`: lead-time chart snaps in + 42/46 stat |
| 2 | 0:10-0:35 | 300-1049 | `src/scenes/Scene2Problem.tsx`: heatmap zoom-out, team badge |
| 3 | 0:35-1:10 | 1050-2099 | `src/scenes/Scene3Method.tsx`: native method animation (bars, cloud, curtailment trap) |
| 4 | 1:10-1:45 | 2100-3149 | `src/scenes/Scene4Leadtime.tsx`: full lollipop chart + stats |
| 5 | 1:45-2:15 | 3150-4049 | `src/scenes/Scene5InvisibleFault.tsx`: INV 01.03.018 flat line, 0 tickets, ~EUR500 |
| 6 | 2:15-2:50 | 4050-5099 | `src/scenes/Scene6ActiveCollapse.tsx`: sections 01.08/01.09, outage counter, fault matrix |
| 7 | 2:50-3:10 | 5100-5699 | `src/scenes/Scene7StaleRegister.tsx`: >1.1 ratio = stale kWp |
| 8 | 3:10-3:20 | 5700-5999 | `src/scenes/Scene8Limitation.tsx`: honest limitation, static |
| 9 | 3:20-3:50 | 6000-6899 | `src/scenes/Scene9Close.tsx`: team, roadmap, end card (held 3s) |

## What to tweak

- **Numbers / on-screen stats:** they are plain JSX text inside each scene
  file (search for the number, e.g. `500` or `51.5`). The narration text
  lives in ONE place: `src/Captions.tsx` (`SCENE_NARRATION`, verbatim from
  the storyboard).
- **Scene durations:** `src/timing.ts`, `SCENES[].durationSec`. Scenes,
  caption timing, and total length all recompute automatically. Keep the
  sum at ≤ 230 s.
- **Voiceover:** see `VoiceoverNote.md`. Drop `public/voiceover.mp3`, flip
  `HAS_VOICEOVER` in `src/timing.ts`.
- **Caption timings:** auto-distributed by word count inside each scene
  (`buildCaptions()` in `src/Captions.tsx`). After the voice is recorded,
  hand-time any lines that drift (instructions in `VoiceoverNote.md`).
- **Team photos (Scene 9):** REQUIRED: drop `orkhan.jpg` and `maxat.jpg`
  into `public/` before the final render. `Scene9Close.tsx` loads them via
  `staticFile()`; if a file is missing at render time the card automatically
  falls back to the bold initial block (`<Img onError>` flips the state), so
  the render never breaks, but the real photos look much better. Any
  portrait-ish crop works; the block is 380×420 with `object-fit: cover`.
- **Dashboard screen recordings** (storyboard "hybrid" recommendation):
  optional: drop an `.mp4` in `public/` and embed with `<OffthreadVideo>`
  inside Scene 2 or Scene 6.

## Assets (`public/`)

Copied from the analysis runs (re-copy if the charts are regenerated):

| File | Source | Used in |
|------|--------|---------|
| `leadtime_chart.png` | `runs/plant_a/viz/` | Scenes 1, 4 |
| `heatmap_monthly_ratio.png` | `runs/plant_a/` | Scenes 2, 7 |
| `money_chart.png` | `runs/plant_a/viz/` | Scene 5 |
| `section_collapse.png` | `runs/plant_a/viz/` | Scene 6 |
| `fault_matrix.png` | `runs/plant_a/faults/` | Scene 6 |
| `soiling_chart.png` | `runs/plant_b/` | unused (available if plant B gets a beat) |

Known gap: Scene 7 calls for a ">1.1-filtered" heatmap + ratio histogram, and
that export doesn't exist yet, so the scene zooms the full heatmap instead.
If the filtered export lands, drop it in `public/` and point
`Scene7StaleRegister.tsx` at it.

## Render spec (storyboard)

H.264 is set in `remotion.config.ts`. For the 10 to 12 Mbps bitrate target:

```bash
npx remotion render MainVideo out/video.mp4 --video-bitrate=11M
```

Final check before submitting: watch the export once **muted**. If the
story still works with captions only, we're safe (judging room may be loud).
