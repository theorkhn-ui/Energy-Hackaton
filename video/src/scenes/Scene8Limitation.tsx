import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { COLORS, display, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 8 (3:10-3:29) — The limit, and how we close it.
 * First the honest limitation (our peer ratio is relative). Then the reveal:
 * an absolute twin, each inverter vs its own healthy baseline. Then the proof,
 * built natively: dim EVERY inverter by 10% and the relative metric never
 * moves (blind) while the absolute twin drops the full 10% (caught).
 * Numbers mirror runs/plant_a/twin/twin_uniform_loss.png.
 */

// Proof-bar geometry on the 1920x1080 canvas. Baseline sits high enough that
// the group labels + verdict chips below it clear the caption bar (~y940).
const BASE_Y = 726;
const UNIT = 320; // px height for a value of 1.0
const BAR_W = 70;
const IN_GAP = 24;
const GROUP_A_X = 1180;
const GROUP_B_X = 1520;
const REF_Y = BASE_Y - UNIT;

const Bar: React.FC<{
  x: number;
  value: number;
  delay: number;
  color: string;
  valueLabel: string;
}> = ({ x, value, delay, color, valueLabel }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 16, stiffness: 150, mass: 0.7 },
  });
  const h = value * UNIT * pop;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: x,
          top: BASE_Y - h,
          width: BAR_W,
          height: h,
          background: color,
          border: `1.5px solid ${COLORS.ink}`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: x - 10,
          top: BASE_Y - h - 42,
          width: BAR_W + 20,
          textAlign: "center",
          ...display(30),
          color,
          opacity: Math.min(1, pop * 1.6),
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {valueLabel}
      </div>
    </>
  );
};

const Verdict: React.FC<{
  centerX: number;
  text: string;
  delay: number;
  lemon?: boolean;
}> = ({ centerX, text, delay, lemon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 14, stiffness: 160, mass: 0.6 } });
  return (
    <div
      style={{
        position: "absolute",
        left: centerX - 150,
        top: BASE_Y + 92,
        width: 300,
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(1, pop * 1.6),
        transform: `translateY(${(1 - pop) * 20}px)`,
      }}
    >
      <div
        style={{
          ...label(20),
          background: lemon ? COLORS.lemon : COLORS.paper,
          color: COLORS.ink,
          border: `1.5px solid ${COLORS.ink}`,
          padding: "10px 18px",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const Scene8Limitation: React.FC = () => {
  const frame = useCurrentFrame();

  const headIn = interpolate(frame, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Reference "1.0 = healthy" line draws across the plot.
  const refDraw = interpolate(frame, [sec(5), sec(6.5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const groupCenterA = GROUP_A_X + BAR_W + IN_GAP / 2;
  const groupCenterB = GROUP_B_X + BAR_W + IN_GAP / 2;

  return (
    <NeoFrame index={8} tag="The limit + the fix" staticGrid>
      <AbsoluteFill>
        {/* Left column: the honest limit, then the reveal. */}
        <div style={{ position: "absolute", left: 96, top: 220, width: 760 }}>
          <div
            style={{
              ...label(22),
              color: COLORS.ink,
              opacity: 0.7 * headIn,
              marginBottom: 18,
            }}
          >
            One honest limit
          </div>
          <div
            style={{
              ...display(50),
              color: COLORS.ink,
              opacity: headIn,
              lineHeight: 1.04,
            }}
          >
            Our peer ratio is{" "}
            <span style={{ background: COLORS.lemon, padding: "0 8px" }}>
              relative
            </span>
            . A loss hitting every inverter at once could hide.
          </div>

          {/* The reveal: absolute twin. */}
          <Panel
            variant="ink"
            delay={sec(5)}
            from="left"
            style={{ marginTop: 46, padding: "26px 32px", maxWidth: 720 }}
          >
            <div style={{ ...label(18), opacity: 0.65, marginBottom: 10 }}>
              So we built
            </div>
            <div style={{ ...display(46) }}>
              An{" "}
              <span style={{ background: COLORS.lemon, color: COLORS.ink, padding: "0 8px" }}>
                absolute twin
              </span>
            </div>
            <div style={{ ...label(18), marginTop: 14, opacity: 0.85, lineHeight: 1.4 }}>
              Each inverter vs its own healthy baseline, from irradiance + module
              temperature. R² 0.957.
            </div>
          </Panel>
        </div>

        {/* Right column: the native uniform-loss proof. */}
        <div
          style={{
            position: "absolute",
            left: 980,
            top: 150,
            ...label(20),
            color: COLORS.ink,
            opacity: refDraw,
          }}
        >
          Stress test — dim{" "}
          <span style={{ background: COLORS.fault, color: COLORS.paper, padding: "2px 8px" }}>
            every inverter -10%
          </span>
        </div>

        {/* 1.0 = healthy reference line. */}
        <div
          style={{
            position: "absolute",
            left: GROUP_A_X - 30,
            top: REF_Y,
            width: (GROUP_B_X + 2 * BAR_W + IN_GAP) - (GROUP_A_X - 30),
            transform: `scaleX(${refDraw})`,
            transformOrigin: "left",
            borderTop: `3px dashed ${COLORS.ink}`,
            opacity: 0.6,
          }}
        />
        {refDraw > 0.9 ? (
          <div
            style={{
              position: "absolute",
              left: GROUP_B_X + 2 * BAR_W + IN_GAP - 6,
              top: REF_Y - 30,
              ...label(16),
              color: COLORS.ink,
              opacity: 0.7,
            }}
          >
            1.0 = healthy
          </div>
        ) : null}

        {/* Baseline rule. */}
        <div
          style={{
            position: "absolute",
            left: GROUP_A_X - 30,
            top: BASE_Y,
            width: (GROUP_B_X + 2 * BAR_W + IN_GAP) - (GROUP_A_X - 30),
            borderTop: `2px solid ${COLORS.ink}`,
          }}
        />

        {/* Group A: relative peer metric — both bars 1.00 (blind). */}
        <Bar x={GROUP_A_X} value={1.0} delay={sec(6)} color={COLORS.ink} valueLabel="1.00" />
        <Bar x={GROUP_A_X + BAR_W + IN_GAP} value={1.0} delay={sec(9)} color={COLORS.fault} valueLabel="1.00" />
        <GroupLabel centerX={groupCenterA} top1="Relative" top2="peer metric" delay={sec(6)} />
        <Verdict centerX={groupCenterA} text="UNCHANGED — BLIND" delay={sec(12)} />

        {/* Group B: absolute twin — after-bar drops to 0.90 (caught). */}
        <Bar x={GROUP_B_X} value={1.0} delay={sec(6.4)} color={COLORS.ink} valueLabel="1.00" />
        <Bar x={GROUP_B_X + BAR_W + IN_GAP} value={0.9} delay={sec(9.4)} color={COLORS.fault} valueLabel="0.90" />
        <GroupLabel centerX={groupCenterB} top1="Absolute" top2="twin" delay={sec(6.4)} />
        <Verdict centerX={groupCenterB} text="DROPS 10% — CAUGHT" delay={sec(12.6)} lemon />
      </AbsoluteFill>
    </NeoFrame>
  );
};

const GroupLabel: React.FC<{ centerX: number; top1: string; top2: string; delay: number }> = ({
  centerX,
  top1,
  top2,
  delay,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: centerX - 150,
        top: BASE_Y + 22,
        width: 300,
        textAlign: "center",
        ...label(18),
        color: COLORS.ink,
        opacity: o,
        lineHeight: 1.25,
      }}
    >
      {top1}
      <br />
      {top2}
    </div>
  );
};
