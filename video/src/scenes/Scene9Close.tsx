import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONT } from "../theme";
import { sec } from "../timing";

/**
 * Scene 9 (3:20–3:50) — Close: team + next steps.
 * Split screen with team cards (placeholder initials — swap in real photos,
 * see README), 3-item roadmap springing in, then the end card holds the
 * final 3 seconds so a paused last frame is still useful.
 */

const TeamCard: React.FC<{ initial: string; name: string; delay: number }> = ({
  initial,
  name,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 15, stiffness: 110, mass: 0.8 },
  });

  return (
    <div
      style={{
        opacity: pop,
        transform: `translateY(${(1 - pop) * 50}px)`,
        background: COLORS.bgPanel,
        border: `1px solid ${COLORS.bgPanelBorder}`,
        borderRadius: 18,
        width: 380,
        padding: "44px 0 32px",
        textAlign: "center",
        boxShadow: "0 18px 60px rgba(0,0,0,0.5)",
      }}
    >
      {/* Placeholder avatar — replace with team photo via <Img src={staticFile("orkhan.jpg")} /> */}
      <div
        style={{
          width: 170,
          height: 170,
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.healthy})`,
          margin: "0 auto 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 84,
          fontWeight: 900,
          color: "#0b1220",
        }}
      >
        {initial}
      </div>
      <div style={{ color: COLORS.text, fontSize: 44, fontWeight: 800 }}>
        {name}
      </div>
    </div>
  );
};

const ROADMAP = [
  "① Live monitoring integration",
  "② Error-code root-cause classification",
  "③ Auto-drafted service tickets",
];

export const Scene9Close: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // End card takes over for the final 3s (plus a short crossfade).
  const endCardOpacity = interpolate(frame, [sec(25.5), sec(27)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      {/* Main part: team + roadmap */}
      <AbsoluteFill
        style={{
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "center",
          gap: 80,
        }}
      >
        <div style={{ display: "flex", gap: 40 }}>
          <TeamCard initial="O" name="Orkhan" delay={10} />
          <TeamCard initial="M" name="Maxat" delay={22} />
        </div>

        <div style={{ width: 760 }}>
          <div
            style={{
              color: COLORS.textDim,
              fontSize: 34,
              fontWeight: 700,
              letterSpacing: 3,
              marginBottom: 28,
            }}
          >
            NEXT STEPS — WITH ENERPARC
          </div>
          {ROADMAP.map((item, i) => {
            const delay = sec(8) + i * sec(2.2);
            const pop = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 14, stiffness: 120, mass: 0.7 },
            });
            return (
              <div
                key={item}
                style={{
                  opacity: pop,
                  transform: `translateX(${(1 - pop) * 70}px)`,
                  background: COLORS.bgPanel,
                  border: `1px solid ${COLORS.bgPanelBorder}`,
                  borderLeft: `8px solid ${COLORS.accent}`,
                  borderRadius: 12,
                  padding: "20px 30px",
                  marginBottom: 22,
                  color: COLORS.text,
                  fontSize: 40,
                  fontWeight: 700,
                }}
              >
                {item}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* End card — holds the final 3 seconds */}
      <AbsoluteFill
        style={{
          opacity: endCardOpacity,
          background: COLORS.bg,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              color: COLORS.text,
              fontSize: 120,
              fontWeight: 900,
              letterSpacing: 4,
            }}
          >
            Team Syz
          </div>
          <div
            style={{
              color: COLORS.textDim,
              fontSize: 44,
              fontWeight: 600,
              marginTop: 18,
            }}
          >
            Orkhan + Maxat · theorkhn@gmail.com
          </div>
          <div
            style={{
              color: COLORS.accent,
              fontSize: 36,
              fontWeight: 700,
              marginTop: 40,
            }}
          >
            Challenge #2.1 — Digital Twin of a Solar Plant
          </div>
          <div
            style={{
              color: COLORS.textDim,
              fontSize: 30,
              marginTop: 12,
            }}
          >
            Energy Hack Munich 2026
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
