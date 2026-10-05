# Storyboard format

Create `.codebase-video/storyboard.json` as valid JSON. Use this schema as the stable interchange format between analysis and video implementation.

## Top-level shape

```json
{
  "title": "Project explainer title",
  "language": "zh-CN",
  "audience": "Developer new to the project",
  "target_duration_seconds": 600,
  "scenes": []
}
```

## Scene shape

Every scene should contain:

```json
{
  "id": "request-flow",
  "title": "一次请求如何跑完整个系统",
  "purpose": "Teach the primary request path end to end",
  "duration_seconds": 75,
  "narration": "...",
  "visual_type": "execution-flow",
  "visuals": [
    "API route card",
    "service card",
    "database card",
    "animated arrows"
  ],
  "animation": "Reveal one hop at a time while the active hop is emphasized",
  "evidence": [
    {"path": "src/api/chat.ts", "symbol": "POST"},
    {"path": "src/services/chat.ts", "symbol": "handleChat"}
  ],
  "code_excerpts": [
    {
      "path": "src/api/chat.ts",
      "symbol": "POST",
      "reason": "Shows the handoff from HTTP to application service"
    }
  ]
}
```

## Recommended scene order

Adapt rather than mechanically forcing every section:

1. Hook and project purpose — 20–45 s.
2. Technology stack and runtime boundary — 20–45 s.
3. High-level architecture — 45–90 s.
4. Module map / directory mental model — 45–90 s.
5. Primary end-to-end execution path — 90–180 s.
6. Data/storage/auth/external integrations relevant to that flow — 60–120 s.
7. Two or three key code excerpts — 60–120 s.
8. How to make a common change safely — 45–90 s.
9. Recap — 20–45 s.

## Scene rules

- One teaching purpose per scene.
- Do not create a scene that is merely a paragraph on screen.
- Use no more than roughly 3–7 simultaneously emphasized concepts.
- Narration can be detailed; on-screen text should remain concise.
- Keep evidence paths in the storyboard even when they are not rendered on screen.
- Use `verified`, `inferred`, or `unknown` language consistent with the analysis.
- If a code excerpt is used, copy it from the repository during video generation rather than embedding stale source in the storyboard.
