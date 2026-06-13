import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { StatPill } from "../components/StatPill";
import { COLORS } from "../theme";
import { sec } from "../timing";

/**
 * Scene 7 (2:50-3:10), Bonus findings.
 * Heatmap zoomed on the top rows with an ink rectangle drawn around the
 * permanently->1.1 band; stale-kWp punchline chips plus the 71%-nuisance
 * alarm stat as a second bonus.
 */
export const Scene7StaleRegister: React.FC = () => {
  return (
    <NeoFrame index={7} tag="Bonus findings">
      <AbsoluteFill>
        <ChartBlock
          src={staticFile("heatmap_monthly_ratio.png")}
          wipeFrom="right"
          wipeDuration={26}
          scale={1.42}
          offsetY={44}
          width={1040}
          height={650}
          caption="Permanently above 1.1"
          highlights={[
            {
              shape: "rect",
              x: 0.12,
              y: 0.08,
              w: 0.74,
              h: 0.22,
              at: sec(4),
              color: COLORS.ink,
              tag: "Always 'overperforming'",
            },
          ]}
          style={{
            justifyContent: "flex-start",
            alignItems: "center",
            paddingLeft: 52,
          }}
        />

        {/* Right rail. */}
        <div style={{ position: "absolute", right: 96, top: 140, width: 540 }}>
          <BigNumeral
            delay={sec(2)}
            value="~8"
            countTo={8}
            prefix="~"
            countDuration={sec(1.6)}
            size={170}
            color={COLORS.ink}
            sub="Inverters always above ratio 1.1"
          />
          <div style={{ marginTop: 40 }}>
            <StatPill delay={sec(7)} big variant="lemon" kicker="The real reason">
              Stale kWp register
            </StatPill>
          </div>
          <div style={{ marginTop: 30 }}>
            <StatPill delay={sec(12)} variant="ink" kicker="Bonus #2: alarm triage">
              71% of alarms = nuisance
            </StatPill>
          </div>
        </div>
      </AbsoluteFill>
    </NeoFrame>
  );
};
