# Codebase Video Explainer

**English** | [简体中文](README.zh-CN.md)

A reusable Agent Skill that turns an unfamiliar software repository into an evidence-backed developer explainer video.

It builds a mental model from real source code, traces representative execution paths, then generates architecture visuals, a storyboard, natural Chinese narration with exact TTS-derived subtitles, a Remotion project when available, and an MP4 with an FFmpeg fallback when needed.

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
- Prefer Remotion; fall back to FFmpeg when the rendering environment cannot install or run Remotion.

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
│   │   └── natural-tts.yml
│   └── remotion-template/
├── references/
│   ├── analysis-workflow.md
│   ├── production-pipeline.md
│   ├── storyboard-format.md
│   └── video-style.md
└── scripts/
    ├── scan_codebase.py
    ├── build_project_manifest.py
    ├── build_subtitles.py
    ├── build_tts_job.py
    ├── synthesize_edge_tts.py
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

The initializer prefers `storyboard.timed.json` when TTS timing exists.

If npm/Remotion is unavailable, use FFmpeg to render the same timed scene visuals, narration, and subtitles. Do not claim the output was rendered by Remotion when FFmpeg was used.

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
