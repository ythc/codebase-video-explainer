# Codebase Video Explainer

[English](README.md) | **简体中文**

一个可复用的 Agent Skill：把陌生的软件项目转换成**有源码证据支撑的开发者讲解视频**。

它会先从真实代码建立项目心智模型，追踪具有代表性的执行链路，再生成架构图、分镜、自然中文旁白、精确字幕和 Remotion 工程。渲染优先本地 Remotion；如果本地 npm / 浏览器受限，则优先转到 GitHub Actions 真 Remotion；只有两者都不可用时才用 FFmpeg 保底。

## 典型产物

默认输出到目标项目的 `.codebase-video/`：

- `scan.json`：项目扫描结果
- `project-manifest.json`：技术栈、依赖、脚本和入口
- `project-analysis.json`：证据化架构与执行链路分析
- `architecture.mmd` / `architecture.svg`：架构图
- `storyboard.json`：初始分镜
- `narration.zh-CN.md`：中文口播稿
- `narration.mp3`：最终旁白
- `timings.json`：真实音频时间轴
- `storyboard.timed.json`：按真实语音时长修正后的分镜
- `subtitles.srt`：真实 TTS 边界生成的字幕
- `remotion/`：Remotion 工程
- `output.mp4`：最终视频

## 适用场景

- 快速理解陌生 GitHub 项目或本地代码仓库
- 为新成员制作 onboarding 视频
- 解释 API、数据库、队列、鉴权、第三方服务之间的调用关系
- 把真实请求或业务流程做成执行链路动画
- 生成中文项目讲解视频

## 关键设计原则

- **先分析，后动画。**
- **执行链路优先于目录导览。**
- **架构结论必须有源码证据。**
- **旁白按场景整段生成，不要一句一句拼接。**
- **真实音频是最终时间轴。**
- **有 TTS 时禁止再按字符数估字幕时间。**
- **最终字幕优先使用 Edge TTS `SentenceBoundary`。**
- **优先真正的 Remotion 渲染；本地 npm / 浏览器受限时，先尝试用户允许的 GitHub Actions Remotion，再使用 FFmpeg fallback。**
- **默认不使用 `espeak` / `pyttsx3` 这类机械音作为正式成片旁白。**

## V3：自然中文旁白 + 精确字幕

推荐默认音色：

```text
zh-CN-YunyangNeural
```

推荐参数：

```text
语速：-5%
音高：-2Hz
场景间隔：0.7 秒
```

直接从 `storyboard.json` 生成整套旁白与时间轴：

```bash
python scripts/synthesize_edge_tts.py \
  --storyboard /path/to/repo/.codebase-video/storyboard.json \
  --output-dir /path/to/repo/.codebase-video
```

它会：

1. 每个场景只发起一次连续 TTS；
2. 同时记录 Edge TTS 的 `SentenceBoundary`；
3. 对人声做统一响度处理；
4. 生成 `narration.mp3`；
5. 根据真实发音 offset / duration 生成 `subtitles.srt`；
6. 生成 `timings.json`；
7. 把真实语音时长写入 `storyboard.timed.json`。

这样最终视频不会再出现“前面字幕还行，后面越来越偏”的累计漂移。

> `scripts/build_subtitles.py` 现在只适合在还没有 TTS 音频时生成**草稿字幕**。有真实语音以后，最终字幕必须以真实 TTS 时间戳为准。

## 免费 GitHub Actions TTS fallback

如果当前执行环境无法访问 Edge TTS，可以使用 GitHub Actions 免费生成，不需要 Azure 订阅或 TTS API Key。

先把分镜转换成 TTS job：

```bash
python scripts/build_tts_job.py \
  --storyboard /path/to/repo/.codebase-video/storyboard.json \
  --output /path/to/actions-repo/tts-jobs/current/scenes.json
```

再把：

```text
assets/github-actions/natural-tts.yml
```

复制到允许使用的 GitHub 仓库：

```text
.github/workflows/codebase-video-natural-tts.yml
```

工作流会自动生成并上传 artifact：

- `narration.mp3`
- `subtitles.srt`
- `timings.json`
- TTS 边界元数据

只有在用户允许的情况下才向其仓库提交工作流文件。

## Remotion

如果有专门的 Remotion Skill，优先使用它。

否则：

```bash
python scripts/init_remotion_project.py \
  --root /path/to/repo \
  --force
```

当 `storyboard.timed.json` 存在时，初始化脚本会优先使用真实 TTS 时长，而不是最初估算的 `storyboard.json`。

## GitHub Actions 真 Remotion fallback

如果当前容器无法访问 npm registry、无法下载 Remotion 浏览器，或者本地渲染受执行时限影响，不要立刻降级成 FFmpeg。只要用户允许使用一个支持 Actions 的仓库，就先把完成后的 Remotion 工程准备成可移植渲染任务：

```bash
python scripts/prepare_remotion_job.py \
  --project /path/to/repo/.codebase-video/remotion \
  --job-dir /path/to/actions-repo/render-jobs/current \
  --composition CodebaseExplainer \
  --audio-run-id 123456789 \
  --audio-artifact-name codebase-video-natural-tts \
  --force
```

然后把：

```text
assets/github-actions/remotion-render.yml
```

复制为：

```text
.github/workflows/codebase-video-remotion-render.yml
```

如果提供 `--audio-run-id`，准备脚本会从 render job 中移除已复制的 `public/narration.mp3`，由 Actions 从前一次 TTS artifact 下载旁白，避免为了渲染提交音频二进制。这个 workflow 会实际执行：`npm install → TypeScript 检查 → Remotion still → Remotion render → ffprobe 验证 → artifact 上传`。最终 artifact 名称默认为 `codebase-video-remotion-render`，包含真正由 Remotion CLI 生成的 MP4、`preview.png` 和 `ffprobe.json`。

只有 Remotion CLI 的完整渲染步骤成功时，才能把成片称为“Remotion 渲染”。只有在本地和获准的 GitHub Actions Remotion 都不可用或失败时，才进入 FFmpeg fallback。

## FFmpeg fallback

如果当前环境无法安装 npm / Remotion CLI，不要把任务停在“只有工程文件”。在画面素材已经准备好的情况下，可以用 FFmpeg 按同一份 `storyboard.timed.json`、`narration.mp3` 和精确 `subtitles.srt` 生成 MP4。

注意：

- 不能拿已经烧过旧字幕的 MP4 再叠新版字幕；
- 字幕时间变化时，应从干净场景画面重新渲染；
- 对主要由静态技术卡片组成的视频，可以降低帧率来缩短渲染时间，但要保持 1080p 可读性；
- 如果最终使用 FFmpeg，要明确说明并非 Remotion 渲染。

## 同步质量检查

最终成片后运行：

```bash
python scripts/check_av_sync.py \
  --audio /path/to/repo/.codebase-video/narration.mp3 \
  --subtitles /path/to/repo/.codebase-video/subtitles.srt \
  --video /path/to/repo/.codebase-video/output.mp4
```

同时人工抽查三个位置：

- 开头 30～60 秒
- 视频中段
- 最后 1 分钟

检查是否存在字幕累计漂移。

## Skill 目录结构

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

## 安全原则

不要输出或写入视频：

- `.env` 真实值
- API Token
- Cookie
- 密码
- 私钥
- 证书私密部分
- Secret Manager 返回的真实凭据

只展示配置名称、接口关系和必要的非敏感结构。
