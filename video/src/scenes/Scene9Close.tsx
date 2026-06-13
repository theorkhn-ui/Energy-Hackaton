import React, { useState } from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { NeoFrame } from "../components/NeoFrame";
import { StatPill } from "../components/StatPill";
import { COLORS, display, FONT_MONO, label } from "../theme";
import { sec } from "../timing";

/**
 * Scene 9 (3:20-3:50), Close: team + next steps.
 * Real photos (public/orkhan.png, public/maxat.jpg) in bold ink-framed
 * blocks. If a file is missing at render time, <Img onError> flips the card
 * to the initial-block fallback so the render never breaks (see README).
 * Roadmap blocks spring in staggered; the end card holds the final 3 s.
 */

const PHOTO_W = 380;
const PHOTO_H = 420;

const TeamCard: React.FC<{
  file: string;
  initial: string;
  name: string;
  role: string;
  delay: number;
}> = ({ file, initial, name, role, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [failed, setFailed] = useState(false);

  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 15, stiffness: 110, mass: 0.8 },
  });

  return (
    <div
      style={{
        opacity: Math.min(1, pop * 1.5),
        transform: `translateY(${(1 - pop) * 70}px)`,
        width: PHOTO_W,
      }}
    >
      {/* Bold framed photo block: thick ink frame, lemon backing plate. */}
      <div style={{ position: "relative" }}>
        <div
          style={{
            position: "absolute",
            left: 14,
            top: 14,
            width: PHOTO_W,
            height: PHOTO_H,
            background: COLORS.lemon,
            border: `1.5px solid ${COLORS.ink}`,
          }}
        />
        <div
          style={{
            position: "relative",
            width: PHOTO_W,
            height: PHOTO_H,
            border: `5px solid ${COLORS.ink}`,
            background: COLORS.stage,
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {failed ? (
            // Fallback: initial block (drop the jpgs into public/ to replace).
            <div
              style={{
                ...display(180),
                color: COLORS.paper,
                lineHeight: 1,
              }}
            >
              {initial}
            </div>
          ) : (
            <Img
              src={staticFile(file)}
              onError={() => setFailed(true)}
              pauseWhenLoading={false}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "grayscale(0.25) contrast(1.05)",
              }}
            />
          )}
          <div
            style={{
              position: "absolute",
              top: 10,
              left: 10,
              ...label(14),
              background: COLORS.paper,
              color: COLORS.ink,
              padding: "4px 10px",
            }}
          >
            {role}
          </div>
        </div>
      </div>

      {/* Name plate. */}
      <div
        style={{
          marginTop: 26,
          background: COLORS.ink,
          color: COLORS.paper,
          padding: "14px 22px",
          ...display(44),
          display: "inline-block",
        }}
      >
        {name}
      </div>
    </div>
  );
};

const ROADMAP = [
  { num: "01", text: "Live monitoring integration" },
  { num: "02", text: "Root-cause classification" },
  { num: "03", text: "Auto-drafted service tickets" },
];

export const Scene9Close: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // End card takes over for the final ~4s.
  const endCardOpacity = interpolate(frame, [sec(25), sec(26.5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const endPop = spring({
    frame: Math.max(0, frame - sec(25.5)),
    fps,
    config: { damping: 16, stiffness: 90, mass: 1 },
  });

  return (
    <NeoFrame index={9} tag="Team + next steps">
      {/* Main part: team + roadmap */}
      <AbsoluteFill
        style={{
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "center",
          gap: 90,
        }}
      >
        <div style={{ display: "flex", gap: 64 }}>
          <TeamCard
            file="orkhan.png"
            initial="O"
            name="Orkhan"
            role="Team Syz"
            delay={8}
          />
          <TeamCard
            file="maxat.jpg"
            initial="M"
            name="Maxat"
            role="Team Syz"
            delay={20}
          />
        </div>

        <div style={{ width: 700 }}>
          <div style={{ ...label(22), color: COLORS.ink, marginBottom: 30 }}>
            Next steps with Enerparc
          </div>
          {ROADMAP.map((item, i) => {
            const delay = sec(7) + i * sec(2.2);
            const pop = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 14, stiffness: 120, mass: 0.7 },
            });
            const variantBg = i === 2 ? COLORS.lemon : COLORS.ink;
            const variantFg = i === 2 ? COLORS.ink : COLORS.paper;
            return (
              <div
                key={item.num}
                style={{
                  opacity: Math.min(1, pop * 1.5),
                  transform: `translateX(${(1 - pop) * 90}px)`,
                  display: "flex",
                  alignItems: "stretch",
                  marginBottom: 20,
                  border: `1.5px solid ${COLORS.ink}`,
                  boxShadow: `${8 * pop}px ${8 * pop}px 0 0 ${COLORS.ink}`,
                }}
              >
                <div
                  style={{
                    background: variantBg,
                    color: variantFg,
                    fontFamily: FONT_MONO,
                    fontSize: 34,
                    padding: "20px 24px",
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {item.num}
                </div>
                <div
                  style={{
                    background: COLORS.paper,
                    color: COLORS.ink,
                    ...display(36),
                    padding: "22px 28px",
                    display: "flex",
                    alignItems: "center",
                    flex: 1,
                  }}
                >
                  {item.text}
                </div>
              </div>
            );
          })}

          <div style={{ marginTop: 34 }}>
            <StatPill delay={sec(14)} variant="lemon" kicker="Found in one day">
              1 live failure + 1 invisible fault + 7 weeks warning
            </StatPill>
          </div>
        </div>
      </AbsoluteFill>

      {/* End card: ink stage, holds the final seconds. */}
      <AbsoluteFill
        style={{
          opacity: endCardOpacity,
          background: COLORS.stage,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            textAlign: "center",
            transform: `scale(${0.92 + 0.08 * endPop})`,
          }}
        >
          <div style={{ ...display(150), color: COLORS.paper }}>
            Team{" "}
            <span
              style={{
                background: COLORS.lemon,
                color: COLORS.ink,
                padding: "0 18px",
              }}
            >
              Syz
            </span>
          </div>
          <div
            style={{
              ...label(26),
              color: COLORS.paper,
              marginTop: 34,
              opacity: 0.9,
            }}
          >
            Orkhan + Maxat / theorkhn@gmail.com
          </div>
          <div
            style={{
              ...label(20),
              color: COLORS.paper,
              marginTop: 22,
              opacity: 0.6,
            }}
          >
            Challenge #2.1: Digital twin of a solar plant / Energy Hack Munich
            2026
          </div>
        </div>
      </AbsoluteFill>
    </NeoFrame>
  );
};
