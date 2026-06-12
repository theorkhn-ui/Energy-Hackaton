import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { StatPill } from "../components/StatPill";
import { COLORS, FONT, FONT_MONO } from "../theme";
import { sec } from "../timing";

/**
 * Scene 5 (1:45–2:15) — Finding 2: the invisible fault.
 * Part A (0–15s): a flat peer-ratio line at ~0.70 for INV 01.03.018 drawn
 * in natively, then a ticket-log search animation returning "0 results".
 * Part B (15–30s): the money bar chart with the verified ~EUR500/yr highlight.
 */

const PART_A = sec(15);
const PART_B = sec(15);

// Deterministic noise for the flat-but-real-looking ratio line.
const noise = (i: number): number => {
  const x = Math.sin((i + 7) * 78.233) * 43758.5453;
  return x - Math.floor(x);
};

const CHART_W = 1320;
const CHART_H = 440;
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
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", fontFamily: FONT }}
    >
      <div
        style={{
          background: COLORS.bgPanel,
          border: `1px solid ${COLORS.bgPanelBorder}`,
          borderRadius: 16,
          padding: "30px 40px 20px",
          boxShadow: "0 20px 70px rgba(0,0,0,0.5)",
        }}
      >
        <div
          style={{
            color: COLORS.text,
            fontSize: 34,
            fontWeight: 800,
            marginBottom: 12,
            fontFamily: FONT_MONO,
          }}
        >
          INV 01.03.018{" "}
          <span style={{ color: COLORS.textDim, fontWeight: 600, fontSize: 26 }}>
            — peer ratio, last 12 months
          </span>
        </div>

        <svg width={CHART_W} height={CHART_H}>
          {/* healthy reference at 1.0 */}
          <line
            x1={0}
            x2={CHART_W}
            y1={y(1.0)}
            y2={y(1.0)}
            stroke={COLORS.healthy}
            strokeWidth={3}
            strokeDasharray="14 10"
            opacity={0.8}
          />
          <text
            x={CHART_W - 8}
            y={y(1.0) - 12}
            fill={COLORS.healthy}
            fontSize={26}
            fontFamily={FONT}
            textAnchor="end"
          >
            healthy = 1.0
          </text>

          {/* the flat 0.70 line, revealed left-to-right */}
          <g clipPath="url(#reveal)">
            <polyline
              points={pts}
              fill="none"
              stroke={COLORS.fault}
              strokeWidth={5}
              strokeLinejoin="round"
            />
          </g>
          <defs>
            <clipPath id="reveal">
              <rect x={0} y={0} width={CHART_W * draw} height={CHART_H} />
            </clipPath>
          </defs>

          {draw > 0.97 ? (
            <text
              x={CHART_W - 8}
              y={y(0.7) + 40}
              fill={COLORS.fault}
              fontSize={30}
              fontWeight={800}
              fontFamily={FONT}
              textAnchor="end"
            >
              0.70 — flat for 12 months
            </text>
          ) : null}
        </svg>

        {/* ticket-log search */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            marginTop: 16,
            opacity: frame >= sec(6) ? 1 : 0,
          }}
        >
          <div
            style={{
              background: "#0a0f1c",
              border: `1px solid ${COLORS.bgPanelBorder}`,
              borderRadius: 8,
              padding: "10px 20px",
              fontFamily: FONT_MONO,
              fontSize: 28,
              color: COLORS.text,
              minWidth: 460,
            }}
          >
            <span style={{ color: COLORS.textDim }}>ticket log ▸ </span>
            {query.slice(0, typedLen)}
            <span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>▌</span>
          </div>
          <StatPill delay={sec(9.5)} color={COLORS.fault}>
            Service tickets found: 0
          </StatPill>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Scene5InvisibleFault: React.FC = () => {
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={PART_A} name="5a — ratio line + 0 tickets">
        <RatioLine />
      </Sequence>

      <Sequence from={PART_A} durationInFrames={PART_B} name="5b — money chart">
        <AbsoluteFill>
          <KenBurnsImage
            src={staticFile("money_chart.png")}
            durationInFrames={PART_B}
            startScale={1.02}
            endScale={1.12}
            maxHeight={760}
          />
          <div
            style={{
              position: "absolute",
              top: 60,
              left: 0,
              right: 0,
              display: "flex",
              justifyContent: "center",
              gap: 36,
            }}
          >
            <StatPill delay={sec(2)} big color={COLORS.warn}>
              ~EUR 500 / year lost
            </StatPill>
            <StatPill delay={sec(4)} color={COLORS.textDim}>
              from a single inverter — caught from data alone
            </StatPill>
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
