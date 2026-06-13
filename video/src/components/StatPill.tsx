import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT, FONT_MONO } from "../theme";

export type ChipVariant = "lemon" | "ink" | "paper" | "fault";

type Props = {
  /** Frame (relative to parent sequence) at which the chip slams in. */
  delay: number;
  variant?: ChipVariant;
  big?: boolean;
  /** Small mono kicker above the value. */
  kicker?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
};

const fills: Record<ChipVariant, { bg: string; fg: string; border: string }> = {
  lemon: { bg: COLORS.lemon, fg: COLORS.ink, border: COLORS.ink },
  ink: { bg: COLORS.ink, fg: COLORS.paper, border: COLORS.ink },
  paper: { bg: COLORS.paper, fg: COLORS.ink, border: COLORS.ink },
  fault: { bg: COLORS.fault, fg: COLORS.paper, border: COLORS.ink },
};

/**
 * Neo-Grid Bold stat chip: blocky zero-radius rectangle, Space Grotesk 700
 * uppercase, 1.5px ink border, hard offset ink shadow (a solid block, not a
 * blur — see DESIGN_NOTES.md deviations). Springs in with overshoot.
 */
export const StatPill: React.FC<Props> = ({
  delay,
  variant = "lemon",
  big = false,
  kicker,
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 13, stiffness: 160, mass: 0.6 },
  });

  const opacity = interpolate(frame - delay, [0, 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const c = fills[variant];
  const shadow = 8 * pop;

  return (
    <div
      style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "flex-start",
        background: c.bg,
        color: c.fg,
        border: `1.5px solid ${c.border}`,
        boxShadow: `${shadow}px ${shadow}px 0 0 ${COLORS.ink}`,
        padding: big ? "18px 34px" : "12px 26px",
        opacity,
        transform: `scale(${0.8 + 0.2 * pop}) translateY(${(1 - pop) * 30}px)`,
        ...style,
      }}
    >
      {kicker ? (
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: big ? 20 : 16,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            opacity: 0.75,
            marginBottom: 4,
          }}
        >
          {kicker}
        </div>
      ) : null}
      <div
        style={{
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: big ? 52 : 34,
          lineHeight: 1.0,
          letterSpacing: "-0.01em",
          textTransform: "uppercase",
          whiteSpace: "nowrap",
        }}
      >
        {children}
      </div>
    </div>
  );
};
