# Codebase Video Explainer

A reusable Agent Skill that turns an unfamiliar software repository into an evidence-backed developer explainer video.

It first builds a mental model from real source code, traces representative execution paths, then generates an architecture diagram, storyboard, Chinese narration/subtitles by default, a Remotion project, and an MP4 when the environment can render it.

## What it produces

Generated artifacts live under `.codebase-video/` in the target project:

- `scan.json`
- `project-manifest.json`
- `project-analysis.json`
- `architecture.mmd`
- `storyboard.json`
- `narration.zh-CN.md`
- `remotion/`
- `output.mp4`

## Example prompts

- `分析当前项目并生成一个 10 分钟左右的中文项目讲解视频。`
- `把这个 GitHub 仓库做成一个适合新开发者 onboarding 的架构讲解视频。`
- `重点讲清楚这个项目从 API 请求到数据库写入的完整链路，并生成 Remotion 视频。`

## Design principles

- Analyze before animating.
- Prefer execution paths over file-by-file tours.
- Keep architectural claims tied to source evidence.
- Label inference and unknowns instead of hallucinating relationships.
- Keep generated artifacts isolated from production code.
- Use a Remotion-specific Skill when available; otherwise generate a standard Remotion project using the current environment's supported setup.

## Skill layout

```text
codebase-video-explainer/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── analysis-workflow.md
│   ├── storyboard-format.md
│   └── video-style.md
└── scripts/
    ├── scan_codebase.py
    └── build_project_manifest.py
```

## Local helper usage

```bash
python scripts/scan_codebase.py \
  --root /path/to/repo \
  --output /path/to/repo/.codebase-video/scan.json

python scripts/build_project_manifest.py \
  --root /path/to/repo \
  --scan /path/to/repo/.codebase-video/scan.json \
  --output /path/to/repo/.codebase-video/project-manifest.json
```

The helper scripts deliberately avoid reading secret-like files such as `.env`, private keys, and credential files.
