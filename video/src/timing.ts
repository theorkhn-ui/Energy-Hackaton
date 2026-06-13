/**
 * Single source of truth for all scene timings.
 * Storyboard: docs/VIDEO_STORYBOARD.md, total 230s = 3:50 (hard cap 4:00).
 * Scenes and captions are BOTH driven by these constants, so retiming a scene
 * automatically retimes its captions.
 */
export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const sec = (s: number): number => Math.round(s * FPS);

export type SceneDef = {
  key: string;
  title: string;
  durationSec: number;
};

export const SCENES: readonly SceneDef[] = [
  { key: "scene1", title: "Cold open: the hook", durationSec: 10 },
  { key: "scene2", title: "The problem", durationSec: 25 },
  { key: "scene3", title: "Method (no math jargon)", durationSec: 35 },
  { key: "scene4", title: "Finding 1: predictive power", durationSec: 35 },
  { key: "scene5", title: "Finding 2: the invisible fault", durationSec: 30 },
  { key: "scene6", title: "Finding 3: failure in progress", durationSec: 35 },
  { key: "scene7", title: "Bonus: stale asset register", durationSec: 20 },
  { key: "scene8", title: "The limit, and how we close it", durationSec: 19 },
  { key: "scene9", title: "Close: team + next steps", durationSec: 30 },
] as const;

export const SCENE_DURATIONS: readonly number[] = SCENES.map((s) =>
  sec(s.durationSec),
);

export const SCENE_STARTS: readonly number[] = SCENE_DURATIONS.reduce<number[]>(
  (acc, _d, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + SCENE_DURATIONS[i - 1]);
    return acc;
  },
  [],
);

export const TOTAL_FRAMES: number = SCENE_DURATIONS.reduce((a, b) => a + b, 0);
// 7170 frames = 239 s = 3:59. Still under the 4:00 hard cap (Scene 8 grew from
// 10s to 19s to add the absolute-twin "limit + fix" beat).

/**
 * Voiceover: drop the narration file at video/public/voiceover.mp3 and flip
 * this to true. See VoiceoverNote.md.
 */
export const HAS_VOICEOVER = false;
export const VOICEOVER_FILE = "voiceover.mp3";
