import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { StatPill } from "../components/StatPill";
import { COLORS } from "../theme";
import { sec } from "../timing";

const DURATION = sec(20);

/**
 * Scene 7 (2:50–3:10) — Bonus: stale asset register.
 * Heatmap pushed in (zoomed view standing in for the ">1.1 filtered" export,
 * which does not exist as a separate asset yet — see README), with the
 * stale-kWp punchline as overlays.
 */
export const Scene7StaleRegister: React.FC = () => {
  return (
    <AbsoluteFill>
      <KenBurnsImage
        src={staticFile("heatmap_monthly_ratio.png")}
        durationInFrames={DURATION}
        startScale={1.45}
        endScale={1.6}
        panY={60}
        maxHeight={780}
      />

      <div
        style={{
          position: "absolute",
          top: 56,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 24,
        }}
      >
        <StatPill delay={sec(2)} big color={COLORS.accent}>
          ~8 inverters permanently &gt; 1.1 ratio
        </StatPill>
        <StatPill delay={sec(8)} big color={COLORS.warn}>
          → stale kWp register, not magic panels
        </StatPill>
      </div>
    </AbsoluteFill>
  );
};
