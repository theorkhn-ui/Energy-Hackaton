import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { StatPill } from "../components/StatPill";
import { COLORS, FONT, FONT_MONO } from "../theme";
import { sec } from "../timing";

const DURATION = sec(35);

/**
 * Scene 6 (2:15–2:50) — Finding 3: failure in progress.
 * Section-collapse chart pushing in; pulsing ACTIVE badge; outage-hours
 * counter ticking up to ~840; fault-matrix card slides in for the
 * "classifying the error codes" beat.
 */
export const Scene6ActiveCollapse: React.FC = () => {
  const frame = useCurrentFrame();

  // Pulsing ACTIVE badge (deterministic sine, no CSS animation).
  const pulse = 0.75 + 0.25 * Math.sin((frame / 30) * Math.PI * 2);

  // Outage-hours counter ticks up.
  const hours = Math.round(
    interpolate(frame, [sec(11), sec(18)], [0, 840], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const counterVisible = frame >= sec(11);

  // Fault-matrix card slides in from the right for the root-cause beat.
  const matrixIn = interpolate(frame, [sec(24), sec(26)], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <KenBurnsImage
        src={staticFile("section_collapse.png")}
        durationInFrames={DURATION}
        startScale={1.0}
        endScale={1.14}
        panX={-20}
        maxHeight={760}
      />

      {/* ACTIVE badge — pulsing red */}
      <div
        style={{
          position: "absolute",
          top: 52,
          left: 64,
          display: "flex",
          gap: 24,
          alignItems: "center",
        }}
      >
        <div
          style={{
            background: COLORS.fault,
            opacity: pulse,
            color: "#ffffff",
            fontWeight: 900,
            fontSize: 40,
            borderRadius: 10,
            padding: "10px 26px",
            letterSpacing: 2,
          }}
        >
          ● ACTIVE
        </div>
        <StatPill delay={sec(1.5)} color={COLORS.fault}>
          sections 01.08 + 01.09 — collapsing since Aug 2025
        </StatPill>
      </div>

      <div style={{ position: "absolute", top: 160, left: 64 }}>
        <StatPill delay={sec(7)} color={COLORS.warn}>
          2 still below 0.7; one recovered in May
        </StatPill>
      </div>

      {/* Outage-hours ticking counter */}
      {counterVisible ? (
        <div
          style={{
            position: "absolute",
            top: 52,
            right: 64,
            background: COLORS.bgPanel,
            border: `2px solid ${COLORS.fault}`,
            borderRadius: 12,
            padding: "14px 30px",
            textAlign: "right",
          }}
        >
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 64,
              fontWeight: 800,
              color: COLORS.fault,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {hours} h
          </div>
          <div style={{ color: COLORS.textDim, fontSize: 26, fontWeight: 600 }}>
            outage hours / 365d — each (~740–840)
          </div>
        </div>
      ) : null}

      {/* Fault matrix — error-code classification in progress */}
      <div
        style={{
          position: "absolute",
          right: 64,
          top: 300,
          opacity: matrixIn,
          transform: `translateX(${(1 - matrixIn) * 320}px)`,
        }}
      >
        <div
          style={{
            background: "#ffffff",
            borderRadius: 12,
            padding: 10,
            boxShadow: "0 18px 60px rgba(0,0,0,0.55)",
          }}
        >
          <Img
            src={staticFile("fault_matrix.png")}
            style={{ width: 560, display: "block", borderRadius: 6 }}
          />
        </div>
        <div
          style={{
            marginTop: 10,
            color: COLORS.text,
            fontSize: 26,
            fontWeight: 600,
            textAlign: "center",
            background: COLORS.captionBg,
            borderRadius: 8,
            padding: "6px 14px",
          }}
        >
          error-code classification → root cause (in progress)
        </div>
      </div>
    </AbsoluteFill>
  );
};
