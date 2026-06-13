import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { StatPill } from "../components/StatPill";
import { COLORS, display, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 4 (1:10-1:45), Finding 1: predictive power.
 * Lead-time chart wipes in from the bottom and holds still on the LEFT edge;
 * a fault-red ellipse draws around the long-lead cluster near the median
 * line (the payload of the scene); the oversized 42/46 numeral, ticket
 * chips, and lemon "7 weeks of warning" panel choreograph in on the right.
 */
export const Scene4Leadtime: React.FC = () => {
  return (
    <NeoFrame index={4} tag="Finding 1: it works">
      <AbsoluteFill>
        {/* Chart pulled to the left border, slightly narrower, so the right
            rail (42/46 + chips + payoff) has clear room. */}
        <ChartBlock
          src={staticFile("leadtime_chart.png")}
          wipeFrom="bottom"
          wipeDuration={32}
          width={1080}
          height={690}
          caption="Back-test vs real service tickets"
          highlights={[
            {
              shape: "ellipse",
              x: 0.6,
              y: 0.1,
              w: 0.32,
              h: 0.4,
              at: sec(15),
              color: COLORS.fault,
              tag: "Flags fired ~51 days early",
            },
          ]}
          style={{
            justifyContent: "flex-start",
            alignItems: "center",
            paddingLeft: 52,
          }}
        />

        {/* Right rail: oversized stat + chips. */}
        <div style={{ position: "absolute", right: 96, top: 120, width: 520 }}>
          <BigNumeral
            delay={sec(5)}
            value="42/46"
            size={170}
            color={COLORS.ink}
            sub="Tickets flagged in advance"
          />

          <div style={{ marginTop: 40 }}>
            <StatPill delay={sec(11)} big variant="ink" kicker="Median lead">
              51.5 days
            </StatPill>
          </div>

          {/* Ticket-category chips, staggered. */}
          <div
            style={{
              marginTop: 36,
              display: "flex",
              flexWrap: "wrap",
              gap: 16,
            }}
          >
            {["capacitors", "boards", "insulation"].map((labelText, i) => (
              <StatPill
                key={labelText}
                delay={sec(8 + i * 0.7)}
                variant="paper"
                style={{ boxShadow: "none" }}
              >
                {labelText}
              </StatPill>
            ))}
          </div>
        </div>

        {/* The payoff panel slams up from the bottom. */}
        <Panel
          variant="lemon"
          delay={sec(20)}
          from="bottom"
          style={{
            position: "absolute",
            right: 96,
            bottom: 140,
            padding: "26px 38px",
          }}
        >
          <div style={{ ...label(18), opacity: 0.7, marginBottom: 8 }}>
            What 51.5 days buys you
          </div>
          <div style={{ ...display(56) }}>= 7 weeks of warning</div>
        </Panel>
      </AbsoluteFill>
    </NeoFrame>
  );
};
