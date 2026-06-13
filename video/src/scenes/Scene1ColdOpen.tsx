import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { StatPill } from "../components/StatPill";
import { COLORS, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 1 (0:00-0:10), Cold open on the stage-black frame.
 * Oversized "42/46" slams in, the lead-time chart wipes in beside it,
 * the lemon "51.5 days" chip lands last. No logo, straight to the stat.
 * Left column ends well before the chart edge so nothing ever overlaps.
 */
export const Scene1ColdOpen: React.FC = () => {
  return (
    <NeoFrame index={1} tag="The hook" mode="ink">
      <AbsoluteFill>
        {/* Oversized numeral block, left. */}
        <div style={{ position: "absolute", left: 96, top: 210 }}>
          <BigNumeral
            delay={6}
            value="42/46"
            size={200}
            color={COLORS.paper}
            sub="Failures visible in the data first"
            subColor={COLORS.paper}
          />
          <div style={{ marginTop: 56 }}>
            <StatPill delay={sec(5)} big variant="lemon" kicker="Median warning">
              51.5 days before a ticket
            </StatPill>
          </div>
        </div>

        {/* Lead-time chart wipes in, right. Static after the wipe. */}
        <ChartBlock
          src={staticFile("leadtime_chart.png")}
          wipeFrom="left"
          wipeDuration={40}
          width={880}
          height={600}
          caption="Lead time per ticket"
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingRight: 80,
          }}
        />

        {/* Mono context line, top-left. */}
        <div
          style={{
            position: "absolute",
            left: 96,
            top: 94,
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
