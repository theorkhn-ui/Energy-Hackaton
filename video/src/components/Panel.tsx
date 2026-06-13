import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

export type PanelVariant = "paper" | "ink" | "lemon";

type Props = {
  variant?: PanelVariant;
  /** Frames (scene-relative) before the panel enters. */
  delay?: number;
  /** Entrance direction. */
  from?: "left" | "right" | "top" | "bottom" | "scale";
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

export const panelColors = (
  variant: PanelVariant,
): { background: string; color: string } => {
  switch (variant) {
    case "ink":
      return { background: COLORS.ink, color: COLORS.paper };
    case "lemon":
      return { background: COLORS.lemon, color: COLORS.ink };
    default:
      return { background: COLORS.paper, color: COLORS.ink };
  }
};

/**
 * Neo-Grid Bold panel: rectangular color block (zero radius, no shadow) with
 * a spring entrance. Composition = colored panels trading roles on the grid.
 */
export const Panel: React.FC<Props> = ({
  variant = "paper",
  delay = 0,
  from = "bottom",
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 18, stiffness: 140, mass: 0.8 },
  });

  const off = (1 - pop) * 90;
  const transform =
    from === "left"
      ? `translateX(${-off}px)`
      : from === "right"
        ? `translateX(${off}px)`
        : from === "top"
          ? `translateY(${-off}px)`
          : from === "scale"
            ? `scale(${0.82 + 0.18 * pop})`
            : `translateY(${off}px)`;

  return (
    <div
      style={{
        position: "relative",
        ...panelColors(variant),
        opacity: Math.min(1, pop * 1.6),
        transform,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
