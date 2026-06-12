import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONT } from "../theme";
import { MethodDiagram } from "./Scene3Method";

/**
 * Scene 8 (3:10–3:20) — Honest limitation.
 * Calm, static frame: the Scene-3 method diagram, frozen and dimmed, with one
 * caption line. Deliberately no animation — let the sentence land
 * (storyboard: sincerity beat).
 */
export const Scene8Limitation: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ fontFamily: FONT, opacity: fadeIn }}>
      <AbsoluteFill style={{ opacity: 0.22 }}>
        <MethodDiagram frame={0} freeze />
      </AbsoluteFill>

      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center" }}
      >
        <div
          style={{
            maxWidth: 1400,
            textAlign: "center",
            color: COLORS.text,
            fontSize: 52,
            fontWeight: 700,
            lineHeight: 1.35,
          }}
        >
          Known limit:{" "}
          <span style={{ color: COLORS.warn }}>relative method</span> —
          plant-wide degradation needs an absolute baseline
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
