import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { StatPill } from "../components/StatPill";
import { COLORS, display, FONT, label } from "../theme";
import { sec } from "../timing";

const DURATION = sec(35);

/**
 * Scene 6 (2:15-2:50) — Finding 3: failure in progress.
 * Section-collapse chart wipes in with a bold rectangle drawn around the
 * collapse region; pulsing ACTIVE tag; outage-hours counter ticks to 840;
 * €42k/yr-at-risk lemon chip; dead-telemetry ink chip; fault-matrix panel
 * slides in for the root-cause beat.
 */
export const Scene6ActiveCollapse: React.FC = () => {
  const frame = useCurrentFrame();

  // Pulsing ACTIVE tag (deterministic sine, no CSS animation).
  const pulse = 0.75 + 0.25 * Math.sin((frame / 30) * Math.PI * 2);

  return (
    <NeoFrame index={6} tag="Finding 3: live">
      <AbsoluteFill>
        <ChartBlock
          src={staticFile("section_collapse.png")}
          durationInFrames={DURATION}
          wipeFrom="left"
          wipeDuration={30}
          startScale={1.0}
          endScale={1.12}
          panX={-16}
          width={1160}
          height={680}
          caption="Sections 01.08 + 01.09"
          highlights={[
            {
              shape: "rect",
              x: 0.55,
              y: 0.18,
              w: 0.4,
              h: 0.62,
              at: sec(4),
              tag: "Collapsing since Aug 2025",
            },
          ]}
          style={{
            justifyContent: "flex-start",
            alignItems: "flex-end",
            paddingLeft: 90,
            paddingBottom: 120,
          }}
        />

        {/* Pulsing ACTIVE tag, top-left. */}
        <div
          style={{
            position: "absolute",
            top: 64,
            left: 90,
            display: "flex",
            gap: 24,
            alignItems: "center",
          }}
        >
          <div
            style={{
              background: COLORS.fault,
              opacity: pulse,
              color: COLORS.paper,
              ...display(40),
              padding: "12px 28px",
              border: `1.5px solid ${COLORS.ink}`,
            }}
          >
            ● Active
          </div>
          <StatPill delay={sec(1.5)} variant="ink">
            2 inverters still below 0.7
          </StatPill>
        </div>

        {/* Right rail: counter + money + telemetry. */}
        <div style={{ position: "absolute", right: 96, top: 150, width: 560 }}>
          <BigNumeral
            delay={sec(9)}
            value="840 h"
            countTo={840}
            suffix=" H"
            countDuration={sec(5)}
            size={150}
            color={COLORS.fault}
            sub="Outage hours / 365 d, worst unit"
            subColor={COLORS.ink}
          />

          <div style={{ marginTop: 40 }}>
            <StatPill delay={sec(15)} big variant="lemon" kicker="Revenue at risk">
              €42k / year
            </StatPill>
          </div>

          <div style={{ marginTop: 30 }}>
            <StatPill delay={sec(19)} variant="ink" kicker="Why no alarm fired">
              Telemetry dead since 2019
            </StatPill>
          </div>
        </div>

        {/* Fault matrix slides in: root-cause work in progress. */}
        <Panel
          variant="ink"
          delay={sec(24)}
          from="right"
          style={{
            position: "absolute",
            right: 96,
            bottom: 130,
            padding: 14,
            width: 600,
          }}
        >
          <Img
            src={staticFile("fault_matrix.png")}
            style={{ width: "100%", display: "block" }}
          />
          <div
            style={{
              marginTop: 12,
              ...label(17),
              color: COLORS.paper,
              textAlign: "center",
            }}
          >
            Error-code classification &gt; root cause (in progress)
          </div>
        </Panel>

        {/* Punchline strip. */}
        <Panel
          variant="lemon"
          delay={sec(29)}
          from="bottom"
          style={{
            position: "absolute",
            left: 90,
            bottom: 130,
            padding: "18px 30px",
          }}
        >
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 36, textTransform: "uppercase", letterSpacing: "-0.01em" }}>
            Ticket #1, written today
          </div>
        </Panel>
      </AbsoluteFill>
    </NeoFrame>
  );
};
