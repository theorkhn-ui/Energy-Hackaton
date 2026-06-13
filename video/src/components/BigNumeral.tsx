import React from "react";
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, display, label } from "../theme";

type Props = {
  /** Frame (scene-relative) at which the numeral springs in. */
  delay: number;
  /** Final string, e.g. "42/46" or "0.55". */
  value: string;
  /** Count up from 0 to this number instead of showing `value` directly. */
  countTo?: number;
  countDecimals?: number;
  countDuration?: number;
  /** Suffix appended after the counted number, e.g. " H". */
  suffix?: string;
  size?: number;
  color?: string;
  /** Mono label under the numeral. */
  sub?: string;
  subColor?: string;
  style?: React.CSSProperties;
};

/**
 * Oversized Neo-Grid Bold stat numeral (156-320px Space Grotesk 700) with a
 * spring entrance and optional deterministic count-up.
 */
export const BigNumeral: React.FC<Props> = ({
  delay,
  value,
  countTo,
  countDecimals = 0,
  countDuration = 50,
  suffix = "",
  size = 156,
  color = COLORS.ink,
  sub,
  subColor,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 14, stiffness: 110, mass: 0.9 },
  });

  let text = value;
  if (countTo !== undefined) {
    const n = interpolate(frame, [delay, delay + countDuration], [0, countTo], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    text = n.toFixed(countDecimals) + suffix;
  }

  return (
    <div
      style={{
        opacity: Math.min(1, pop * 1.5),
        transform: `scale(${0.7 + 0.3 * pop})`,
        transformOrigin: "left bottom",
        ...style,
      }}
    >
      <div
        style={{
          ...display(size),
          lineHeight: 0.88,
          color,
          fontVariantNumeric: "tabular-nums",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
      {sub ? (
        <div
          style={{
            ...label(22),
            color: subColor ?? color,
            opacity: 0.8,
            marginTop: 14,
          }}
        >
          {sub}
        </div>
      ) : null}
    </div>
  );
};
