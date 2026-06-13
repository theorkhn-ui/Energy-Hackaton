# Voiceover, where it goes and how it syncs

## Drop the file here

```
video/public/voiceover.mp3
```

(`.wav` also works, then change `VOICEOVER_FILE` in `src/timing.ts`.)

Then open `src/timing.ts` and flip:

```ts
export const HAS_VOICEOVER = true;
```

That's it, `src/MainVideo.tsx` already contains the `<Audio>` tag, gated by
that flag, so the project compiles and previews fine with no audio file
present.

## Recording checklist (from the storyboard)

- ~540 words total, ~140 wpm. Record **scene by scene**, one take per scene
  is fine. Quiet room; phone mic in a closet beats laptop mic in a hall.
- Speak the numbers as written in the narration column ("fifty-one and a half
  days"), don't read digits.
- Scene 8 (limitation): slow down, drop the energy. Sincerity beat.
- Normalize to −16 LUFS (e.g. `ffmpeg -i raw.wav -af loudnorm=I=-16 voiceover.mp3`).

## How sync works

The composition is built scene-first: every scene starts at a fixed frame
(`SCENE_STARTS` in `src/timing.ts`, 10/25/35/35/30/35/20/10/30 seconds).
The voiceover must hit those same boundaries:

1. Record each scene's narration separately.
2. Concatenate with padding so each scene's audio starts exactly at its
   scene start time (0:00, 0:10, 0:35, 1:10, 1:45, 2:15, 2:50, 3:10, 3:20).
   Example with ffmpeg: pad each clip to its scene duration
   (`-af apad=whole_dur=25` for Scene 2), then concat.
3. If a take runs long for its slot, either re-record tighter or adjust that
   scene's `durationSec` in `src/timing.ts`, scenes AND captions retime
   automatically. Keep the total at ≤ 230s (4:00 hard cap minus buffer).

## Caption fine-tuning

Captions currently auto-distribute each scene's narration proportionally to
word count (`buildCaptions()` in `src/Captions.tsx`). After recording, if a
specific line drifts from the voice, replace the auto timing with hand-timed
values: export the `captions` array as literal `Caption[]` objects with
`startMs`/`endMs` measured from the audio (Audacity label track or
`whisper --output_format srt` both work).
