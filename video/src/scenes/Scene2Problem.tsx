import React from "react";
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { StatPill } from "../components/StatPill";
import { COLORS, FONT } from "../theme";
import { sec } from "../timing";

const DURATION = sec(25);

/**
 * Scene 2 (0:10–0:35) — The problem.
 * Monthly heatmap (65 inverters x 113 months) slowly zooming OUT — red
 * failure streaks become visible against the green. End frame: team name +
 * challenge title appear small in the corner.
 */
export const Scene2Problem: React.FC = () => {
  const frame = useCurrentFrame();

  const badgeOpacity = interpolate(frame, [sec(19), sec(21)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurnsImage
        src={staticFile("heatmap_monthly_ratio.png")}
        durationInFrames={DURATION}
        startScale={1.55}
        endScale={1.0}
        panY={-10}
        maxHeight={780}
      />

      <div
        style={{
          position: "absolute",
          top: 56,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 32,
        }}
      >
        <StatPill delay={sec(3)} color={COLORS.accent}>
          9.4 years
        </StatPill>
        <StatPill delay={sec(4.5)} color={COLORS.accent}>
          65 inverters
        </StatPill>
        <StatPill delay={sec(6)} color={COLORS.accent}>
          5-min resolution
        </StatPill>
      </div>

      {/* Team badge, small, top-right corner near the end of the scene. */}
      <div
        style={{
          position: "absolute",
          top: 180,
          right: 64,
          opacity: badgeOpacity,
          background: COLORS.bgPanel,
          border: `1px solid ${COLORS.bgPanelBorder}`,
          borderRadius: 10,
          padding: "12px 22px",
          color: COLORS.textDim,
          fontFamily: FONT,
          fontSize: 28,
          fontWeight: 600,
        }}
      >
        <span style={{ color: COLORS.text }}>Team Syz</span> — Challenge #2.1:
        Digital Twin of a Solar Plant
      </div>
    </AbsoluteFill>
  );
};
