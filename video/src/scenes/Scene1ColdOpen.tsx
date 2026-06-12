import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { StatPill } from "../components/StatPill";
import { COLORS } from "../theme";

/**
 * Scene 1 (0:00–0:10) — Cold open: the hook.
 * Black screen → lead-time lollipop chart snaps in, one lollipop at a time
 * (stepped left-to-right wipe). No logo, no title — straight to the stat.
 */
export const Scene1ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();

  // Stepped reveal: quantized into 12 "snaps" so lollipops pop in in groups.
  const reveal = interpolate(frame, [8, 75], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stepped = Math.ceil(reveal * 12) / 12;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center" }}
      >
        <Img
          src={staticFile("leadtime_chart.png")}
          style={{
            maxWidth: 1640,
            maxHeight: 720,
            objectFit: "contain",
            background: "#ffffff",
            padding: 16,
            borderRadius: 14,
            boxShadow: "0 24px 90px rgba(0, 0, 0, 0.6)",
            clipPath: `inset(0 ${(1 - stepped) * 100}% 0 0)`,
          }}
        />
      </AbsoluteFill>

      {/* Stat overlays — upper third, never colliding with captions. */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 40,
        }}
      >
        <StatPill delay={140} big color={COLORS.fault}>
          42 / 46 failures predicted
        </StatPill>
        <StatPill delay={200} big color={COLORS.accent}>
          51.5 days median lead time
        </StatPill>
      </div>
    </AbsoluteFill>
  );
};
