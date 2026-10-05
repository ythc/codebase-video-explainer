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
    },
    {
      "name": "chat",
      "path": "/chat",
      "wait_for_selector": "main",
      "full_page": false,
      "viewport": {"width": 1440, "height": 900}
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

If Playwright is missing, install it in the execution environment and install Chromium. Do not change the target application's dependency files just to capture screenshots unless the user explicitly asks.

## 3. Build subtitles

Generate deterministic SRT cues from storyboard scene durations and narration:

```bash
python <skill-dir>/scripts/build_subtitles.py \
  --storyboard <repo>/.codebase-video/storyboard.json \
  --output <repo>/.codebase-video/subtitles.srt
```

If real TTS timing is available, prefer real speech timing over estimated scene timing.

## 4. Optional Chinese TTS

The bundled helper supports `edge-tts` when the package is available:

```bash
python <skill-dir>/scripts/synthesize_edge_tts.py \
  --input <repo>/.codebase-video/narration.zh-CN.md \
  --output <repo>/.codebase-video/narration.mp3
```

The default voice is `zh-CN-XiaoxiaoNeural`. Respect a user-selected voice when provided. TTS is optional; never block a complete visual project on audio generation.

## 5. Initialize the Remotion project

Use the bundled fallback template only when a dedicated Remotion Skill or an existing project-specific Remotion setup is unavailable.

```bash
python <skill-dir>/scripts/init_remotion_project.py \
  --root <repo> \
  --force
```

This copies the fallback project to `.codebase-video/remotion/`, injects `storyboard.json`, and copies available screenshots, architecture source, narration audio, and subtitles into the project.

Then:

```bash
cd <repo>/.codebase-video/remotion
npm install
npm run studio
npm run render
```

The fallback template is intentionally generic. After it renders, tailor scenes to the actual architecture and code excerpts. Do not ship the generic fallback as the final video unless the user explicitly requests a rough prototype.

## 6. Final verification

Before rendering the final video:

- Confirm all screenshot paths resolve.
- Confirm architecture labels match verified analysis.
- Confirm every code excerpt still matches the repository.
- Confirm subtitles are readable and do not overlap code.
- Confirm narration does not claim inferred relationships as verified facts.
- Confirm the full composition renders end to end.
