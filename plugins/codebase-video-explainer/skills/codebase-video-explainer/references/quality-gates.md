# Quality gates

Use this checklist before declaring a codebase explainer video complete.

## Content accuracy

- The project purpose is understandable in under 60 seconds.
- The architecture diagram matches verified source relationships.
- At least one representative end-to-end execution path is shown.
- Every key code excerpt existed in the repository at generation time.
- Unknown or inferred relationships are labeled.
- The viewer learns where to make at least one common change safely.

## Narrative and visual quality

- No scene exists only to display a paragraph.
- Narration sounds continuous at scene level rather than sentence-by-sentence spliced.
- On-screen text remains readable at 1080p.
- Visual emphasis follows the explanation instead of competing with it.

## Timing and subtitle quality

- Final subtitles use real TTS boundaries when narration audio exists.
- The last subtitle cue ends close to the narration end.
- Beginning, middle, and ending subtitle sync have been checked manually.
- Video and audio durations are nearly identical.

When ffprobe is available, run:

```bash
python <skill-dir>/scripts/check_av_sync.py \
  --audio <repo>/.codebase-video/narration.mp3 \
  --subtitles <repo>/.codebase-video/subtitles.srt \
  --video <repo>/.codebase-video/output.mp4
```

## Render provenance

- A local Remotion render must pass TypeScript checking when configured, a preview still, the full `remotion render`, and ffprobe verification.
- A GitHub Actions Remotion render must pass the same stages and preserve the run URL or run ID.
- A video produced by FFmpeg fallback must be labeled as FFmpeg output, not Remotion output.

## Security and repository hygiene

- No secret values appear in narration, screenshots, logs, generated assets, or committed render jobs.
- Temporary TTS/render jobs and one-off workflows are removed after publishing unless they are intentionally reusable project infrastructure.
