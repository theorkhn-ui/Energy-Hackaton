import type React from "react";
import { loadFont as loadGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

/**
 * Neo-Grid Bold design tokens (zarazhangrui/beautiful-html-templates →
 * templates/neo-grid-bold). Heavy editorial poster system: 12x8 grid,
 * paper-ecru / ink-black / neon-lemon panels, Space Grotesk 700 uppercase
 * display, JetBrains Mono uppercase labels, zero border radius, no gradients.
 * See video/DESIGN_NOTES.md for what was adopted and the two documented
 * deviations (functional fault-red, hard offset shadows on chips).
 */

const grotesk = loadGrotesk("normal", { weights: ["400", "500", "700"] });
const mono = loadMono("normal", { weights: ["400", "500"] });

export const COLORS = {
  /** Warm ecru off-white. Default panel fill. */
  paper: "#F5F4EF",
  /** Putty ecru. Slide background behind the 40px inset frame. */
  bg: "#ECECE8",
  /** Structural near-black: text, inverted panels, all rules. */
  ink: "#0A0A0A",
  /** Electric neon-yellow. The single chromatic accent. Fill only, never text. */
  lemon: "#E6FF3D",
  /** Reserved graphite, used sparingly for de-emphasized text. */
  muted: "#8A8A85",
  /** Deep stage black (cold open, end card, photo regions). */
  stage: "#1A1A1A",
  /**
   * DEVIATION from the template: a functional data color for faults.
   * The video's story is "red = fault"; the judges read charts, not posters.
   * Used ONLY on fault data marks (bars, lines, ACTIVE tag), never as decor.
   */
  fault: "#E5484D",
} as const;

export const FONT = `"${grotesk.fontFamily}", "Helvetica Neue", Helvetica, Arial, sans-serif`;
export const FONT_MONO = `"${mono.fontFamily}", ui-monospace, "Cascadia Mono", Consolas, monospace`;

/** Neo-Grid Bold type scale (px, fixed 1920x1080 canvas). */
export const TYPE = {
  sectionNum: 320,
  statNumLg: 240,
  statNum: 156,
  display: 132,
  statNumSm: 96,
  title: 88,
  subtitle: 56,
  cardHeadline: 44,
  cardH3: 30,
  body: 28,
  label: 24,
  bodySm: 22,
  labelSm: 16,
  labelXs: 14,
} as const;

/** Universal frame: 40px inset, 12-col x 8-row, 12px gaps. */
export const GRID = {
  inset: 40,
  cols: 12,
  rows: 8,
  gap: 12,
} as const;

/** Display text style helper: Space Grotesk 700, uppercase, tight tracking. */
export const display = (size: number): React.CSSProperties => ({
  fontFamily: FONT,
  fontWeight: 700,
  fontSize: size,
  lineHeight: 0.95,
  letterSpacing: size >= 200 ? "-0.04em" : size >= 100 ? "-0.02em" : "-0.01em",
  textTransform: "uppercase",
});

/** Mono label style helper: JetBrains Mono, uppercase, wide tracking. */
export const label = (size: number): React.CSSProperties => ({
  fontFamily: FONT_MONO,
  fontWeight: 400,
  fontSize: size,
  letterSpacing: size <= 16 ? "0.12em" : "0.08em",
  textTransform: "uppercase",
});
