import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { StatPill } from "../components/StatPill";
import { COLORS, label } from "../theme";
import { sec } from "../timing";

const DURATION = sec(10);

/**
 * Scene 1 (0:00-0:10) — Cold open on the stage-black frame.
 * Oversized "42/46" slams in, the lead-time chart wipes in beside it,
 * the lemon "51.5 days" chip lands last. No logo, straight to the stat.
 */
export const Scene1ColdOpen: React.FC = () => {
  return (
    <NeoFrame index={1} tag="The hook" mode="ink">
      <AbsoluteFill>
        {/* Oversized numeral block, left. */}
        <div style={{ position: "absolute", left: 96, top: 200 }}>
          <BigNumeral
            delay={6}
            value="42/46"
            size={220}
            color={COLORS.paper}
            sub="Failures visible in the data first"
            subColor={COLORS.paper}
          />
          <div style={{ marginTop: 48 }}>
            <StatPill delay={sec(5)} big variant="lemon" kicker="Median warning">
              51.5 days before a ticket
            </StatPill>
          </div>
        </div>

        {/* Lead-time chart wipes in, right. */}
        <ChartBlock
          src={staticFile("leadtime_chart.png")}
          durationInFrames={DURATION}
          wipeFrom="left"
          wipeDuration={40}
          startScale={1.0}
          endScale={1.05}
          width={880}
          height={600}
          caption="Lead time per ticket"
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingRight: 90,
          }}
        />

        {/* Mono context line, top-left. */}
        <div
          style={{
            position: "absolute",
            left: 96,
            top: 84,
            ...label(20),
            color: COLORS.paper,
            opacity: 0.7,
          }}
        >
          Real solar plant / real service tickets
        </div>
      </AbsoluteFill>
    </NeoFrame>
  );
};
