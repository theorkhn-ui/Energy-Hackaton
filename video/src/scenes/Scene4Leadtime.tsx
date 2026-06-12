import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { StatPill } from "../components/StatPill";
import { COLORS, FONT } from "../theme";
import { sec } from "../timing";

const DURATION = sec(35);

/**
 * Scene 4 (1:10–1:45) — Finding 1: predictive power.
 * Full lead-time lollipop chart with a slow Ken Burns push-in; the headline
 * stats and ticket-category chips spring in over it.
 */
export const Scene4Leadtime: React.FC = () => {
  return (
    <AbsoluteFill>
      <KenBurnsImage
        src={staticFile("leadtime_chart.png")}
        durationInFrames={DURATION}
        startScale={1.0}
        endScale={1.12}
        panY={-14}
        maxHeight={760}
      />

      <div
        style={{
          position: "absolute",
          top: 52,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 36,
        }}
      >
        <StatPill delay={sec(7)} big color={COLORS.healthy}>
          42 of 46 tickets flagged in advance
        </StatPill>
        <StatPill delay={sec(12.5)} big color={COLORS.accent}>
          Median lead: 51.5 days
        </StatPill>
      </div>

      {/* Ticket category chips */}
      <div
        style={{
          position: "absolute",
          top: 175,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 24,
          fontFamily: FONT,
        }}
      >
        {["capacitors", "boards", "insulation faults"].map((label, i) => (
          <StatPill
            key={label}
            delay={sec(9 + i * 0.8)}
            color={COLORS.textDim}
            style={{ fontSize: 30, fontWeight: 600, color: COLORS.textDim }}
          >
            {label}
          </StatPill>
        ))}
      </div>

      <div
        style={{
          position: "absolute",
          top: 270,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <StatPill delay={sec(21)} color={COLORS.warn}>
          = 7 weeks of warning
        </StatPill>
      </div>
    </AbsoluteFill>
  );
};
