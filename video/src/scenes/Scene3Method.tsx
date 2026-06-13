import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { StatPill } from "../components/StatPill";
import { COLORS, display, FONT_MONO, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 3 (0:35-1:10), Method, no math jargon. Native Remotion. Beats:
 *   1. 65 inverter bars rise in (ink on paper), median line draws across.
 *   2. One bar dips below the median and turns red (a real fault).
 *   3. THE BIG BEAT (10.5s-16s): everything freezes and dims, the bad bar
 *      pulses red, a HUGE "0.55" springs in with the "below 1.0 = trouble"
 *      tag, held for 4+ seconds. This is the number the judges must keep.
 *   4. A cloud passes over ALL bars at once, all dip together, the ratio
 *      stays 1.00 (visual proof that weather cancels out).
 *   5. "EVU/DV curtailment" rows get struck out: the trap.
 */

const N = 65;
const FAULT_IDX = 23;
const BAR_W = 16;
const GAP = 8;
const PLOT_W = N * BAR_W + (N - 1) * GAP; // 1552
const LEFT = (1920 - PLOT_W) / 2;
const BASELINE_Y = 720;
const MAX_H = 330;

// Deterministic pseudo-random heights (no Math.random, render must be pure).
const rand = (i: number): number => {
  const x = Math.sin((i + 1) * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};
const BASE: number[] = Array.from({ length: N }, (_, i) => 0.84 + 0.28 * rand(i));

const median = (values: number[]): number => {
  const s = [...values].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
};

// Beat boundaries (seconds within the scene).
const T_DIP_START = 8;
const T_DIP_END = 10.5;
const T_FREEZE_IN = 10.5;
const T_FREEZE_OUT = 15.8; // >= 2.5s hold, actually >4s
const T_CLOUD_START = 17;
const T_CLOUD_END = 24;
const T_TRAP = 25.5;

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

  // Beat 4: cloud shading hits all bars at once.
  const cloudCover = freeze
    ? 0
    : interpolate(
        f,
        [sec(T_CLOUD_START + 1), sec(T_CLOUD_START + 2.5), sec(T_CLOUD_END - 1.5), sec(T_CLOUD_END)],
        [0, 0.35, 0.35, 0],
        {
          easing: Easing.bezier(0.45, 0, 0.55, 1),
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        },
      );

  // Beat 2: the fault bar dips.
  const faultDip = interpolate(f, [sec(T_DIP_START), sec(T_DIP_END)], [1, 0.55], {
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
      {/* Bars: ink = healthy, fault red = the dipping unit. */}
      {heights.map((h, i) => {
        const isFault = i === FAULT_IDX && f >= sec(T_DIP_START + 0.4) && !freeze;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: LEFT + i * (BAR_W + GAP),
              bottom: 1080 - BASELINE_Y,
              width: BAR_W,
              height: Math.max(0, h * MAX_H),
              background: isFault ? COLORS.fault : COLORS.ink,
            }}
          />
        );
      })}

      {/* Plant median line (dashed ink) */}
      <div
        style={{
          position: "absolute",
          left: LEFT,
          top: medianY,
          width: PLOT_W * medianDraw,
          borderTop: `4px dashed ${COLORS.ink}`,
          opacity: 0.9,
        }}
      />
      {medianDraw > 0.95 ? (
        <div
          style={{
            position: "absolute",
            left: LEFT + PLOT_W - 240,
            top: medianY - 44,
            ...label(18),
            background: COLORS.lemon,
            color: COLORS.ink,
            padding: "6px 12px",
          }}
        >
          Plant median
        </div>
      ) : null}

      {/* Baseline */}
      <div
        style={{
          position: "absolute",
          left: LEFT - 20,
          top: BASELINE_Y,
          width: PLOT_W + 40,
          borderTop: `2px solid ${COLORS.ink}`,
        }}
      />
    </>
  );
};

/** Simple cloud built from overlapping circles (emoji are render-unsafe). */
const Cloud: React.FC<{ x: number; opacity: number }> = ({ x, opacity }) => (
  <div style={{ position: "absolute", left: x, top: 250, opacity }}>
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
          background: COLORS.muted,
          opacity: 0.55,
        }}
      />
    ))}
  </div>
);

/**
 * THE BIG BEAT: freeze + dim everything, keep the bad bar pulsing red, and
 * spring in a giant 0.55 with the "below 1.0 = trouble" tag. Held 4+ s.
 */
const FreezeBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const dim = interpolate(
    frame,
    [sec(T_FREEZE_IN), sec(T_FREEZE_IN + 0.6), sec(T_FREEZE_OUT), sec(T_FREEZE_OUT + 0.8)],
    [0, 0.92, 0.92, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  if (dim <= 0) return null;

  // Deterministic red pulse on the bad bar.
  const pulse = 0.6 + 0.4 * Math.sin(((frame - sec(T_FREEZE_IN)) / fps) * Math.PI * 2.2);

  const numIn = spring({
    frame: Math.max(0, frame - sec(T_FREEZE_IN + 0.5)),
    fps,
    config: { damping: 12, stiffness: 90, mass: 1.0 },
  });
  const tagIn = spring({
    frame: Math.max(0, frame - sec(T_FREEZE_IN + 1.1)),
    fps,
    config: { damping: 13, stiffness: 140, mass: 0.7 },
  });

  const barH = BASE[FAULT_IDX] * 0.55 * MAX_H;
  const barX = LEFT + FAULT_IDX * (BAR_W + GAP);

  const inner = Math.min(1, dim / 0.92);

  return (
    <AbsoluteFill>
      {/* Paper dim layer over everything else. */}
      <AbsoluteFill style={{ background: COLORS.paper, opacity: dim }} />

      <AbsoluteFill style={{ opacity: inner }}>
        {/* The bad bar, re-drawn on top, pulsing red with a halo ring. */}
        <div
          style={{
            position: "absolute",
            left: barX,
            bottom: 1080 - BASELINE_Y,
            width: BAR_W,
            height: barH,
            background: COLORS.fault,
            opacity: 0.55 + 0.45 * pulse,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: barX - 26 - 10 * pulse,
            bottom: 1080 - BASELINE_Y - 14,
            width: BAR_W + 52 + 20 * pulse,
            height: barH + 36 + 14 * pulse,
            border: `6px solid ${COLORS.fault}`,
            opacity: 0.5 + 0.5 * pulse,
          }}
        />
        {/* Baseline stays visible for context. */}
        <div
          style={{
            position: "absolute",
            left: LEFT - 20,
            top: BASELINE_Y,
            width: PLOT_W + 40,
            borderTop: `2px solid ${COLORS.ink}`,
            opacity: 0.4,
          }}
        />

        {/* HUGE 0.55 numeral. */}
        <div
          style={{
            position: "absolute",
            left: 150,
            top: 140,
            opacity: Math.min(1, numIn * 1.4),
            transform: `scale(${0.6 + 0.4 * numIn})`,
            transformOrigin: "left top",
          }}
        >
          <div
            style={{
              ...display(280),
              lineHeight: 0.85,
              color: COLORS.fault,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            0.55
          </div>
        </div>

        {/* Bold tag underneath. Sits ABOVE the pulsing red outline around
            the bar (halo top is ~y509) so the flagged bar stays visible. */}
        <div
          style={{
            position: "absolute",
            left: 158,
            top: 408,
            opacity: Math.min(1, tagIn * 1.4),
            transform: `translateY(${(1 - tagIn) * 50}px)`,
          }}
        >
          <div
            style={{
              display: "inline-block",
              background: COLORS.ink,
              color: COLORS.paper,
              padding: "14px 26px",
              ...display(50),
            }}
          >
            Below{" "}
            <span style={{ background: COLORS.lemon, color: COLORS.ink, padding: "0 10px" }}>
              1.0
            </span>{" "}
            = trouble
          </div>
          <div style={{ ...label(20), color: COLORS.ink, marginTop: 14, opacity: 0.8 }}>
            This bar just became a flag
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Scene3Method: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Formula banner.
  const formulaIn = spring({
    frame: Math.max(0, frame - sec(1.5)),
    fps,
    config: { damping: 200 },
  });

  // Cloud flies across the whole plant.
  const cloudX = interpolate(frame, [sec(T_CLOUD_START), sec(T_CLOUD_END)], [-260, 1980], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cloudVisible = frame >= sec(T_CLOUD_START) && frame <= sec(T_CLOUD_END);
  const cancelOpacity = interpolate(
    frame,
    [sec(T_CLOUD_START + 2), sec(T_CLOUD_START + 3), sec(T_CLOUD_END - 1), sec(T_CLOUD_END)],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Beat 5: curtailment trap card.
  const strike1 = interpolate(frame, [sec(T_TRAP + 1.5), sec(T_TRAP + 2.5)], [0, 100], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const strike2 = interpolate(frame, [sec(T_TRAP + 2.5), sec(T_TRAP + 3.5)], [0, 100], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const warnOpacity = interpolate(frame, [sec(T_TRAP + 4), sec(T_TRAP + 5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Judge note: THE TRAP card overlays the bars. Fade a paper scrim over the
  // diagram as the card lands so the bars read as grayed-out behind it and
  // the card is clearly the focus.
  const trapDim = interpolate(
    frame,
    [sec(T_TRAP - 0.4), sec(T_TRAP + 0.8)],
    [0, 0.82],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <NeoFrame index={3} tag="The method">
      <MethodDiagram frame={frame} />

      {/* Formula banner: ink panel, top center. */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: formulaIn,
          transform: `translateY(${(1 - formulaIn) * -40}px)`,
        }}
      >
        <div
          style={{
            background: COLORS.ink,
            color: COLORS.paper,
            padding: "18px 38px",
            fontFamily: FONT_MONO,
            fontSize: 36,
            letterSpacing: "0.02em",
            textTransform: "uppercase",
          }}
        >
          Peer ratio = inverter ÷ plant median{" "}
          <span style={{ opacity: 0.6, fontSize: 24 }}>(same timestamp)</span>
        </div>
      </div>

      {cloudVisible ? <Cloud x={cloudX} opacity={0.95} /> : null}

      {/* Cancellation proof readout */}
      <div
        style={{
          position: "absolute",
          top: 200,
          right: 90,
          opacity: cancelOpacity,
        }}
      >
        <StatPill delay={0} big variant="lemon" kicker="All dip together">
          Ratio stays 1.00
        </StatPill>
        <div style={{ ...label(18), color: COLORS.ink, marginTop: 14, opacity: 0.75 }}>
          Weather cancels out
        </div>
      </div>

      {/* Gray scrim over the bars while THE TRAP card is up. */}
      {trapDim > 0 ? (
        <AbsoluteFill style={{ background: COLORS.bg, opacity: trapDim }} />
      ) : null}

      {/* Curtailment trap: ink panel with struck-out rows. */}
      <Panel
        variant="ink"
        delay={sec(T_TRAP)}
        from="scale"
        style={{
          position: "absolute",
          top: 210,
          left: "50%",
          marginLeft: -480,
          width: 960,
          padding: "30px 44px",
        }}
      >
        <div style={{ ...label(18), opacity: 0.65, marginBottom: 16 }}>
          The trap
        </div>
        {[
          { text: "EVU curtailment: grid feed-in limited", strike: strike1 },
          { text: "DV curtailment: grid operator signal", strike: strike2 },
        ].map((row, i) => (
          <div
            key={i}
            style={{
              position: "relative",
              fontFamily: FONT_MONO,
              fontSize: 32,
              textTransform: "uppercase",
              letterSpacing: "0.03em",
              padding: "10px 0",
            }}
          >
            {row.text}
            <div
              style={{
                position: "absolute",
                left: 0,
                top: "50%",
                width: `${row.strike}%`,
                borderTop: `6px solid ${COLORS.fault}`,
              }}
            />
          </div>
        ))}
        <div
          style={{
            marginTop: 18,
            opacity: warnOpacity,
            display: "inline-block",
            background: COLORS.lemon,
            color: COLORS.ink,
            padding: "10px 18px",
            ...display(30),
          }}
        >
          Curtailment looks like a fault. Filter it out.
        </div>
      </Panel>

      {/* The big freeze beat renders on top of everything. */}
      <FreezeBeat />
    </NeoFrame>
  );
};
