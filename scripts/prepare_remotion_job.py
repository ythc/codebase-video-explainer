#!/usr/bin/env python3
"""Prepare a portable GitHub Actions Remotion render job from a generated project."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

EXCLUDED_DIRS = {"node_modules", "out", ".git", ".cache", ".parcel-cache"}


def ignore_paths(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_DIRS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Source Remotion project directory")
    parser.add_argument("--job-dir", required=True, help="Destination render job directory")
    parser.add_argument("--composition", default="CodebaseExplainer")
    parser.add_argument("--entrypoint", default="src/index.ts")
    parser.add_argument("--output-name", default="output.mp4")
    parser.add_argument("--artifact-name", default="codebase-video-remotion-render")
    parser.add_argument("--preview-frame", type=int, default=90)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--audio-run-id", default="", help="Optional prior GitHub Actions run ID containing narration")
    parser.add_argument("--audio-artifact-name", default="codebase-video-natural-tts")
    parser.add_argument("--audio-artifact-file", default="narration.mp3")
    parser.add_argument("--audio-target", default="public/narration.mp3")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source = Path(args.project).resolve()
    job_dir = Path(args.job_dir).resolve()
    project_dir = job_dir / "project"

    if not source.is_dir():
        raise SystemExit(f"Remotion project not found: {source}")
    if not (source / "package.json").is_file():
        raise SystemExit(f"package.json not found in Remotion project: {source}")
    if args.preview_frame < 0:
        parser.error("--preview-frame must be >= 0")
    if args.concurrency < 1:
        parser.error("--concurrency must be >= 1")
    if "/" in args.output_name or "\\" in args.output_name:
        parser.error("--output-name must be a file name, not a path")

    if job_dir.exists():
        if not args.force:
            raise SystemExit(f"Job directory already exists: {job_dir}; use --force to replace it")
        shutil.rmtree(job_dir)

    job_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, project_dir, ignore=ignore_paths)

    audio_target = Path(args.audio_target)
    if audio_target.is_absolute() or ".." in audio_target.parts:
        parser.error("--audio-target must stay inside the copied project")

    if args.audio_run_id:
        copied_audio = project_dir / audio_target
        if copied_audio.is_file():
            copied_audio.unlink()

    config = {
        "project_path": "render-jobs/current/project",
        "entrypoint": args.entrypoint,
        "composition": args.composition,
        "output_name": args.output_name,
        "artifact_name": args.artifact_name,
        "preview_frame": args.preview_frame,
        "concurrency": args.concurrency,
        "audio_run_id": str(args.audio_run_id),
        "audio_artifact_name": args.audio_artifact_name,
        "audio_artifact_file": args.audio_artifact_file,
        "audio_target": args.audio_target,
    }
    (job_dir / "render-job.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Prepared Remotion render job: {job_dir}")
    print(f"Project files: {project_dir}")
    print(f"Config: {job_dir / 'render-job.json'}")
    if args.audio_run_id:
        print(
            "Narration will be downloaded from Actions run "
            f"{args.audio_run_id} / artifact {args.audio_artifact_name}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
