# Production pipeline

## Table of contents

- [1. Render the architecture diagram](#1-render-the-architecture-diagram)
- [2. Plan and capture UI screenshots](#2-plan-and-capture-ui-screenshots)
- [3. Treat estimated subtitles as draft-only](#3-treat-estimated-subtitles-as-draft-only)
- [4. Preferred natural Chinese TTS with exact timing](#4-preferred-natural-chinese-tts-with-exact-timing)
- [5. Free GitHub Actions TTS fallback](#5-free-github-actions-tts-fallback)
- [6. Initialize the Remotion project](#6-initialize-the-remotion-project)
- [7. Prefer local Remotion rendering](#7-prefer-local-remotion-rendering)
- [8. GitHub Actions Remotion fallback](#8-github-actions-remotion-fallback)
- [9. FFmpeg fallback when Remotion is unavailable](#9-ffmpeg-fallback-when-remotion-is-unavailable)
- [10. Final synchronization verification](#10-final-synchronization-verification)

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

## 7. Prefer local Remotion rendering

When npm registry access and the browser runtime work locally, render in the generated project:

```bash
cd <repo>/.codebase-video/remotion
npm install
npx tsc --noEmit
npm run render:still
npm run render
```

Render a preview still before the full MP4. Inspect text fit, Chinese fonts, subtitle safe area, and scene composition. Verify the final MP4 with ffprobe.

## 8. GitHub Actions Remotion fallback

Use this before FFmpeg when the Remotion project is valid but the current environment cannot reach npm, cannot download or launch Chromium, or has a strict local execution limit. This path performs a real Remotion render on a GitHub-hosted runner.

Prepare a portable render job in a repository the user permits using:

```bash
python <skill-dir>/scripts/prepare_remotion_job.py \
  --project <repo>/.codebase-video/remotion \
  --job-dir <runner-repo>/render-jobs/current \
  --composition CodebaseExplainer \
  --audio-run-id <optional-tts-workflow-run-id> \
  --audio-artifact-name codebase-video-natural-tts \
  --force
```

The helper copies the Remotion project while excluding `node_modules`, prior `out/` files, caches, and Git metadata. It writes `render-job.json` with the composition, entrypoint, preview frame, concurrency, output name, and optional prior TTS artifact metadata.

If `--audio-run-id` is provided, the helper removes the copied `public/narration.mp3`; GitHub Actions will download that file from the previous workflow artifact instead of committing the narration binary. If the narration already belongs in the render repository, omit the artifact options.

Copy the bundled workflow:

```text
<skill-dir>/assets/github-actions/remotion-render.yml
    -> <runner-repo>/.github/workflows/codebase-video-remotion-render.yml
```

The workflow then:

1. checks out the render job;
2. installs Node 22, Noto CJK fonts, and ffmpeg;
3. optionally downloads narration from a prior Actions artifact;
4. runs `npm ci` when a lockfile exists, otherwise `npm install`;
5. runs `npx tsc --noEmit` when `tsconfig.json` exists;
6. renders `out/preview.png` with `remotion still`;
7. renders the full H.264/yuv420p MP4 with the real `remotion render` command;
8. writes `out/ffprobe.json`; and
9. uploads the MP4, preview image, and ffprobe report as the `codebase-video-remotion-render` artifact by default.

For a roughly 8-minute 1080p/30fps technical explainer, one successful GitHub-hosted run took about 8–10 minutes end to end. Treat this only as an observed reference, not a guarantee.

Keep the workflow run URL or run ID as provenance. This is a genuine Remotion render: ffmpeg is used only for media support and verification, while Remotion renders the video frames. Do not silently commit the workflow or render job into the user's repository without permission.

## 9. FFmpeg fallback when Remotion is unavailable

Use FFmpeg only when both local Remotion and GitHub Actions Remotion are unavailable, disallowed, or unsuitable:

1. Render or prepare one static/animated visual for each timed scene.
2. Use `timings.json` / `storyboard.timed.json` for scene lengths.
3. Use `narration.mp3` as the master audio track.
4. Burn or mux `subtitles.srt` generated from real speech boundaries.
5. Use a lower frame rate for mostly static technical cards if render time is constrained; preserve 1920x1080 readability.
6. State clearly that FFmpeg fallback, not Remotion, produced the final MP4.

Do not reuse an MP4 that already has obsolete subtitles burned in. Re-render from clean scene visuals when subtitle timing changes.

## 10. Final synchronization verification

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
