import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { StatPill } from "../components/StatPill";
import { sec } from "../timing";

/**
 * Scene 2 (0:10-0:35) — The problem.
 * Monthly heatmap (65 inverters x 113 months) wipes in from the top and
 * holds still; a bold fault-red rectangle draws itself around the failure
 * streaks; the dataset chips stagger in along the top. The heatmap stops
 * well above the caption bar so subtitles never sit on the chart.
 */
export const Scene2Problem: React.FC = () => {
  return (
    <NeoFrame index={2} tag="The problem">
      <AbsoluteFill>
        {/* Panel aspect matches the 1.6 PNG so the heatmap fills its frame. */}
        <ChartBlock
          src={staticFile("heatmap_monthly_ratio.png")}
          wipeFrom="top"
          wipeDuration={34}
          width={1060}
          height={650}
          caption="9.4 years x 65 inverters, monthly peer ratio"
          highlights={[
            {
              shape: "rect",
              x: 0.56,
              y: 0.32,
              w: 0.3,
              h: 0.34,
              at: sec(13),
              tag: "Failures nobody caught",
            },
          ]}
          style={{
            justifyContent: "center",
            alignItems: "flex-start",
            paddingTop: 175,
          }}
        />

        {/* Dataset chips, staggered along the top. */}
        <div
          style={{
            position: "absolute",
            top: 64,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            gap: 28,
          }}
        >
          <StatPill delay={sec(3)} variant="ink" kicker="Dataset">
            9.4 years
          </StatPill>
          <StatPill delay={sec(4.2)} variant="ink">
            65 inverters
          </StatPill>
          <StatPill delay={sec(5.4)} variant="lemon">
            5-min readings
          </StatPill>
        </div>
      </AbsoluteFill>
    </NeoFrame>
  );
};
