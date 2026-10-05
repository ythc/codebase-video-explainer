# Production pipeline

Use this reference after analysis and storyboard creation.

## 1. Render the architecture diagram

Prefer SVG because it stays sharp during zooms and pans.

```bash
python <skill-dir>/scripts/render_mermaid.py \
  --input <repo>/.codebase-video/architecture.mmd \
  --output <repo>/.codebase-video/architecture.svg
```

The helper uses a local `mmdc` first and falls back to `npx @mermaid-js/mermaid-cli`.

## 2. Plan and capture UI screenshots

Create `.codebase-video/screenshot-plan.json` only when screenshots materially help explain the application.

Example:

```json
{
  "base_url": "http://127.0.0.1:3000",
  "shots": [
    {
      "name": "home",
      "path": "/",
      "full_page": true,
      "wait_until": "networkidle",
      "wait_for_ms": 500
    }
  ]
}
```

Validate without launching a browser:

```bash
python <skill-dir>/scripts/capture_screenshots.py \
  --plan <repo>/.codebase-video/screenshot-plan.json \
  --output-dir <repo>/.codebase-video/screenshots \
  --validate-plan
```

Capture when the target app is already running:

```bash
python <skill-dir>/scripts/capture_screenshots.py \
  --plan <repo>/.codebase-video/screenshot-plan.json \
  --output-dir <repo>/.codebase-video/screenshots
```

Do not change the target application's dependency files merely to capture screenshots unless the user asks.

## 3. Treat estimated subtitles as draft-only

Before TTS exists, this helper can create a rough SRT from storyboard estimates:

```bash
python <skill-dir>/scripts/build_subtitles.py \
  --storyboard <repo>/.codebase-video/storyboard.json \
  --output <repo>/.codebase-video/subtitles.draft.srt
```

Do not use character-count or estimated-duration subtitles as the final subtitle track once real narration audio exists.

## 4. Preferred natural Chinese TTS with exact timing

Default voice:

```text
zh-CN-YunyangNeural
```

Recommended defaults:

```text
rate: -5%
pitch: -2Hz
scene gap: 0.7 s
```

Generate one continuous TTS utterance per storyboard scene and capture Edge TTS `SentenceBoundary` events:

```bash
python <skill-dir>/scripts/synthesize_edge_tts.py \
  --storyboard <repo>/.codebase-video/storyboard.json \
  --output-dir <repo>/.codebase-video
```

This emits:

- `narration.mp3`
- `narration.wav`
- `subtitles.srt` from real speech boundaries
- `timings.json`
- `storyboard.timed.json`
- `tts-metadata/*.jsonl`
- normalized per-scene WAV files

Use `storyboard.timed.json` as the final scene-duration source. Do not time-stretch speech to fit the original estimated scene durations.

Avoid `espeak`, `pyttsx3`, or similarly robotic voices for the final deliverable unless the user explicitly accepts them.

## 5. Free GitHub Actions TTS fallback

Use this when direct Edge TTS networking is blocked locally and the user has an Actions-capable repository they permit using.

Build a portable job file:

```bash
python <skill-dir>/scripts/build_tts_job.py \
  --storyboard <repo>/.codebase-video/storyboard.json \
  --output <runner-repo>/tts-jobs/current/scenes.json
```

Copy the bundled workflow:

```text
<skill-dir>/assets/github-actions/natural-tts.yml
    -> <runner-repo>/.github/workflows/codebase-video-natural-tts.yml
```

The workflow installs `edge-tts==7.2.8` and ffmpeg, synthesizes each scene continuously, records `SentenceBoundary` metadata, normalizes audio, and uploads an artifact named `codebase-video-natural-tts` containing:

- `narration.mp3`
- `subtitles.srt`
- `timings.json`
- raw boundary metadata

Download the artifact and place the final files under the target project's `.codebase-video/` directory. Do not silently commit workflow files into a user's repository without permission.

## 6. Initialize the Remotion project

Use the bundled fallback template only when a dedicated Remotion Skill or project-specific Remotion setup is unavailable.

```bash
python <skill-dir>/scripts/init_remotion_project.py \
  --root <repo> \
  --force
```

The initializer prefers `.codebase-video/storyboard.timed.json` when present, then copies available architecture source, screenshots, narration audio, subtitles, and timing metadata.

Then:

```bash
cd <repo>/.codebase-video/remotion
npm install
npm run studio
npm run render
```

Tailor the fallback template to the actual architecture, code excerpts, screenshots, and execution paths before final delivery.

## 7. FFmpeg fallback when Remotion is unavailable

If npm/Remotion cannot be installed or launched, still produce a usable MP4 when practical:

1. Render or prepare one static/animated visual for each timed scene.
2. Use `timings.json` / `storyboard.timed.json` for scene lengths.
3. Use `narration.mp3` as the master audio track.
4. Burn or mux `subtitles.srt` generated from real speech boundaries.
5. Use a lower frame rate for mostly static technical cards if render time is constrained; preserve 1920x1080 readability.
6. State clearly that FFmpeg fallback, not Remotion, produced the final MP4.

Do not reuse an MP4 that already has obsolete subtitles burned in. Re-render from clean scene visuals when subtitle timing changes.

## 8. Final synchronization verification

Run:

```bash
python <skill-dir>/scripts/check_av_sync.py \
  --audio <repo>/.codebase-video/narration.mp3 \
  --subtitles <repo>/.codebase-video/subtitles.srt \
  --video <repo>/.codebase-video/output.mp4
```

Then manually sample-check at least:

- the opening 30–60 seconds,
- the middle of the video,
- the final minute.

Confirm:

- subtitle content matches the spoken sentence,
- there is no cumulative drift,
- the last subtitle ends close to the narration end,
- video and audio durations are nearly identical,
- code and architecture labels remain legible,
- narration does not present inference as verified fact.
