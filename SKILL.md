---
name: codebase-video-explainer
description: Create evidence-backed developer explainer videos from local projects, Git repositories, or GitHub repositories. Use when the user asks to understand, onboard to, explain, visualize, or produce a video walkthrough of a codebase, architecture, request flow, module relationship, or execution path. Analyze verified source relationships first, then create architecture visuals, a storyboard, natural Chinese narration with exact TTS-derived subtitle timing, a Remotion project, and a final MP4. Prefer local Remotion, use GitHub Actions Remotion when local npm or browser access is blocked, and use FFmpeg only as the final fallback.
---

# Codebase Video Explainer

Treat this as an Agent Skill, not a standalone application. `SKILL.md` is the control plane; `scripts/`, `references/`, and `assets/` are supporting resources.

## Core principles

- Analyze before animating. Verify architecture and execution paths from source whenever possible.
- Prefer execution paths over file-by-file tours.
- Keep verified facts separate from inference and label unknowns.
- Write narration for speech. Generate one continuous TTS request per scene whenever practical.
- Treat measured narration audio as the master timeline. Final subtitles must use real TTS boundaries when available.
- Call an output a Remotion render only when the Remotion CLI actually rendered it.
- Keep generated artifacts under `.codebase-video/` unless the user requests another location.
- Do not modify production application code unless the user explicitly asks.

## Use bundled scripts efficiently

Treat bundled scripts as black boxes first. Run `python <script> --help` before reading script source. Read or patch a script only when the documented interface is insufficient, the environment requires adaptation, or debugging is necessary.

## Workflow

1. **Resolve the repository.**
   - Use the current project when appropriate.
   - For a GitHub URL, use an available GitHub connector, Git client, or checkout mechanism.
   - Ask for a path or URL only when no repository is available.

2. **Inventory and analyze.**
   - Run `scripts/scan_codebase.py` and `scripts/build_project_manifest.py`.
   - Read `references/analysis-workflow.md` and build an evidence-backed mental model.
   - Trace 1–3 representative end-to-end execution paths through real files and symbols.
   - Produce `project-analysis.json` and `architecture.mmd`; render SVG when practical.

3. **Design the explanation.**
   - Read `references/storyboard-format.md` before writing `storyboard.json`.
   - Read `references/video-style.md` before implementing scenes.
   - Default audience: a developer new to the repository.
   - Default language: Simplified Chinese.
   - Prefer: purpose → architecture → module map → execution path → key code → modification guide → recap.

4. **Generate narration and exact timing.**
   - Read `references/production-pipeline.md` before audio/video production.
   - Prefer `zh-CN-YunyangNeural` unless the user chooses another voice.
   - Use scene-level TTS and Edge TTS `SentenceBoundary` metadata for final SRT timing.
   - Use `storyboard.timed.json` for final rendering when TTS timing exists.
   - Never distribute final subtitle timing by character count after real TTS audio exists.
   - Do not silently fall back to `espeak`, `pyttsx3`, or similarly robotic voices for a deliverable.

5. **Implement visuals.**
   - Capture screenshots only when they materially improve understanding and the app can be run safely.
   - Prefer a dedicated Remotion Skill if one is installed; otherwise initialize the bundled template with `scripts/init_remotion_project.py`.
   - Tailor the generic template to the real architecture, code excerpts, screenshots, and execution paths.

6. **Render using the best available path.**
   - Prefer a real local Remotion render.
   - If local npm, DNS, Chromium, or runtime limits block Remotion and the user permits GitHub Actions, prepare a portable render job with `scripts/prepare_remotion_job.py` and use `assets/github-actions/remotion-render.yml`.
   - Use FFmpeg only when both local and permitted GitHub Actions Remotion are unavailable, disallowed, or unsuitable.

7. **Verify the result.**
   - Read `references/quality-gates.md` and run its checks before declaring completion.
   - Sample-check subtitle sync near the beginning, middle, and end.
   - Preserve render provenance, including a GitHub Actions run URL or run ID when used.

## Render decision tree

```text
Need final MP4
├─ Local Remotion works
│  └─ typecheck → preview still → remotion render → ffprobe
├─ Local Remotion blocked, GitHub Actions permitted
│  └─ prepare render job → Actions Remotion → ffprobe → artifact
└─ Remotion unavailable or disallowed
   └─ FFmpeg fallback using the same timed storyboard, narration, and exact SRT
```

## Output contract

Create these artifacts when the corresponding phase runs:

- `scan.json`, `project-manifest.json`
- `project-analysis.json`
- `architecture.mmd` and optional `architecture.svg`
- `storyboard.json`, `narration.zh-CN.md`
- `narration.mp3`, `timings.json`, `storyboard.timed.json`, `subtitles.srt`
- optional `screenshots/`
- `remotion/`
- `output.mp4`

## Guardrails

- Never expose `.env` values, API tokens, passwords, cookies, private keys, certificates, or secret-manager output.
- Skip dependency/build trees such as `node_modules`, `.git`, `.next`, `dist`, `build`, `target`, `vendor`, caches, virtualenvs, and generated bundles during analysis.
- Do not present README claims as proof when implementation disagrees.
- Do not reuse an MP4 with obsolete burned-in subtitles; re-render from clean visuals when subtitle timing changes.
- Do not silently commit temporary workflows or render jobs into a user's repository without permission.

## References

- Read `references/analysis-workflow.md` during repository analysis and evidence collection.
- Read `references/storyboard-format.md` before creating or changing the storyboard interchange format.
- Read `references/video-style.md` before implementing scene visuals and transitions.
- Read `references/production-pipeline.md` for Mermaid, screenshots, TTS, exact subtitles, Remotion, GitHub Actions, and FFmpeg fallback details.
- Read `references/quality-gates.md` before final delivery and QA.
