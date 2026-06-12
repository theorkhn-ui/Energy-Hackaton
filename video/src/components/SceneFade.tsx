import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

type Props = {
  durationInFrames: number;
  /** Set to 0 to hard-cut in (Scene 1 cold open). */
  fadeInFrames?: number;
  fadeOutFrames?: number;
  children: React.ReactNode;
};

/**
 * Gentle fade at scene boundaries so cuts between full-screen charts do not
 * flash. Uses interpolate with clamping (remotion-best-practices).
 */
export const SceneFade: React.FC<Props> = ({
  durationInFrames,
  fadeInFrames = 10,
  fadeOutFrames = 10,
  children,
}) => {
  const frame = useCurrentFrame();

  const fadeIn =
    fadeInFrames <= 0
      ? 1
      : interpolate(frame, [0, fadeInFrames], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
  const fadeOut =
    fadeOutFrames <= 0
      ? 1
      : interpolate(
          frame,
          [durationInFrames - fadeOutFrames, durationInFrames - 1],
          [1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );

  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn, fadeOut) }}>
      {children}
    </AbsoluteFill>
  );
};
