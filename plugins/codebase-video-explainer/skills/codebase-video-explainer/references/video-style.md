# Video style guide

## Teaching style

Teach a mental model, not a directory listing. Start broad and progressively zoom in:

`system → module → execution path → file → relevant lines of code`.

Return to the architecture diagram after code close-ups so the viewer retains context.

## Visual language

Prefer:

- architecture cards with clear boundaries
- animated arrows for control/data flow
- progressive disclosure rather than showing the full graph immediately
- file-tree zooms with only relevant branches expanded
- sequence diagrams for request/event flows
- syntax-highlighted excerpts with 1–6 lines emphasized at a time
- concise callouts for side effects, storage, network calls, retries, and auth

Avoid:

- full-screen paragraphs
- entire source files
- tiny text
- decorative animation that competes with the explanation
- representing an inferred connection with the same certainty as a verified one

## Pacing

- Aim for about 120–170 spoken Chinese characters per minute-equivalent segment after natural pauses; adapt to TTS speed when audio exists.
- Allow diagrams time to settle before changing focus.
- Keep code close-ups long enough to read the highlighted lines.
- Split complicated flows into multiple scenes instead of overloading one diagram.

## Subtitles

- Use the narration as the source of truth.
- Break subtitles at natural clauses.
- Avoid more than two subtitle lines at once.
- Keep code identifiers intact when possible.

## Remotion implementation

- Build reusable components for architecture nodes, arrows, file trees, code windows, captions, and section titles.
- Drive scene timing from storyboard data rather than scattering magic frame numbers.
- Prefer deterministic animations based on frame/time.
- Preload local images, screenshots, and fonts before render when required.
- Keep source excerpts local to the generated video project and record their repository path in metadata.
- Use the environment's current Remotion best practices or an installed Remotion Skill when available.

## Default render

- 1920×1080
- 30 FPS
- H.264 MP4
- 16:9

Change these defaults when the user asks for vertical, short-form, high-frame-rate, or presentation-style output.
