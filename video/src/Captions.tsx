import React from "react";
import type { Caption } from "@remotion/captions";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS, FONT } from "./theme";
import { FPS, SCENE_DURATIONS, SCENE_STARTS } from "./timing";

/**
 * Burned-in captions, always on (judges may watch muted).
 * Plain student tone, short sentences, no em dashes. Verified numbers are
 * kept exactly: 42/46, 51.5 days, ~EUR 500/yr (INV 01.03.018), EUR 42k/yr at
 * risk, 9.4 years, 65 inverters, 71% nuisance, telemetry dead since 2019.
 *
 * Timing within each scene is distributed proportionally to word count,
 * anchored to the same SCENE_STARTS constants the scenes use. Retime a scene
 * and its captions follow. The full speaker-split transcript lives in
 * docs/VOICEOVER_TRANSCRIPT.md and matches this text word for word.
 */
const SCENE_NARRATION: string[][] = [
  // Scene 1: cold open (10s)
  [
    "Forty two of the last forty six inverter failures here were visible in the data first.",
    "A median of fifty one and a half days before anyone opened a ticket.",
  ],
  // Scene 2: the problem (25s)
  [
    "This is nine point four years of real monitoring data from a solar plant with sixty five inverters.",
    "A reading every five minutes, from every inverter.",
    "Hidden inside it are failures the plant's own monitoring never caught.",
    "We are team Syz. For Enerparc's digital twin challenge, we built the layer that catches them.",
  ],
  // Scene 3: method (35s). Caption order tracks the animation beats:
  // bars + median first, then the big 0.55 freeze, then the cloud, then the trap.
  [
    "Our method is simple on purpose.",
    "Every five minutes, we compare each inverter to the plant median.",
    "What is left is a peer ratio. One point zero means healthy.",
    "This one just dropped to zero point five five. Below one point zero means trouble.",
    "Clouds and seasons hit every inverter at once, so they cancel out.",
    "One trap though. Grid curtailment looks exactly like a fault.",
    "So we filter the EVU and DV signals out, or we would flag healthy inverters all day.",
  ],
  // Scene 4: finding 1, predictive power (35s)
  [
    "Does it actually work? We back tested it against the plant's real service history.",
    "Of forty six inverter specific tickets, things like broken capacitors, boards and insulation faults,",
    "forty two were flagged by our method in advance.",
    "The median lead time was fifty one and a half days.",
    "That is seven weeks of warning.",
    "Seven weeks to order the part, schedule the crew, and fix it on your terms instead of the inverter's.",
  ],
  // Scene 5: finding 2, the invisible fault (30s)
  [
    "Sometimes there is no ticket at all.",
    "Inverter zero one, zero three, zero one eight has been running at seventy percent of its peers for a full year.",
    "No service ticket exists. Nobody noticed.",
    "That is roughly five hundred euros a year, gone, from one inverter.",
    "Our flag caught it from the data alone.",
  ],
  // Scene 6: finding 3, failure in progress (35s)
  [
    "This one is not history. It is happening right now.",
    "Sections one zero eight and one zero nine started collapsing in August twenty twenty five.",
    "Two inverters are still below seventy percent of their peers.",
    "The worst unit lost around eight hundred forty hours in the last year.",
    "In total, about forty two thousand euros of yearly revenue is at risk.",
    "And no alarm fired, because the plant's error telemetry has been dead since twenty nineteen.",
    "If we were on call, this would be ticket number one, written today.",
  ],
  // Scene 7: bonus findings (20s)
  [
    "Two bonus findings.",
    "About eight inverters sit permanently above a ratio of one point one.",
    "That is not better hardware. That is a stale kilowatt peak value in the asset register.",
    "We also sorted the old alarms. Seventy one percent of them were nuisance.",
  ],
  // Scene 8: honest limitation (10s)
  [
    "One honest limit. We compare inverters to each other.",
    "A loss that hits all of them equally would be invisible to us.",
  ],
  // Scene 9: close (30s)
  [
    "We are Orkhan and Maxat, team Syz.",
    "In one day, with your data, we found a failure in progress, a fault nobody had noticed, and a seven week warning signal checked against your own tickets.",
    "Next, we want to wire this into live monitoring, finish the root cause work, and auto draft the service tickets.",
    "Less downtime, caught earlier, with math your engineers can check line by line.",
    "Thanks for watching.",
  ],
];

const buildCaptions = (): Caption[] => {
  const all: Caption[] = [];
  SCENE_NARRATION.forEach((chunks, sceneIdx) => {
    const sceneStartMs = (SCENE_STARTS[sceneIdx] / FPS) * 1000;
    const sceneDurMs = (SCENE_DURATIONS[sceneIdx] / FPS) * 1000;
    // Leave a small breath at the end of each scene.
    const usableMs = sceneDurMs * 0.96;
    const wordCounts = chunks.map((c) => c.split(/\s+/).length);
    const totalWords = wordCounts.reduce((a, b) => a + b, 0);

    let cursor = sceneStartMs;
    chunks.forEach((text, i) => {
      const durMs = (wordCounts[i] / totalWords) * usableMs;
      all.push({
        text,
        startMs: cursor,
        endMs: cursor + durMs,
        timestampMs: null,
        confidence: null,
      });
      cursor += durMs;
    });
  });
  return all;
};

export const captions: Caption[] = buildCaptions();

/**
 * Neo-Grid Bold caption bar: bottom-center ink band, paper text, zero
 * radius, a lemon block riveted to the left edge. Max two lines. Stat
 * overlays stay in the upper two-thirds, so this strip owns the bottom.
 */
export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const ms = (frame / FPS) * 1000;
  const active = captions.find((c) => ms >= c.startMs && ms < c.endMs);

  if (!active) {
    return null;
  }

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center" }}>
      <div
        style={{
          marginBottom: 44,
          maxWidth: 1560,
          display: "flex",
          alignItems: "stretch",
        }}
      >
        <div style={{ width: 18, background: COLORS.lemon, flexShrink: 0 }} />
        <div
          style={{
            background: COLORS.ink,
            color: COLORS.paper,
            fontFamily: FONT,
            fontWeight: 500,
            fontSize: 40,
            lineHeight: 1.3,
            textAlign: "left",
            padding: "14px 36px",
          }}
        >
          {active.text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
