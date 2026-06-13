# Design notes: Neo-Grid Bold

The video is restyled to the **Neo-Grid Bold** design system from
[`zarazhangrui/beautiful-html-templates`](https://github.com/zarazhangrui/beautiful-html-templates/tree/main/templates/neo-grid-bold)
(referenced by the `zarazhangrui/frontend-slides` bold template pack). Source
of truth: that template's `design.md`. All tokens live in `src/theme.ts`.

## Adopted tokens

### Palette
| Token | Value | Role |
|---|---|---|
| `paper` | `#F5F4EF` | Warm ecru. Default panel fill. |
| `bg` | `#ECECE8` | Putty ecru. Slide background behind the 40px frame. |
| `ink` | `#0A0A0A` | Near-black. Text, inverted panels, all rules. |
| `lemon` | `#E6FF3D` | Electric neon-yellow. The single accent. Fill only, never text. |
| `muted` | `#8A8A85` | Graphite. Rare, de-emphasized only (Scene 3 cloud). |
| `stage` | `#1A1A1A` | Stage black. Cold open, end card, photo blocks. |

### Typography
- **Space Grotesk 700, strict uppercase, negative tracking** for every
  display moment, title, chip value, and stat numeral (loaded via
  `@remotion/google-fonts/SpaceGrotesk`).
- **Space Grotesk 400 mixed case** for body copy and captions.
- **JetBrains Mono 400 uppercase, +0.08em tracking** for every label, page
  tag, axis tag, and metadata string.
- Scale (px): 320 / 240 / 156 / 132 / 96 / 88 / 56 / 44 / 30 / 28 / 24 / 22 /
  16 / 14. Oversized numerals (150-290px) carry the stats in Scenes 1, 3, 4,
  5, 6, 7.

### Grid and layout
- Universal frame: 40px inset, 12-column x 8-row grid, 12px gaps. Rendered as
  animated hairlines (7% ink) that draw in at the start of every scene
  (`NeoFrame` / `GridLines`).
- Zero border radius everywhere. Strict rectangles.
- No gradients, no blur shadows on panels. Depth = color adjacency
  (paper / ink / lemon panels trading roles).
- 1.5px ink borders on chips/pills, 2-3px ink wireframes on chart frames and
  baselines (template: table/axis weights).

### Accent devices
- **Page-number tag** bottom-left on every scene: `03 / 09` in JetBrains
  Mono, plus a lemon kicker block naming the scene.
- **Corner mark** top-right: 2x2 block stamp, squares pop in staggered.
- **`<mark>`-style lemon swatch** inside headlines ("Below **1.0** =
  trouble", "Team **Syz**").
- **Blocky stat chips** (`StatPill`): zero-radius rectangles, mono kicker +
  Space Grotesk 700 value, lemon / ink / paper / fault variants.
- **Bold drawn highlights** over chart PNGs: 7px rectangles/ellipses that
  draw themselves around the key region (`ChartBlock` `highlights`).

## Documented deviations from the template

1. **Fault red (`#E5484D`).** The template allows exactly one chromatic
   accent (lemon) and says yellow carries no semantic meaning. This video's
   story depends on "red = fault" data marks (the dipping bar, the 0.70
   line, the ACTIVE tag, highlight boxes on failure regions). Red is used
   strictly as a *data* color, never decoration; lemon stays the only
   editorial accent.
2. **Hard offset shadows on chips.** The template forbids `box-shadow`
   blur. The chips use a *solid* offset ink block (`8px 8px 0 0`), a
   neo-brutalist hard shadow, to make stats pop against busy chart PNGs at
   video scale. No blur anywhere.
3. **Motion.** The template is a static slide system; all entrance
   choreography (grid lines drawing in, panel slams, spring chips, masked
   chart wipes, drawn highlight outlines, the Scene 3 freeze beat) is our
   translation of the system into time, using Remotion `spring()` and
   `interpolate()` only (no CSS animations).
4. **Captions.** Burned-in caption bar = ink band + lemon edge block,
   Space Grotesk 500 mixed case (template has no caption concept).

## Scene-by-scene design map

| # | Frame mode | Key Neo-Grid devices |
|---|---|---|
| 1 | stage ink | 220px `42/46` numeral, lemon chip, chart wipe-in |
| 2 | paper | heatmap wipe + zoom-out, fault rect draws on failure streaks, ink team panel |
| 3 | paper | native bar field (ink bars), ink formula banner, **freeze beat: dim + pulsing red bar + 290px `0.55` + "below 1.0 = trouble" tag, held 4+ s** |
| 4 | paper | chart wipe, ink highlight rect, 170px `42/46`, lemon "7 weeks" panel |
| 5 | paper | SVG ratio line in ink-framed panel, typed ticket search, money chart + ellipse highlight, 150px `~€500` |
| 6 | paper | chart wipe + fault rect, pulsing ACTIVE tag, 840h count-up numeral, lemon `€42k/yr` chip, dead-telemetry ink chip, fault-matrix ink panel |
| 7 | paper | zoomed heatmap + ink rect on the >1.1 band, 170px `~8`, 71% nuisance chip |
| 8 | paper | frozen dimmed method diagram, single ink panel with lemon mark |
| 9 | paper → stage ink | photo blocks (ink frame + lemon backing plate), numbered roadmap blocks, end card with lemon `SYZ` mark |
