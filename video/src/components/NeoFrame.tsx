import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONT_MONO, GRID, label } from "../theme";

/**
 * Neo-Grid Bold universal frame: putty background, the 12x8 grid drawing in
 * as hairlines, an animated page-number tag bottom-left ("03 / 09") and a
 * 2x2 corner mark top-right whose squares pop in staggered. Every scene
 * wraps its content in this.
 */

const W = 1920;
const H = 1080;
const INNER_W = W - 2 * GRID.inset;
const INNER_H = H - 2 * GRID.inset;

type Props = {
  /** 1-based scene index for the page tag. */
  index: number;
  /** Mono kicker shown next to the page tag, e.g. "METHOD". */
  tag?: string;
  /** "paper" (default) or "ink" for dark scenes. */
  mode?: "paper" | "ink";
  /** Skip the grid-draw animation (already-busy scenes). */
  staticGrid?: boolean;
  children: React.ReactNode;
};

export const GridLines: React.FC<{ mode: "paper" | "ink"; draw: number }> = ({
  mode,
  draw,
}) => {
  const line = mode === "ink" ? COLORS.paper : COLORS.ink;
  const cols = Array.from({ length: GRID.cols - 1 }, (_, i) => i + 1);
  const rows = Array.from({ length: GRID.rows - 1 }, (_, i) => i + 1);
  return (
    <svg
      width={W}
      height={H}
      style={{ position: "absolute", inset: 0, opacity: 0.07 }}
    >
      {cols.map((c) => {
        const x = GRID.inset + (INNER_W / GRID.cols) * c;
        return (
          <line
            key={`c${c}`}
            x1={x}
            x2={x}
            y1={GRID.inset}
            y2={GRID.inset + INNER_H * draw}
            stroke={line}
            strokeWidth={1.5}
          />
        );
      })}
      {rows.map((r) => {
        const y = GRID.inset + (INNER_H / GRID.rows) * r;
        return (
          <line
            key={`r${r}`}
            x1={GRID.inset}
            x2={GRID.inset + INNER_W * draw}
            y1={y}
            y2={y}
            stroke={line}
            strokeWidth={1.5}
          />
        );
      })}
    </svg>
  );
};

/** 2x2 block stamp; squares pop in one after another. */
export const CornerMark: React.FC<{
  color?: string;
  size?: number;
  delay?: number;
}> = ({ color = COLORS.ink, size = 36, delay = 4 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sq = (size - 4) / 2;
  // Diagonal fill: top-left + bottom-right solid, top-right accent.
  const cells = [
    { x: 0, y: 0, fill: color },
    { x: sq + 4, y: 0, fill: COLORS.lemon },
    { x: 0, y: sq + 4, fill: "transparent" },
    { x: sq + 4, y: sq + 4, fill: color },
  ];
  return (
    <div style={{ position: "absolute", top: 22, right: 22, width: size, height: size }}>
      {cells.map((c, i) => {
        const pop = spring({
          frame: Math.max(0, frame - delay - i * 4),
          fps,
          config: { damping: 14, stiffness: 200, mass: 0.5 },
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: c.x,
              top: c.y,
              width: sq,
              height: sq,
              background: c.fill,
              transform: `scale(${pop})`,
            }}
          />
        );
      })}
    </div>
  );
};

export const NeoFrame: React.FC<Props> = ({
  index,
  tag,
  mode = "paper",
  staticGrid = false,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const draw = staticGrid
    ? 1
    : interpolate(frame, [0, 22], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  const tagIn = spring({
    frame: Math.max(0, frame - 6),
    fps,
    config: { damping: 200 },
  });

  const bg = mode === "ink" ? COLORS.stage : COLORS.bg;
  const tagBg = mode === "ink" ? COLORS.lemon : COLORS.ink;
  const tagFg = mode === "ink" ? COLORS.ink : COLORS.paper;

  return (
    <AbsoluteFill style={{ background: bg }}>
      <GridLines mode={mode} draw={draw} />
      {children}

      {/* Page-number tag, bottom-left, slides up from the frame edge. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          display: "flex",
          alignItems: "stretch",
          transform: `translateY(${(1 - tagIn) * 70}px)`,
        }}
      >
        <div
          style={{
            background: tagBg,
            color: tagFg,
            fontFamily: FONT_MONO,
            fontSize: 24,
            letterSpacing: "0.04em",
            padding: "14px 22px",
          }}
        >
          {String(index).padStart(2, "0")} / 09
        </div>
        {tag ? (
          <div
            style={{
              ...label(16),
              background: mode === "ink" ? COLORS.paper : COLORS.lemon,
              color: COLORS.ink,
              padding: "14px 22px",
              display: "flex",
              alignItems: "center",
            }}
          >
            {tag}
          </div>
        ) : null}
      </div>

      <CornerMark color={mode === "ink" ? COLORS.paper : COLORS.ink} />
    </AbsoluteFill>
  );
};
