import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { StatPill } from "../components/StatPill";
import { display, label } from "../theme";
import { sec } from "../timing";

const DURATION = sec(25);

/**
 * Scene 2 (0:10-0:35) — The problem.
 * Monthly heatmap (65 inverters x 113 months) wipes in from the top, then a
 * slow zoom-out; a bold fault-red rectangle draws itself around the failure
 * streaks; the dataset chips stagger in; the team panel slams in last.
 */
export const Scene2Problem: React.FC = () => {
  return (
    <NeoFrame index={2} tag="The problem">
      <AbsoluteFill>
        <ChartBlock
          src={staticFile("heatmap_monthly_ratio.png")}
          durationInFrames={DURATION}
          wipeFrom="top"
          wipeDuration={34}
          startScale={1.32}
          endScale={1.0}
          panY={-6}
          width={1500}
          height={680}
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
          style={{ paddingTop: 60 }}
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

        {/* Team panel slides in near the end. */}
        <Panel
          variant="ink"
          delay={sec(19)}
          from="right"
          style={{
            position: "absolute",
            right: 0,
            bottom: 130,
            padding: "26px 36px",
            maxWidth: 660,
          }}
        >
          <div style={{ ...label(16), opacity: 0.7, marginBottom: 8 }}>
            Energy Hack Munich 2026
          </div>
          <div style={{ ...display(44) }}>Team Syz</div>
          <div style={{ ...label(18), marginTop: 10, opacity: 0.85 }}>
            Challenge #2.1: Digital twin of a solar plant
          </div>
        </Panel>
      </AbsoluteFill>
    </NeoFrame>
  );
};
