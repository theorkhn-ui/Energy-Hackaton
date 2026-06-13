import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { BigNumeral } from "../components/BigNumeral";
import { ChartBlock } from "../components/ChartBlock";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { StatPill } from "../components/StatPill";
import { COLORS, FONT_MONO, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 5 (1:45-2:15) — Finding 2: the invisible fault.
 * Part A (0-15s): flat peer-ratio line at ~0.70 for INV 01.03.018 draws in
 * on a paper panel, then a ticket-log search types itself and returns 0.
 * Part B (15-30s): the money chart wipes in with a bold ellipse around the
 * verified ~EUR 500/yr bar.
 */

const PART_A = sec(15);
const PART_B = sec(15);

// Deterministic noise for the flat-but-real-looking ratio line.
const noise = (i: number): number => {
  const x = Math.sin((i + 7) * 78.233) * 43758.5453;
  return x - Math.floor(x);
};

const CHART_W = 1280;
const CHART_H = 420;
const POINTS = 48;

const RatioLine: React.FC = () => {
  const frame = useCurrentFrame();

  const draw = interpolate(frame, [10, 100], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const y = (ratio: number): number =>
    CHART_H - ((ratio - 0.4) / (1.3 - 0.4)) * CHART_H;

  const pts = Array.from({ length: POINTS }, (_, i) => {
    const x = (i / (POINTS - 1)) * CHART_W;
    const ratio = 0.7 + (noise(i) - 0.5) * 0.045;
    return `${x},${y(ratio)}`;
  }).join(" ");

  // Search beat
  const query = "INV 01.03.018";
  const typedLen = Math.floor(
    interpolate(frame, [sec(6), sec(8)], [0, query.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <Panel
        variant="paper"
        delay={0}
        from="scale"
        style={{
          border: `3px solid ${COLORS.ink}`,
          padding: "34px 44px 26px",
        }}
      >
        {/* Block title bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 18 }}>
          <div
            style={{
              background: COLORS.ink,
              color: COLORS.paper,
              fontFamily: FONT_MONO,
              fontSize: 30,
              letterSpacing: "0.06em",
              padding: "8px 18px",
            }}
          >
            INV 01.03.018
          </div>
          <div style={{ ...label(20), color: COLORS.ink, opacity: 0.7 }}>
            Peer ratio, last 12 months
          </div>
        </div>

        <svg width={CHART_W} height={CHART_H}>
          {/* healthy reference at 1.0 */}
          <line
            x1={0}
            x2={CHART_W}
            y1={y(1.0)}
            y2={y(1.0)}
            stroke={COLORS.ink}
            strokeWidth={3}
            strokeDasharray="14 10"
            opacity={0.7}
          />
          <rect x={CHART_W - 250} y={y(1.0) - 44} width={242} height={34} fill={COLORS.lemon} />
          <text
            x={CHART_W - 238}
            y={y(1.0) - 20}
            fill={COLORS.ink}
            fontSize={20}
            fontFamily={FONT_MONO}
            letterSpacing="0.08em"
          >
            HEALTHY = 1.0
          </text>

          {/* the flat 0.70 line, revealed left-to-right */}
          <g clipPath="url(#reveal)">
            <polyline
              points={pts}
              fill="none"
              stroke={COLORS.fault}
              strokeWidth={6}
              strokeLinejoin="round"
            />
          </g>
          <defs>
            <clipPath id="reveal">
              <rect x={0} y={0} width={CHART_W * draw} height={CHART_H} />
            </clipPath>
          </defs>

          {draw > 0.97 ? (
            <g>
              <rect x={CHART_W - 420} y={y(0.7) + 16} width={412} height={40} fill={COLORS.fault} />
              <text
                x={CHART_W - 404}
                y={y(0.7) + 44}
                fill={COLORS.paper}
                fontSize={22}
                fontFamily={FONT_MONO}
                letterSpacing="0.06em"
              >
                0.70 FLAT FOR 12 MONTHS
              </text>
            </g>
          ) : null}
        </svg>

        {/* ticket-log search */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 28,
            marginTop: 20,
            opacity: frame >= sec(6) ? 1 : 0,
          }}
        >
          <div
            style={{
              background: COLORS.ink,
              color: COLORS.paper,
              padding: "12px 22px",
              fontFamily: FONT_MONO,
              fontSize: 28,
              minWidth: 480,
            }}
          >
            <span style={{ opacity: 0.55 }}>TICKET LOG &gt; </span>
            {query.slice(0, typedLen)}
            <span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>█</span>
          </div>
          <StatPill delay={sec(9.5)} variant="fault" kicker="Search result">
            0 tickets found
          </StatPill>
        </div>
      </Panel>
    </AbsoluteFill>
  );
};

export const Scene5InvisibleFault: React.FC = () => {
  return (
    <NeoFrame index={5} tag="Finding 2: invisible">
      <Sequence durationInFrames={PART_A} name="5a: ratio line + 0 tickets">
        <RatioLine />
      </Sequence>

      <Sequence from={PART_A} durationInFrames={PART_B} name="5b: money chart">
        <AbsoluteFill>
          <ChartBlock
            src={staticFile("money_chart.png")}
            wipeFrom="left"
            wipeDuration={26}
            width={1180}
            height={690}
            caption="Lost revenue per inverter"
            highlights={[
              {
                // Hug the orange "found by our model" bar (top row) instead
                // of floating off to the left of it (judge: "out of place").
                shape: "rect",
                x: 0.12,
                y: 0.205,
                w: 0.62,
                h: 0.085,
                at: sec(4),
                tag: "INV 01.03.018",
              },
            ]}
            style={{
              justifyContent: "flex-start",
              alignItems: "center",
              paddingLeft: 52,
            }}
          />

          {/* Right rail: the money stat. */}
          <div style={{ position: "absolute", right: 96, top: 170, width: 500 }}>
            <BigNumeral
              delay={sec(2)}
              value="~€500"
              countTo={500}
              prefix="~€"
              countDuration={sec(2.2)}
              size={150}
              color={COLORS.ink}
              sub="Per year, one inverter"
            />
            <div style={{ marginTop: 40 }}>
              <StatPill delay={sec(5)} big variant="lemon" kicker="How we found it">
                Data alone
              </StatPill>
            </div>
            <div style={{ marginTop: 36 }}>
              <StatPill delay={sec(7)} variant="ink">
                No ticket. Nobody noticed.
              </StatPill>
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>
    </NeoFrame>
  );
};
