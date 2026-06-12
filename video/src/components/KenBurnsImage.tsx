import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, useCurrentFrame } from "remotion";

type Props = {
  src: string;
  durationInFrames: number;
  /** Scale at the first frame of the (parent) sequence. */
  startScale?: number;
  /** Scale at the last frame. >start = slow zoom in, <start = zoom out. */
  endScale?: number;
  /** Total horizontal drift in px (applied pre-scale). */
  panX?: number;
  /** Total vertical drift in px. */
  panY?: number;
  maxWidth?: number;
  maxHeight?: number;
  /** Extra styles on the white chart card. */
  cardStyle?: React.CSSProperties;
};

/**
 * Full-screen chart image with a subtle Ken Burns move, driven by
 * interpolate() + Bézier easing (per remotion-best-practices: never CSS
 * animations). Matplotlib PNGs are wrapped in a white rounded "card" so they
 * sit intentionally on the dark background.
 */
export const KenBurnsImage: React.FC<Props> = ({
  src,
  durationInFrames,
  startScale = 1.0,
  endScale = 1.08,
  panX = 0,
  panY = 0,
  maxWidth = 1700,
  maxHeight = 800,
  cardStyle,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(progress, [0, 1], [startScale, endScale]);
  const tx = interpolate(progress, [0, 1], [0, panX]);
  const ty = interpolate(progress, [0, 1], [0, panY]);

  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", overflow: "hidden" }}
    >
      <div style={{ transform: `scale(${scale}) translate(${tx}px, ${ty}px)` }}>
        <Img
          src={src}
          style={{
            maxWidth,
            maxHeight,
            objectFit: "contain",
            background: "#ffffff",
            padding: 18,
            borderRadius: 16,
            boxShadow: "0 24px 90px rgba(0, 0, 0, 0.55)",
            ...cardStyle,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
