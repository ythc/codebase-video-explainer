---
name: codebase-video-explainer
description: Analyze an unfamiliar software repository and turn it into an evidence-backed developer explainer video. Use when the user asks to understand, onboard to, explain, visualize, or create a video walkthrough of a local project, Git repository, GitHub repository, application architecture, request flow, module relationships, or codebase. Build a verified project mental model first, then produce architecture visuals, storyboard, natural Chinese narration with exact TTS-derived subtitle timing by default, a Remotion project, and an MP4; prefer local Remotion, use GitHub Actions Remotion when local npm/browser access is blocked, and use FFmpeg only as the final fallback.
---

# Codebase Video Explainer

Treat this repository as an Agent Skill first. The scripts, references, Remotion template, and GitHub Actions workflows are supporting resources that this Skill coordinates; they are not a standalone end-user application.

Turn a real codebase into a concise developer walkthrough. Analyze first; animate second. Never infer architecture merely from filenames when the implementation can be verified from source.

## Output contract

Create work products under `.codebase-video/` in the target project unless the user specifies another directory:

- `scan.json` — deterministic repository inventory.
- `project-manifest.json` — technology, package, script, entrypoint, and dependency summary.
- `project-analysis.json` — evidence-backed mental model, modules, external systems, important files, execution paths, risks, and unknowns.
- `architecture.mmd` — Mermaid architecture source.
- `architecture.svg` — rendered architecture when available.
- `screenshots/` — optional UI screenshots.
- `storyboard.json` — initial scene plan.
- `narration.zh-CN.md` — natural Chinese narration copy by default.
- `narration.mp3` — final narration audio when TTS succeeds.
- `timings.json` — measured per-scene audio timing.
- `storyboard.timed.json` — storyboard with scene durations replaced by measured TTS durations.
- `subtitles.srt` — final subtitles derived from real TTS speech boundaries when TTS is used.
- `remotion/` — generated Remotion project.
- `output.mp4` — final video.

Do not modify production application code unless the user explicitly asks. Keep generated artifacts isolated under `.codebase-video/` whenever possible.

## Core workflow

1. Resolve the repository.
   - Prefer the current working directory when it is the user's project.
   - For a GitHub URL, use an available GitHub connector, Git client, or checkout mechanism.
   - If no repository is available, request the repository path or URL.

2. Inventory the project.
   - Run `scripts/scan_codebase.py`.
   - Run `scripts/build_project_manifest.py`.
   - Skip dependency/build trees such as `node_modules`, `.git`, `.next`, `dist`, `build`, `target`, `vendor`, caches, virtualenvs, and generated bundles.

3. Build an evidence-backed mental model.
   - Follow `references/analysis-workflow.md`.
   - Read README/package/build manifests, then entrypoints, routes/bootstrap code, core modules, storage, auth, external clients, and representative tests.
   - Trace 1–3 representative execution paths through real files and symbols.
   - Record supporting paths/symbols for important architectural claims.
   - Label uncertainty explicitly.

4. Produce `project-analysis.json` and `architecture.mmd`.
   - Keep the architecture diagram compact and module-oriented rather than one node per file.
   - Render to SVG with `scripts/render_mermaid.py` when possible.

5. Design the video before implementing it.
   - Follow `references/storyboard-format.md` and `references/video-style.md`.
   - Default audience: developer new to the repository.
   - Default language: Simplified Chinese.
   - Default duration: roughly 5–15 minutes, adapted to complexity.
   - Prefer: purpose → architecture → module map → representative execution flow → key code → modification guide → recap.

6. Write `storyboard.json` and `narration.zh-CN.md`.
   - Write narration for speech, not for reading a document aloud.
   - Rewrite awkward file paths, symbols, acronyms, and URLs into natural spoken Chinese when meaning is preserved.
   - Prefer one continuous narration block per scene instead of many tiny TTS clips.
   - Keep on-screen text short and evidence-backed.

7. Generate narration and final timing.
   - Read `references/production-pipeline.md` before audio/video production.
   - Prefer `zh-CN-YunyangNeural` for Chinese developer narration unless the user chooses another voice.
   - Preferred local command:
     `python <skill-dir>/scripts/synthesize_edge_tts.py --storyboard <repo>/.codebase-video/storyboard.json --output-dir <repo>/.codebase-video`
   - This must synthesize each scene continuously and use Edge TTS `SentenceBoundary` metadata for final subtitle timing.
   - Treat audio timing as the master timeline. Use `storyboard.timed.json`, not the original estimated durations, for final rendering.
   - Never derive final subtitles by distributing time according to character count when TTS audio exists.
   - Never default to `espeak`, `pyttsx3`, or similar robotic offline voices for a deliverable unless the user explicitly accepts that fallback.

8. If local Edge TTS networking is unavailable, use the free GitHub Actions fallback when the user has an Actions-capable repository they permit using.
   - Generate `tts-jobs/current/scenes.json` with `scripts/build_tts_job.py`.
   - Copy `assets/github-actions/natural-tts.yml` to `.github/workflows/codebase-video-natural-tts.yml` in the permitted runner repository.
   - Let the workflow generate `narration.mp3`, `subtitles.srt`, `timings.json`, and boundary metadata.
   - Download the artifact and place the final files under `.codebase-video/`.
   - Do not silently commit workflow files to a user's repository without permission.

9. Collect optional visual assets.
   - Capture screenshots only when they materially improve understanding and the target app can be run safely.
   - Use `scripts/capture_screenshots.py` with a reviewed screenshot plan.
   - Do not install browser dependencies into the target application unless the user asks.

10. Generate the Remotion implementation.
    - Prefer a Remotion-focused Skill if one is installed.
    - Otherwise use `scripts/init_remotion_project.py --root <repo> --force`.
    - The initializer prefers `storyboard.timed.json` when present and copies narration, subtitles, and timing metadata into the project.
    - Tailor the generic template to the real architecture, code excerpts, screenshots, and execution paths before final delivery.

11. Prefer a real local Remotion render when npm and the browser runtime are available.
    - Run TypeScript checking when configured.
    - Render a preview still before the full MP4.
    - Run the actual Remotion CLI render command, then verify the result with ffprobe.

12. If local Remotion is blocked by npm registry, DNS, Chromium/browser download, or container limits, use GitHub Actions Remotion before FFmpeg when the user permits an Actions-capable repository.
    - Prepare `render-jobs/current/` with `scripts/prepare_remotion_job.py --project <repo>/.codebase-video/remotion --job-dir <runner-repo>/render-jobs/current --composition <composition-id> --force`.
    - Copy `assets/github-actions/remotion-render.yml` to `<runner-repo>/.github/workflows/codebase-video-remotion-render.yml`.
    - When a prior TTS workflow artifact exists, pass its run ID to `prepare_remotion_job.py` so narration can be downloaded by Actions instead of committed as a binary.
    - Let the workflow install Node, Chinese fonts, ffmpeg, and project dependencies; run TypeScript checking; render a preview still; execute the real `remotion render`; verify with ffprobe; and upload the MP4 artifact.
    - Download the `codebase-video-remotion-render` artifact and place the MP4 under `.codebase-video/output.mp4`.
    - Do not silently commit render jobs or workflow files into a user's repository without permission.
    - Preserve the workflow run URL or run ID as render provenance.

13. Fall back to FFmpeg only when both local Remotion and GitHub Actions Remotion are unavailable, disallowed, or unsuitable.
    - Reuse the same timed storyboard, scene visuals, narration audio, and exact SRT.
    - For static explainer cards, a low frame rate is acceptable if it materially reduces render time; preserve resolution and legibility.
    - Keep narration and subtitles on the same measured timeline.
    - Never claim a Remotion render occurred when the final MP4 was produced with FFmpeg.

14. Verify synchronization and render quality.
    - Run `scripts/check_av_sync.py --audio <repo>/.codebase-video/narration.mp3 --subtitles <repo>/.codebase-video/subtitles.srt --video <repo>/.codebase-video/output.mp4` after final render when ffprobe is available.
    - Ensure video/audio duration mismatch stays within the check tolerance.
    - Ensure the last subtitle cue ends close to the narration end.
    - Sample-check beginning, middle, and ending subtitle sync visually/audibly.

## TTS and subtitle rules

- Use one continuous TTS request per scene whenever practical.
- Use Edge TTS `SentenceBoundary` offsets/durations for final SRT cues.
- Keep a short natural gap between scenes; default around 0.7 seconds.
- Normalize narration to a consistent perceived loudness before final delivery.
- If TTS is unavailable, `scripts/build_subtitles.py` may create draft subtitles from estimated scene timing, but label them as estimated and do not present them as synchronized final subtitles.
- If exact TTS metadata is available, it always overrides estimated storyboard timing.
- Do not time-stretch speech merely to fit an estimated storyboard duration; update the scene duration to match the speech instead.

## Analysis rules

- Do not explain every file; explain the smallest set that yields an accurate mental model.
- Prefer execution paths over directory tours.
- Separate verified facts from inference.
- Treat README claims as orientation, not proof, when implementation disagrees.
- Use tests to validate expected behavior when practical.
- For monorepos, identify apps/packages first and scope the video to the requested or primary runnable application.
- Never expose `.env` values, tokens, passwords, private keys, certificates, cookies, or secret-manager output.
- Avoid large generated files and third-party source in analysis.

## Quality gates

Before calling the task complete, verify:

1. The project purpose is understandable in under 60 seconds.
2. The architecture diagram matches verified source relationships.
3. At least one representative end-to-end execution path is shown.
4. Every key code excerpt exists in the repository at generation time.
5. No scene exists only to display a paragraph.
6. The viewer learns where to make at least one common change safely.
7. Unknown relationships are labeled.
8. Narration sounds continuous at scene level rather than sentence-by-sentence spliced.
9. Final subtitles use real TTS boundaries when narration audio exists.
10. Beginning, middle, and end subtitle sync have been checked.
11. Local Remotion renders successfully, or GitHub Actions Remotion is attempted before FFmpeg when the blocker is only npm/browser/runtime access.
12. GitHub Actions Remotion, when used, passes typecheck, preview-still rendering, the full `remotion render`, and ffprobe verification.
13. Final A/V durations pass `scripts/check_av_sync.py` when ffprobe is available.
14. Render provenance is stated accurately: call an output a Remotion render only when the Remotion CLI render step succeeded; label FFmpeg fallback explicitly.

## References

- Read `references/analysis-workflow.md` for repository analysis and evidence requirements.
- Read `references/storyboard-format.md` before creating `storyboard.json`.
- Read `references/video-style.md` before implementing scenes.
- Read `references/production-pipeline.md` for Mermaid, screenshots, natural TTS, exact subtitles, GitHub Actions TTS and Remotion fallbacks, FFmpeg fallback, and final QA.
