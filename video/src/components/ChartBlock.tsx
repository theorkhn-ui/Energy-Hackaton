import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { COLORS, FONT_MONO } from "../theme";

type HighlightShape = {
  /** "rect" draws a bold rectangle, "ellipse" a bold ellipse. */
  shape: "rect" | "ellipse";
  /** Region in fractions of the chart box (0..1). */
  x: number;
  y: number;
  w: number;
  h: number;
  /** Frame (scene-relative) at which the stroke starts drawing. */
  at: number;
  color?: string;
  /** Optional mono tag rendered at the top-left of the highlight. */
  tag?: string;
};

type Props = {
  src: string;
  durationInFrames: number;
  /** Wipe direction for the masked reveal. */
  wipeFrom?: "left" | "right" | "top" | "bottom";
  /** Frames the wipe takes (starts at frame 0 of the parent sequence). */
  wipeDuration?: number;
  startScale?: number;
  endScale?: number;
  panX?: number;
  panY?: number;
  width?: number;
  height?: number;
  /** Bold outlines drawn around key regions of the PNG. */
  highlights?: HighlightShape[];
  /** Mono label riveted to the top edge of the block. */
  caption?: string;
  style?: React.CSSProperties;
};

/**
 * Neo-Grid Bold chart block: the matplotlib PNG sits in a paper panel with a
 * thick ink frame. It enters with a masked wipe (animated clip-path), then
 * pans/zooms inside the frame, and bold highlight shapes draw themselves
 * around the key region of the image (stroke-dash animation).
 */
export const ChartBlock: React.FC<Props> = ({
  src,
  durationInFrames,
  wipeFrom = "left",
  wipeDuration = 28,
  startScale = 1.0,
  endScale = 1.08,
  panX = 0,
  panY = 0,
  width = 1560,
  height = 760,
  highlights = [],
  caption,
  style,
}) => {
  const frame = useCurrentFrame();

  const wipe = interpolate(frame, [0, wipeDuration], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const remain = (1 - wipe) * 100;
  const clipPath =
    wipeFrom === "left"
      ? `inset(0 ${remain}% 0 0)`
      : wipeFrom === "right"
        ? `inset(0 0 0 ${remain}%)`
        : wipeFrom === "top"
          ? `inset(0 0 ${remain}% 0)`
          : `inset(${remain}% 0 0 0)`;

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(progress, [0, 1], [startScale, endScale]);
  const tx = interpolate(progress, [0, 1], [0, panX]);
  const ty = interpolate(progress, [0, 1], [0, panY]);

  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", ...style }}
    >
      <div style={{ position: "relative", clipPath }}>
        <div
          style={{
            width,
            height,
            background: COLORS.paper,
            border: `3px solid ${COLORS.ink}`,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 14,
              transform: `scale(${scale}) translate(${tx}px, ${ty}px)`,
            }}
          >
            <Img
              src={src}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
              }}
            />
          </div>

          {/* Animated highlight outlines over the PNG. */}
          <svg
            width={width}
            height={height}
            style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
          >
            {highlights.map((hl, i) => {
              const drawn = interpolate(frame, [hl.at, hl.at + 22], [0, 1], {
                easing: Easing.bezier(0.45, 0, 0.55, 1),
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              });
              if (drawn <= 0) return null;
              const c = hl.color ?? COLORS.fault;
              const px = hl.x * width;
              const py = hl.y * height;
              const pw = hl.w * width;
              const ph = hl.h * height;
              const common = {
                fill: "none",
                stroke: c,
                strokeWidth: 7,
                pathLength: 1,
                strokeDasharray: 1,
                strokeDashoffset: 1 - drawn,
              } as const;
              return (
                <g key={i}>
                  {hl.shape === "rect" ? (
                    <rect x={px} y={py} width={pw} height={ph} {...common} />
                  ) : (
                    <ellipse
                      cx={px + pw / 2}
                      cy={py + ph / 2}
                      rx={pw / 2}
                      ry={ph / 2}
                      {...common}
                    />
                  )}
                  {hl.tag && drawn > 0.9 ? (
                    <g>
                      <rect
                        x={px}
                        y={py - 40}
                        width={hl.tag.length * 13.5 + 24}
                        height={34}
                        fill={c}
                      />
                      <text
                        x={px + 12}
                        y={py - 16}
                        fill={COLORS.paper}
                        fontFamily={FONT_MONO}
                        fontSize={20}
                        letterSpacing="0.08em"
                      >
                        {hl.tag.toUpperCase()}
                      </text>
                    </g>
                  ) : null}
                </g>
              );
            })}
          </svg>
        </div>

        {caption ? (
          <div
            style={{
              position: "absolute",
              top: -1.5,
              left: -1.5,
              background: COLORS.ink,
              color: COLORS.paper,
              fontFamily: FONT_MONO,
              fontSize: 18,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              padding: "8px 18px",
            }}
          >
            {caption}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
