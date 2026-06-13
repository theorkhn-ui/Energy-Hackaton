import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { NeoFrame } from "../components/NeoFrame";
import { Panel } from "../components/Panel";
import { COLORS, display, label } from "../theme";
import { MethodDiagram } from "./Scene3Method";

/**
 * Scene 8 (3:10-3:20) — Honest limitation.
 * Calm beat: the Scene-3 method diagram, frozen and dimmed, behind a single
 * ink panel that slides up and lets the sentence land. Deliberately the
 * quietest scene in the video (sincerity beat), but still choreographed.
 */
export const Scene8Limitation: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <NeoFrame index={8} tag="Honest limit" staticGrid>
      <AbsoluteFill style={{ opacity: fadeIn }}>
        <AbsoluteFill style={{ opacity: 0.14 }}>
          <MethodDiagram frame={0} freeze />
        </AbsoluteFill>

        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <Panel
            variant="ink"
            delay={8}
            from="bottom"
            style={{ padding: "44px 60px", maxWidth: 1300 }}
          >
            <div style={{ ...label(20), opacity: 0.65, marginBottom: 18 }}>
              Known limit
            </div>
            <div style={{ ...display(56), lineHeight: 1.05 }}>
              We compare inverters{" "}
              <span
                style={{
                  background: COLORS.lemon,
                  color: COLORS.ink,
                  padding: "0 10px",
                }}
              >
                to each other
              </span>
            </div>
            <div
              style={{
                marginTop: 22,
                fontSize: 32,
                fontWeight: 400,
                lineHeight: 1.35,
                color: COLORS.paper,
              }}
            >
              A loss that hits every inverter equally is invisible to this
              method. That needs an absolute baseline.
            </div>
          </Panel>
        </AbsoluteFill>
      </AbsoluteFill>
    </NeoFrame>
  );
};
