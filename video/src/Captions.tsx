import React from "react";
import type { Caption } from "@remotion/captions";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS, FONT } from "./theme";
import { FPS, SCENE_DURATIONS, SCENE_STARTS } from "./timing";

/**
 * Burned-in captions, always on (judges may watch muted).
 * Narration text is VERBATIM from docs/VIDEO_STORYBOARD.md, pre-split into
 * max-2-line chunks. Timing within each scene is distributed proportionally
 * to word count at ~140 wpm, anchored to the same SCENE_STARTS constants the
 * scenes use — retime a scene and its captions follow.
 *
 * Once the real voiceover is recorded, fine-tune by replacing
 * buildCaptions() with hand-timed Caption[] (see VoiceoverNote.md).
 */
const SCENE_NARRATION: string[][] = [
  // Scene 1 — cold open (10s)
  [
    "Forty-two of the last forty-six inverter failures at this solar plant",
    "were visible in the data — a median of fifty-one days",
    "before anyone opened a ticket.",
  ],
  // Scene 2 — the problem (25s)
  [
    "This is nine point four years of real monitoring data",
    "from a sixty-five-inverter PV plant.",
    "A reading every five minutes, from every inverter.",
    "And hidden inside it: failures the operator's own monitoring never caught.",
    "We're team Syz, and for Enerparc's digital twin challenge,",
    "we built the layer that catches them.",
  ],
  // Scene 3 — method (35s)
  [
    "Our method is deliberately simple.",
    "Every five minutes, we compare each inverter",
    "to the plant median at that exact moment.",
    "Clouds, seasons, soiling rain — they hit every inverter at once,",
    "so they cancel out.",
    "What's left is a clean peer ratio:",
    "one point zero means healthy, anything below means trouble.",
    "One trap, though: grid curtailment looks exactly like a fault.",
    "We filter the EVU and DV curtailment signals out explicitly —",
    "skip that step, and you'll flag perfectly healthy inverters all day.",
  ],
  // Scene 4 — finding 1: predictive power (35s)
  [
    "But does it actually work?",
    "We back-tested against the plant's real service history.",
    "Of forty-six inverter-specific tickets — defective capacitors,",
    "defective boards, insulation faults —",
    "forty-two were preceded by our performance flag.",
    "Median lead time: fifty-one and a half days.",
    "That's seven weeks of warning.",
    "Seven weeks to order the part, schedule the crew,",
    "and fix it on your terms instead of the inverter's.",
  ],
  // Scene 5 — finding 2: the invisible fault (30s)
  [
    "And sometimes there is no ticket at all.",
    "Inverter zero-one — zero-three — zero-one-eight",
    "has been running at seventy percent of its peers for a full year.",
    "No service ticket exists. Nobody noticed.",
    "That's roughly four hundred and thirty euros a year",
    "quietly evaporating — from a single inverter.",
    "Our flag caught it from the data alone.",
  ],
  // Scene 6 — finding 3: failure in progress (35s)
  [
    "This one isn't history — it's happening right now.",
    "Sections one-oh-eight and one-oh-nine",
    "started collapsing in August twenty twenty-five.",
    "Today, several inverters there are producing",
    "at just thirty-five to fifty percent of their peers,",
    "each with roughly seven hundred fifty to eight hundred forty",
    "outage hours in the last twelve months.",
    "We're classifying the error codes to pin down the root cause.",
    "If we were on call, this would be ticket number one, written today.",
  ],
  // Scene 7 — bonus: stale asset register (20s)
  [
    "One bonus finding: about eight inverters",
    "sit permanently above a ratio of one point one.",
    "That's not overperformance — that's a stale kilowatt-peak value",
    "in the asset register.",
    "Fix the master data, and every yield calculation",
    "on this plant gets sharper.",
  ],
  // Scene 8 — honest limitation (10s)
  [
    "To be fully honest about the limits:",
    "because we measure inverters against each other,",
    "a plant-wide degradation that hits every inverter equally",
    "would be invisible to this method.",
  ],
  // Scene 9 — close (30s)
  [
    "We're Orkhan and Maxat — team Syz.",
    "In one weekend, with your data, we found one failure in progress,",
    "one failure nobody had noticed,",
    "and a seven-week early-warning signal",
    "validated against your own ticket history.",
    "With Enerparc, our next steps are clear:",
    "wire this into live monitoring,",
    "finish error-code root-cause classification,",
    "and auto-draft the service tickets.",
    "Less downtime, caught earlier —",
    "with math your engineers can audit line by line.",
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
 * Bottom-center, max 2 lines, white on a 60%-opacity dark band
 * (storyboard tech spec). Stat overlays stay in the upper two-thirds,
 * so the bottom band is reserved for these.
 */
export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const ms = (frame / FPS) * 1000;
  const active = captions.find((c) => ms >= c.startMs && ms < c.endMs);

  if (!active) {
    return null;
  }

  return (
    <AbsoluteFill
      style={{ justifyContent: "flex-end", alignItems: "center" }}
    >
      <div
        style={{
          marginBottom: 48,
          maxWidth: 1560,
          background: COLORS.captionBg,
          color: "#ffffff",
          fontFamily: FONT,
          fontWeight: 600,
          fontSize: 42,
          lineHeight: 1.3,
          textAlign: "center",
          padding: "14px 38px",
          borderRadius: 10,
        }}
      >
        {active.text}
      </div>
    </AbsoluteFill>
  );
};
