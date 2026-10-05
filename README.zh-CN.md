# Codebase Video Explainer

[English](README.md) | **简体中文**

一个可复用的 Agent Skill：把陌生的软件项目转换成**有源码证据支撑的开发者讲解视频**。

它会先从真实代码中建立项目心智模型，追踪具有代表性的执行链路，再生成架构图、分镜脚本、中文旁白/字幕、Remotion 视频工程，并在运行环境支持时渲染出 MP4。

## 它能做什么

在目标项目中生成 `.codebase-video/` 工作目录，典型产物包括：

- `scan.json`：项目文件清单与基础扫描结果
- `project-manifest.json`：技术栈、依赖、脚本、入口等项目元信息
- `project-analysis.json`：有证据支撑的项目结构、模块关系与执行链路分析
- `architecture.mmd`：Mermaid 架构图源文件
- `architecture.svg`：可选的架构图渲染结果
- `storyboard.json`：逐场景视频分镜
- `narration.zh-CN.md`：默认中文旁白文稿
- `subtitles.srt`：根据场景时间轴生成的字幕
- `narration.mp3`：可选的 TTS 中文配音
- `screenshots/`：可选的 UI 截图素材
- `remotion/`：生成的 Remotion 视频工程
- `output.mp4`：环境支持时生成的最终视频

## 适合什么场景

这个 Skill 适合：

- 快速理解一个陌生 GitHub 项目或本地代码仓库
- 给新成员制作项目 onboarding 视频
- 解释前后端、API、数据库、队列、AI 服务之间的调用关系
- 把一次真实请求或业务流程做成可视化执行链路
- 从「项目结构」逐步讲到「关键文件」和「关键代码」
- 为复杂项目自动生成中文技术讲解视频

## 示例提示词

```text
分析当前项目并生成一个 10 分钟左右的中文项目讲解视频。
```

```text
把这个 GitHub 仓库做成一个适合新开发者 onboarding 的架构讲解视频。
```

```text
重点讲清楚这个项目从 API 请求到数据库写入的完整链路，并生成 Remotion 视频。
```

```text
先分析项目结构，再选择 2 条最有代表性的执行链路，生成中文旁白、字幕和 MP4。
```

## 设计原则

- **先分析，后动画。** 不在没读懂项目之前直接做视频。
- **执行链路优先于目录导览。** 重点解释代码是怎么真正跑起来的。
- **架构结论必须绑定源码证据。** 不根据文件名臆测模块关系。
- **明确区分已验证、推断和未知。** 避免把猜测说成事实。
- **尽量不修改业务源码。** 生成内容默认隔离到 `.codebase-video/`。
- **优先复用专业 Remotion Skill。** 没有时才使用本仓库内置的 fallback 模板。
- **避免泄露敏感信息。** 不读取或输出 `.env`、私钥、凭证、Token 等秘密值。

## 工作流程

大致流程如下：

```text
代码仓库
   ↓
扫描项目结构
   ↓
识别技术栈 / 入口 / 模块 / 外部服务
   ↓
建立证据化项目心智模型
   ↓
选择 1～3 条代表性执行链路
   ↓
生成架构图 + 分镜 + 中文旁白
   ↓
生成字幕 / 可选 TTS / 可选截图
   ↓
生成 Remotion 工程
   ↓
预览与检查
   ↓
渲染 MP4
```

## Skill 目录结构

```text
codebase-video-explainer/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── agents/
│   └── openai.yaml
├── assets/
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
    ├── capture_screenshots.py
    ├── init_remotion_project.py
    ├── render_mermaid.py
    └── synthesize_edge_tts.py
```

## 本地辅助脚本

### 1. 扫描代码仓库

```bash
python scripts/scan_codebase.py \
  --root /path/to/repo \
  --output /path/to/repo/.codebase-video/scan.json
```

默认会忽略：

- `.git`
- `node_modules`
- `dist`
- `build`
- `.next`
- `target`
- `vendor`
- Python 虚拟环境和缓存目录
- `.codebase-video`

同时会跳过 `.env`、私钥、凭证文件等可能包含敏感信息的文件。

### 2. 生成项目 manifest

```bash
python scripts/build_project_manifest.py \
  --root /path/to/repo \
  --scan /path/to/repo/.codebase-video/scan.json \
  --output /path/to/repo/.codebase-video/project-manifest.json
```

用于识别 Node.js、Python、Go、Rust、JVM 等生态信息，以及包管理器、框架、入口候选和部署配置。

## V2 视频生产工具

### Mermaid 架构图渲染

```bash
python scripts/render_mermaid.py \
  --input /path/to/repo/.codebase-video/architecture.mmd \
  --output /path/to/repo/.codebase-video/architecture.svg
```

优先使用本机 `mmdc`，没有时会尝试通过 `npx @mermaid-js/mermaid-cli` 调用。

### 自动生成字幕

```bash
python scripts/build_subtitles.py \
  --storyboard /path/to/repo/.codebase-video/storyboard.json \
  --output /path/to/repo/.codebase-video/subtitles.srt
```

会根据每个场景的 `duration_seconds` 和旁白内容生成 SRT 时间轴。

### UI 自动截图

当运行中的项目页面有助于讲解时，可以先创建截图计划，然后通过 Playwright 自动截图：

```bash
python scripts/capture_screenshots.py \
  --plan /path/to/repo/.codebase-video/screenshot-plan.json \
  --output-dir /path/to/repo/.codebase-video/screenshots
```

截图不是必选项，只在能明显提升理解时使用。

### 中文 TTS 配音

如果执行环境已经安装 `edge-tts`，可以生成中文旁白：

```bash
python scripts/synthesize_edge_tts.py \
  --input /path/to/repo/.codebase-video/narration.zh-CN.md \
  --output /path/to/repo/.codebase-video/narration.mp3
```

默认语音为：

```text
zh-CN-XiaoxiaoNeural
```

TTS 是可选能力。没有 TTS 时，Skill 仍应完成旁白文本、字幕、Remotion 工程和可渲染的视觉内容。

### 初始化 Remotion 工程

```bash
python scripts/init_remotion_project.py \
  --root /path/to/repo \
  --force
```

然后：

```bash
cd /path/to/repo/.codebase-video/remotion
npm install
npm run studio
npm run render
```

内置模板只是 fallback。最终视频应根据真实项目的架构、代码、截图和执行链路进行定制，而不是直接使用占位画面作为最终成品。

## 默认视频规格

默认情况下：

- 语言：简体中文
- 时长：根据项目复杂度自动调整，通常约 5～15 分钟
- 分辨率：1920 × 1080
- 帧率：30 FPS
- 编码：H.264
- 容器：MP4
- 讲解对象：第一次接触该项目的开发者

## 推荐视频结构

一个典型的视频会按以下顺序组织：

1. 项目是做什么的
2. 技术栈和运行边界
3. 高层架构
4. 关键模块和目录心智模型
5. 一条主要请求 / 事件执行链路
6. 数据库、鉴权、外部服务等关键边界
7. 2～3 个重要代码片段
8. 修改一个常见需求应该从哪里入手
9. 总结与回顾

## 安全原则

Skill 应避免：

- 输出 `.env` 中的真实值
- 输出 API Token、Cookie、密码或密钥
- 把凭证文件复制进视频工程
- 因为目录名或 README 描述就断言代码关系
- 为了截图或视频生成而擅自修改业务代码

## 安装

可以直接使用仓库根目录中的：

```text
skill.zip
```

将其作为 Skill 安装包上传即可。

## 当前状态

V2 已包含：

- 项目扫描与 manifest 生成
- 证据化代码分析工作流
- 分镜规范
- Mermaid 架构图支持
- SRT 字幕生成
- Playwright 截图辅助
- 可选 Edge TTS 中文配音
- Remotion fallback 工程模板
- MP4 渲染工作流

后续可以继续增强真实项目上的自动化程度，例如更智能的代码摘录、架构动画组件、TTS 时间轴对齐和自动质量检查。
