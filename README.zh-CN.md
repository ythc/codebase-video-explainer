# Codebase Video Explainer

[English](README.md) | **简体中文**

**Codebase Video Explainer 是一个可安装到 Codex 的 Plugin，里面包含一个专门把软件代码仓库转换成开发者讲解视频的 Agent Skill。**

把本地项目或 GitHub 仓库交给 Codex，这个 Skill 会分析真实源码、建立有证据支撑的项目心智模型、设计面向开发者的分镜、生成自然中文旁白和精确字幕，并使用 Remotion 输出最终 MP4。

## 项目讲解视频

[![观看 Codebase Video Explainer 项目讲解视频](docs/media/codebase-video-explainer-preview.png)](docs/media/codebase-video-explainer-demo.mp4)

[观看或下载 MP4](docs/media/codebase-video-explainer-demo.mp4)

这支演示视频就是由 **Codebase Video Explainer 使用当前仓库自身生成的**。它展示了完整的用户流程：代码仓库分析 → 有源码证据支撑的架构与分镜 → 自然中文旁白和精确字幕 → Remotion 渲染 → 最终质量检查。

## 安装到 Codex

### 1. 添加 Marketplace

```bash
codex plugin marketplace add ythc/codebase-video-explainer --ref main
```

可选检查：

```bash
codex plugin marketplace list
```

### 2. 安装 Plugin

启动 Codex：

```bash
codex
```

输入：

```text
/plugins
```

找到 **Codebase Video Explainer**，选择 **Install plugin**。

安装后新建一个 Codex 会话。

## 使用

直接告诉 Codex：

```text
分析这个 GitHub 项目，并生成一支中文开发者讲解视频。
```

或者：

```text
使用 Codebase Video Explainer 分析当前代码库，面向新开发者进行讲解，并用 Remotion 生成视频。
```

正常使用时不需要手工运行仓库里的 Python 脚本。

## 能做什么

- **分析**：扫描代码仓库，识别关键模块并追踪代表性执行链路。
- **讲解**：生成有源码证据支撑的架构模型和开发者分镜。
- **旁白**：生成自然中文旁白和精确字幕时间轴。
- **渲染**：优先输出真实 Remotion 成片，并在需要时使用支持的 fallback。
- **校验**：在交付前检查音频、字幕和视频时间轴。

## 输出

生成内容默认放在目标项目的 `.codebase-video/`：

```text
.codebase-video/
├── project-analysis.json
├── architecture.mmd
├── architecture.svg
├── storyboard.json
├── narration.zh-CN.md
├── narration.mp3
├── timings.json
├── storyboard.timed.json
├── subtitles.srt
├── remotion/
└── output.mp4
```

## Plugin 结构

```text
.agents/plugins/marketplace.json

plugins/codebase-video-explainer/
├── plugin.json
├── .codex-plugin/
│   └── plugin.json
└── skills/
    └── codebase-video-explainer/
        ├── SKILL.md
        ├── agents/
        ├── scripts/
        ├── references/
        └── assets/
```

仓库顶层 README 和 `docs/media/` 只用于项目展示。真正安装到 Codex 的 Skill 位于 `plugins/codebase-video-explainer/skills/codebase-video-explainer/`。

## 更新

```bash
codex plugin marketplace upgrade codebase-video-explainer
```

更新后新建一个 Codex 会话。

## 安全

Skill 会避免在分析、旁白、截图、生成素材和日志中暴露敏感配置或凭据，并尽量把生成内容与生产源码隔离。
