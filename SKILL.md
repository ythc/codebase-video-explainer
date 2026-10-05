---
name: codebase-video-explainer
description: Analyze an unfamiliar software repository and turn it into a developer-oriented visual explainer video. Use when the user asks to understand, onboard to, explain, visualize, or create a video walkthrough of a local project, Git repository, GitHub repository, application architecture, request flow, module relationships, or codebase. Build an evidence-backed project mental model first, then produce architecture diagrams, a structured storyboard, Chinese narration/subtitles by default, a Remotion video project, and an MP4 when rendering is available.
---

# Codebase Video Explainer

Turn a real codebase into a concise visual developer walkthrough. Analyze first; animate second. Never infer architecture merely from filenames when the implementation can be verified from source.

## Output contract

Create work products under `.codebase-video/` in the target project unless the user specifies another output directory:

- `scan.json` — deterministic repository inventory from `scripts/scan_codebase.py`.
- `project-manifest.json` — technology, package, script, entrypoint, and dependency summary from `scripts/build_project_manifest.py`.
- `project-analysis.json` — evidence-backed mental model, modules, important files, external systems, and execution paths.
- `architecture.mmd` — Mermaid architecture diagram.
- `storyboard.json` — scene-by-scene video specification following `references/storyboard-format.md`.
- `narration.zh-CN.md` — Chinese narration and subtitle copy by default.
- `remotion/` — generated Remotion project.
- `output.mp4` — final video when rendering succeeds.

Do not modify production application code unless the user explicitly asks. Keep generated video artifacts isolated under `.codebase-video/`.

## Workflow

1. Resolve the repository.
   - Prefer the current working directory when it is the user's project.
   - If the user provides a GitHub repository or URL, use an available GitHub connector, Git client, or repository checkout mechanism to access the source.
   - If no repository is available, request the repository path or URL.

2. Create `.codebase-video/` and inventory the project.
   - Run:
     `python <skill-dir>/scripts/scan_codebase.py --root <repo> --output <repo>/.codebase-video/scan.json`
   - Then run:
     `python <skill-dir>/scripts/build_project_manifest.py --root <repo> --scan <repo>/.codebase-video/scan.json --output <repo>/.codebase-video/project-manifest.json`
   - Do not recursively inspect dependency/build directories such as `node_modules`, `.git`, `.next`, `dist`, `build`, `target`, `vendor`, coverage output, caches, virtualenvs, or generated bundles.

3. Build a mental model from evidence.
   - Follow `references/analysis-workflow.md`.
   - Read README and package/build manifests first, then entrypoints, routing/bootstrap code, major module boundaries, data/storage code, external service clients, and representative tests.
   - Identify the project's purpose, tech stack, startup path, important modules, boundaries, APIs, storage, auth, jobs/events, external services, and risky/complex areas.
   - Trace 1–3 representative execution paths through real files and symbols.
   - Record supporting file paths and symbol names for every important architectural claim.
   - Explicitly label uncertainty when a relationship cannot be verified.

4. Produce `project-analysis.json`.
   Include at least:
   - `summary`
   - `tech_stack`
   - `entrypoints`
   - `modules`
   - `external_systems`
   - `important_files`
   - `execution_paths`
   - `developer_mental_model`
   - `risks_and_unknowns`
   - `evidence`

5. Produce `architecture.mmd`.
   - Prefer a compact Mermaid flowchart or sequence diagram.
   - Show system boundaries and actual verified relationships.
   - Avoid one node per file. Group files into meaningful modules or services.

6. Design the video before implementing it.
   - Follow `references/storyboard-format.md` and `references/video-style.md`.
   - Default target duration: 5–15 minutes, adapted to project complexity.
   - Default language: Simplified Chinese.
   - Default audience: developer who has never seen the project.
   - Prefer the progression: project purpose → architecture → module map → representative flow → key code → modification guide → recap.
   - Prefer visuals over paragraphs: animated architecture, file tree zooms, arrows, request/data flow, sequence diagrams, code highlights, and UI screenshots when they clarify behavior.

7. Create `storyboard.json` and `narration.zh-CN.md`.
   - Every scene must state its teaching purpose, evidence source, narration, visuals, animation, and approximate duration.
   - Keep on-screen text short.
   - Never present an unverified inference as fact in narration.

8. Generate the Remotion implementation.
   - If a Remotion-focused Skill is available in the environment, use it for current Remotion conventions, animation patterns, media handling, preview, and rendering.
   - Otherwise create a standard Remotion project under `.codebase-video/remotion/` using the currently supported Remotion setup for the environment.
   - Keep architecture/module visuals as reusable components rather than a single giant scene.
   - Use syntax-highlighted code excerpts copied from the repository; do not retype code from memory.
   - Keep long code blocks out of the video. Highlight only the lines needed to explain the current concept.

9. Narration and subtitles.
   - Generate Chinese narration by default.
   - Generate timed subtitles from the same narration text.
   - If a TTS capability is available, synthesize narration audio and align scenes/subtitles to the audio duration.
   - If no TTS capability is available, still complete the narration, subtitles, and renderable visual project; state the missing audio dependency instead of fabricating an audio file.

10. Preview and verify.
    - Open or run Remotion Studio when available.
    - Verify that all compositions load, text fits, code is legible, animations do not overlap, assets resolve, and the full timeline renders without errors.
    - Fix render/runtime errors before final export.

11. Render.
    - Default: 1920×1080, 30 FPS, H.264 MP4 unless the user requests otherwise.
    - Render to `.codebase-video/output.mp4`.
    - If final rendering is impossible in the current environment, deliver the complete Remotion project plus the exact render command and explain the missing prerequisite.

## Analysis rules

- Do not explain every file. Explain the smallest set of files that gives the viewer an accurate mental model.
- Prefer execution paths over directory tours.
- Separate verified facts from inference.
- Treat README claims as orientation, not proof, when implementation disagrees.
- Use tests to validate expected behavior when practical.
- For large monorepos, first identify apps/packages and scope the video to the user's requested product or the primary runnable application.
- Avoid exposing secrets from `.env`, credentials, tokens, keys, private certificates, or secret-manager output. Show configuration names, never secret values.
- Avoid including large generated files or third-party source in the analysis.

## Quality gates

Before calling the task complete, verify all of the following:

1. The project purpose is understandable in under 60 seconds of video.
2. The architecture diagram matches verified source relationships.
3. At least one representative end-to-end execution path is shown.
4. Every key code excerpt exists in the repository at generation time.
5. The storyboard has no scene whose only purpose is to display a paragraph.
6. The viewer learns where to make a common change and what downstream modules it affects.
7. Unknown or ambiguous relationships are labeled as such.
8. The Remotion project loads successfully, or the exact blocking dependency is documented.
9. The final MP4 renders successfully when the environment supports rendering.

## References

- Read `references/analysis-workflow.md` for repository analysis and evidence requirements.
- Read `references/storyboard-format.md` before creating `storyboard.json`.
- Read `references/video-style.md` before implementing Remotion scenes.
