# Codebase Video Explainer

**English** | [简体中文](README.zh-CN.md)

**Codebase Video Explainer is an Agent Skill for ChatGPT.** It teaches ChatGPT how to turn an unfamiliar software repository into an evidence-backed developer explainer video.

The Skill orchestrates a repeatable workflow: build a mental model from real source code, trace representative execution paths, generate architecture visuals and a storyboard, create natural Chinese narration with exact TTS-derived subtitles, then render the final MP4 with Remotion. Rendering prefers local Remotion, moves to GitHub Actions Remotion when local npm/browser access is blocked, and uses FFmpeg only as the final fallback.

## Video demo

[![Watch the Codebase Video Explainer demo](docs/media/codebase-video-explainer-preview.png)](docs/media/codebase-video-explainer-demo.mp4)

This project can explain itself: the demo above was generated from this repository with the same analysis → TTS → exact subtitles → Remotion pipeline described below.

[Watch or download the MP4](docs/media/codebase-video-explainer-demo.mp4)


## Install and use as a Skill

This repository is the **source repository for one Agent Skill**. The distributable Skill bundle should contain only:

```text
SKILL.md
agents/
scripts/
references/
assets/
```

Repository-facing files such as this README and `docs/media/` are intentionally not part of the packaged Skill.

Typical usage after installing the Skill:

```text
Analyze this GitHub repository and create a Chinese developer explainer video.
```

The Skill should auto-select its bundled workflow, scripts, references, and rendering fallbacks as needed.

## What it produces

Generated artifacts live under `.codebase-video/` in the target project:

- `scan.json`
- `project-manifest.json`
- `project-analysis.json`
- `architecture.mmd` / optional `architecture.svg`
- `storyboard.json`
- `narration.zh-CN.md`
- `narration.mp3`
- `timings.json`
- `storyboard.timed.json`
- `subtitles.srt`
- `remotion/`
- `output.mp4`

## Example prompts

- `分析当前项目并生成一个 10 分钟左右的中文项目讲解视频。`
- `把这个 GitHub 仓库做成一个适合新开发者 onboarding 的架构讲解视频。`
- `重点讲清楚这个项目从 API 请求到数据库写入的完整链路，并生成视频。`

## Design principles

- Analyze before animating.
- Prefer execution paths over file-by-file tours.
- Keep architectural claims tied to source evidence.
- Label inference and unknowns instead of hallucinating relationships.
- Keep generated artifacts isolated from production code.
- Use natural, scene-level narration instead of sentence-by-sentence audio splicing.
- Treat narration audio as the master timeline.
- Derive final subtitles from real TTS speech boundaries, never character-count timing when audio exists.
- Prefer a real Remotion render locally; if local npm/browser access fails, use GitHub Actions Remotion rendering when permitted before falling back to FFmpeg.

## Skill layout

```text
codebase-video-explainer/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── github-actions/
│   │   ├── natural-tts.yml
│   │   └── remotion-render.yml
│   └── remotion-template/
├── references/
│   ├── analysis-workflow.md
│   ├── production-pipeline.md
│   ├── quality-gates.md
│   ├── storyboard-format.md
│   └── video-style.md
└── scripts/
    ├── scan_codebase.py
    ├── build_project_manifest.py
    ├── build_subtitles.py
    ├── build_tts_job.py
    ├── synthesize_edge_tts.py
    ├── prepare_remotion_job.py
    ├── check_av_sync.py
    ├── capture_screenshots.py
    ├── render_mermaid.py
    └── init_remotion_project.py
```

## V3 natural voice and exact subtitle pipeline

The preferred Chinese narration path is Edge TTS with `zh-CN-YunyangNeural`:

```bash
python scripts/synthesize_edge_tts.py \
  --storyboard /path/to/repo/.codebase-video/storyboard.json \
  --output-dir /path/to/repo/.codebase-video
```

Default delivery settings:

```text
voice: zh-CN-YunyangNeural
rate: -5%
pitch: -2Hz
scene gap: 0.7 s
```

The script synthesizes each scene as one continuous utterance and uses Edge TTS `SentenceBoundary` metadata to create exact SRT timing. It also writes a measured `storyboard.timed.json`, so the video timeline follows the real narration duration instead of forcing speech into estimated scene lengths.

Do not use `build_subtitles.py` for final subtitles after TTS audio exists. That helper is only a draft/estimated timing fallback.

## Free GitHub Actions fallback

If the local execution environment cannot reach Edge TTS, the Skill includes a free GitHub Actions fallback:

1. Generate `tts-jobs/current/scenes.json` with `scripts/build_tts_job.py`.
2. Copy `assets/github-actions/natural-tts.yml` to `.github/workflows/codebase-video-natural-tts.yml` in an Actions-capable repository the user permits using.
3. Run the workflow and download the `codebase-video-natural-tts` artifact.
4. Reuse the returned `narration.mp3`, exact `subtitles.srt`, and `timings.json` in the video project.

This path requires no Azure subscription or TTS API key.

## Remotion and FFmpeg

Use a dedicated Remotion Skill when available. Otherwise initialize the bundled fallback project:

```bash
python scripts/init_remotion_project.py --root /path/to/repo --force
```

The initializer prefers `storyboard.timed.json` when TTS timing exists. Try a real local Remotion render first.

If local npm, DNS, browser download, or container limits block Remotion, prepare a portable GitHub Actions job:

```bash
python scripts/prepare_remotion_job.py \
  --project /path/to/repo/.codebase-video/remotion \
  --job-dir /path/to/actions-repo/render-jobs/current \
  --composition CodebaseExplainer \
  --audio-run-id 123456789 \
  --audio-artifact-name codebase-video-natural-tts \
  --force
```

When `--audio-run-id` is supplied, the prepared job omits the copied narration binary and the workflow downloads `narration.mp3` from that earlier Actions artifact. Then copy `assets/github-actions/remotion-render.yml` to `.github/workflows/codebase-video-remotion-render.yml` in a repository the user permits using. The workflow runs a preview still plus the real Remotion CLI render, verifies the MP4 with ffprobe, and uploads `codebase-video-remotion-render`.

Use FFmpeg only if local and permitted GitHub Actions Remotion rendering are unavailable or fail. Do not claim the output was rendered by Remotion when FFmpeg was used.

## Sync QA

After rendering, verify the final timeline:

```bash
python scripts/check_av_sync.py \
  --audio /path/to/repo/.codebase-video/narration.mp3 \
  --subtitles /path/to/repo/.codebase-video/subtitles.srt \
  --video /path/to/repo/.codebase-video/output.mp4
```

Also sample-check subtitle sync near the beginning, middle, and end of the video to catch cumulative drift.

## Safety

The analysis helpers deliberately avoid secret-like files such as `.env`, private keys, and credential files. Never expose real credentials, tokens, cookies, passwords, or private key material in narration, screenshots, generated video assets, or logs.
