import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONT, FONT_MONO } from "../theme";
import { sec } from "../timing";

/**
 * Scene 3 (0:35–1:10) — Method, no math jargon. Built natively in Remotion
 * (storyboard asset checklist). Beats:
 *   1. 65 inverter bars rise in, plant-median line draws across.
 *   2. One bar dips below the median → turns red (a real fault).
 *   3. A cloud passes over ALL bars at once → all dip together, the median
 *      dips with them → peer ratio stays 1.00 (visual proof of cancellation).
 *   4. "EVU/DV curtailment" rows get crossed out — the trap.
 */

const N = 65;
const FAULT_IDX = 23;
const BAR_W = 16;
const GAP = 8;
const PLOT_W = N * BAR_W + (N - 1) * GAP; // 1552
const LEFT = (1920 - PLOT_W) / 2;
const BASELINE_Y = 700;
const MAX_H = 330;

// Deterministic pseudo-random heights (no Math.random — render must be pure).
const rand = (i: number): number => {
  const x = Math.sin((i + 1) * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};
const BASE: number[] = Array.from({ length: N }, (_, i) => 0.84 + 0.28 * rand(i));

const median = (values: number[]): number => {
  const s = [...values].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
};

type DiagramProps = {
  frame: number;
  /** Render fully-settled and non-interactive (Scene 8 reuse). */
  freeze?: boolean;
};

/**
 * The bar-field + median line, parameterized by frame so Scene 8 can render
 * a frozen, dimmed copy of the same diagram.
 */
export const MethodDiagram: React.FC<DiagramProps> = ({ frame, freeze }) => {
  const f = freeze ? 9999 : frame;

  // Beat 3: cloud shading hits all bars at once.
  const cloudCover = freeze
    ? 0
    : interpolate(f, [sec(14), sec(15.5), sec(19), sec(20.5)], [0, 0.35, 0.35, 0], {
        easing: Easing.bezier(0.45, 0, 0.55, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  // Beat 2: the fault bar dips.
  const faultDip = interpolate(f, [sec(8), sec(10.5)], [1, 0.55], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const heights = BASE.map((b, i) => {
    const rise = interpolate(f, [i * 1.1, i * 1.1 + 18], [0, 1], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const dip = i === FAULT_IDX ? faultDip : 1;
    return b * rise * (1 - cloudCover) * dip;
  });

  const med = median(heights.filter((h) => h > 0).length === N ? heights : BASE);
  const medianY = BASE.length > 0 ? BASELINE_Y - med * MAX_H : BASELINE_Y;

  const medianDraw = interpolate(f, [sec(4), sec(6)], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <>
      {/* Bars */}
      {heights.map((h, i) => {
        const isFault = i === FAULT_IDX && f >= sec(8.4) && !freeze;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: LEFT + i * (BAR_W + GAP),
              bottom: 1080 - BASELINE_Y,
              width: BAR_W,
              height: Math.max(0, h * MAX_H),
              background: isFault ? COLORS.fault : COLORS.healthy,
              borderRadius: 3,
            }}
          />
        );
      })}

      {/* Plant median line (dashed) */}
      <div
        style={{
          position: "absolute",
          left: LEFT,
          top: medianY,
          width: PLOT_W * medianDraw,
          borderTop: `4px dashed ${COLORS.text}`,
          opacity: 0.85,
        }}
      />
      {medianDraw > 0.95 ? (
        <div
          style={{
            position: "absolute",
            left: LEFT + PLOT_W + 14,
            top: medianY - 22,
            color: COLORS.text,
            fontFamily: FONT,
            fontSize: 26,
            fontWeight: 600,
            opacity: 0.9,
          }}
        >
          plant median
        </div>
      ) : null}

      {/* Baseline */}
      <div
        style={{
          position: "absolute",
          left: LEFT - 20,
          top: BASELINE_Y,
          width: PLOT_W + 40,
          borderTop: `2px solid ${COLORS.bgPanelBorder}`,
        }}
      />
    </>
  );
};

/** Simple cloud built from overlapping circles (emoji are render-unsafe). */
const Cloud: React.FC<{ x: number; opacity: number }> = ({ x, opacity }) => (
  <div style={{ position: "absolute", left: x, top: 230, opacity }}>
    {[
      { dx: 0, dy: 18, r: 52 },
      { dx: 44, dy: 0, r: 66 },
      { dx: 104, dy: 12, r: 56 },
      { dx: 52, dy: 34, r: 60 },
    ].map((c, i) => (
      <div
        key={i}
        style={{
          position: "absolute",
          left: c.dx,
          top: c.dy,
          width: c.r * 2,
          height: c.r * 2,
          borderRadius: "50%",
          background: "#d7deea",
        }}
      />
    ))}
  </div>
);

export const Scene3Method: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Formula banner.
  const formulaIn = spring({
    frame: Math.max(0, frame - sec(2)),
    fps,
    config: { damping: 200 },
  });

  // Fault label above the dipped bar.
  const faultLabelOpacity = interpolate(frame, [sec(10), sec(11)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Cloud flies across the whole plant.
  const cloudX = interpolate(frame, [sec(13), sec(21)], [-260, 1980], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cloudVisible = frame >= sec(13) && frame <= sec(21);
  const cancelOpacity = interpolate(
    frame,
    [sec(15), sec(16), sec(20), sec(21)],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Beat 4: curtailment trap card.
  const trapIn = spring({
    frame: Math.max(0, frame - sec(23)),
    fps,
    config: { damping: 16, stiffness: 120, mass: 0.8 },
  });
  const strike1 = interpolate(frame, [sec(25), sec(26)], [0, 100], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const strike2 = interpolate(frame, [sec(26), sec(27)], [0, 100], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const warnOpacity = interpolate(frame, [sec(27.5), sec(28.5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <MethodDiagram frame={frame} />

      {/* Formula banner — upper area, clear of captions. */}
      <div
        style={{
          position: "absolute",
          top: 64,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: formulaIn,
          transform: `translateY(${(1 - formulaIn) * -30}px)`,
        }}
      >
        <div
          style={{
            background: COLORS.bgPanel,
            border: `1px solid ${COLORS.bgPanelBorder}`,
            borderRadius: 12,
            padding: "16px 36px",
            color: COLORS.text,
            fontFamily: FONT_MONO,
            fontSize: 40,
            fontWeight: 700,
          }}
        >
          peer ratio = inverter ÷ plant median{" "}
          <span style={{ color: COLORS.textDim, fontSize: 30 }}>
            (same timestamp)
          </span>
        </div>
      </div>

      {/* Fault bar callout */}
      <div
        style={{
          position: "absolute",
          left: LEFT + FAULT_IDX * (BAR_W + GAP) - 64,
          top: BASELINE_Y - 0.62 * MAX_H - 70,
          opacity: faultLabelOpacity,
          color: COLORS.fault,
          fontSize: 34,
          fontWeight: 800,
          textAlign: "center",
          width: 150,
        }}
      >
        0.55
        <div style={{ fontSize: 24, color: COLORS.textDim, fontWeight: 600 }}>
          below 1.0 → trouble
        </div>
      </div>

      {cloudVisible ? <Cloud x={cloudX} opacity={0.95} /> : null}

      {/* Cancellation proof readout */}
      <div
        style={{
          position: "absolute",
          top: 170,
          right: 80,
          opacity: cancelOpacity,
          background: COLORS.bgPanel,
          border: `2px solid ${COLORS.healthy}`,
          borderRadius: 12,
          padding: "14px 28px",
          color: COLORS.text,
          fontSize: 32,
          fontWeight: 700,
        }}
      >
        all dip together → ratio stays{" "}
        <span style={{ color: COLORS.healthy, fontFamily: FONT_MONO }}>
          1.00
        </span>
        <div style={{ fontSize: 24, color: COLORS.textDim, fontWeight: 600 }}>
          weather cancels out
        </div>
      </div>

      {/* Curtailment trap card */}
      <div
        style={{
          position: "absolute",
          top: 220,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: trapIn,
          transform: `scale(${0.9 + 0.1 * trapIn})`,
        }}
      >
        <div
          style={{
            background: COLORS.bgPanel,
            border: `1px solid ${COLORS.bgPanelBorder}`,
            borderRadius: 14,
            padding: "26px 44px",
            minWidth: 760,
            boxShadow: "0 18px 60px rgba(0,0,0,0.5)",
          }}
        >
          {[
            { label: "EVU curtailment — grid feed-in limited", strike: strike1 },
            { label: "DV curtailment — grid operator signal", strike: strike2 },
          ].map((row, i) => (
            <div
              key={i}
              style={{
                position: "relative",
                color: COLORS.text,
                fontFamily: FONT_MONO,
                fontSize: 34,
                padding: "10px 0",
              }}
            >
              {row.label}
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: "50%",
                  width: `${row.strike}%`,
                  borderTop: `5px solid ${COLORS.fault}`,
                }}
              />
            </div>
          ))}
          <div
            style={{
              marginTop: 14,
              opacity: warnOpacity,
              color: COLORS.warn,
              fontSize: 30,
              fontWeight: 700,
            }}
          >
            ⚠ Curtailment (EVU/DV) excluded — the trap
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
