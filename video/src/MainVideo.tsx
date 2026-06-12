import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { Captions } from "./Captions";
import { SceneFade } from "./components/SceneFade";
import { Scene1ColdOpen } from "./scenes/Scene1ColdOpen";
import { Scene2Problem } from "./scenes/Scene2Problem";
import { Scene3Method } from "./scenes/Scene3Method";
import { Scene4Leadtime } from "./scenes/Scene4Leadtime";
import { Scene5InvisibleFault } from "./scenes/Scene5InvisibleFault";
import { Scene6ActiveCollapse } from "./scenes/Scene6ActiveCollapse";
import { Scene7StaleRegister } from "./scenes/Scene7StaleRegister";
import { Scene8Limitation } from "./scenes/Scene8Limitation";
import { Scene9Close } from "./scenes/Scene9Close";
import { COLORS, FONT } from "./theme";
import {
  HAS_VOICEOVER,
  SCENE_DURATIONS,
  SCENE_STARTS,
  SCENES,
  TOTAL_FRAMES,
  VOICEOVER_FILE,
} from "./timing";

const SCENE_COMPONENTS: React.FC[] = [
  Scene1ColdOpen,
  Scene2Problem,
  Scene3Method,
  Scene4Leadtime,
  Scene5InvisibleFault,
  Scene6ActiveCollapse,
  Scene7StaleRegister,
  Scene8Limitation,
  Scene9Close,
];

/**
 * MainVideo — 1920x1080 @ 30fps, 6900 frames = 230s = 3:50.
 * Scene order/durations come from timing.ts (single source of truth);
 * captions are driven by the same constants.
 */
export const MainVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, fontFamily: FONT }}>
      {SCENE_COMPONENTS.map((SceneComponent, i) => (
        <Sequence
          key={SCENES[i].key}
          from={SCENE_STARTS[i]}
          durationInFrames={SCENE_DURATIONS[i]}
          name={`${i + 1} — ${SCENES[i].title}`}
        >
          <SceneFade
            durationInFrames={SCENE_DURATIONS[i]}
            // Scene 1 hard-cuts in from black; Scene 9 ends on the held card.
            fadeInFrames={i === 0 ? 0 : 10}
            fadeOutFrames={i === SCENE_COMPONENTS.length - 1 ? 0 : 10}
          >
            <SceneComponent />
          </SceneFade>
        </Sequence>
      ))}

      {/* Burned-in captions on top of everything, full duration. */}
      <Sequence from={0} durationInFrames={TOTAL_FRAMES} name="Captions">
        <Captions />
      </Sequence>

      {/* Voiceover: drop public/voiceover.mp3 and set HAS_VOICEOVER=true in
          timing.ts. See VoiceoverNote.md for the sync workflow. */}
      {HAS_VOICEOVER ? <Audio src={staticFile(VOICEOVER_FILE)} /> : null}
    </AbsoluteFill>
  );
};
