/**
 * Color language per storyboard: red = fault, green/neutral = healthy,
 * consistent across ALL scenes. Dark engineering-dashboard look.
 */
export const COLORS = {
  bg: "#0b1220",
  bgPanel: "#121c31",
  bgPanelBorder: "#24314f",
  text: "#f5f7fa",
  textDim: "#9aa7bd",
  healthy: "#30a46c",
  fault: "#e5484d",
  warn: "#ffb224",
  accent: "#4cc2ff",
  captionBg: "rgba(0, 0, 0, 0.6)",
} as const;

export const FONT = `"Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif`;
export const FONT_MONO = `"JetBrains Mono", "SF Mono", "Cascadia Mono", Consolas, monospace`;
