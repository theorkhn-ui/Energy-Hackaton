import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT } from "../theme";

type Props = {
  /** Frame (relative to parent sequence) at which the pill pops in. */
  delay: number;
  color?: string;
  big?: boolean;
  children: React.ReactNode;
  style?: React.CSSProperties;
};

/**
 * Animated stat reveal: spring() pop with a slight overshoot, opacity gated
 * so nothing is visible before `delay`. Stat overlays live in the upper
 * two-thirds of the frame so they never collide with captions (storyboard
 * spec).
 */
export const StatPill: React.FC<Props> = ({
  delay,
  color = COLORS.accent,
  big = false,
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 14, stiffness: 130, mass: 0.7 },
  });

  const opacity = interpolate(frame - delay, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 16,
        background: COLORS.bgPanel,
        border: `1px solid ${COLORS.bgPanelBorder}`,
        borderLeft: `8px solid ${color}`,
        borderRadius: 12,
        padding: big ? "18px 36px" : "12px 26px",
        color: COLORS.text,
        fontFamily: FONT,
        fontWeight: 700,
        fontSize: big ? 54 : 38,
        boxShadow: "0 12px 40px rgba(0, 0, 0, 0.45)",
        opacity,
        transform: `scale(${0.85 + 0.15 * pop}) translateY(${(1 - pop) * 26}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
