#!/usr/bin/env python3
"""Create a Remotion workspace from the bundled fallback template."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def copy_optional(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if source.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Target repository root")
    parser.add_argument("--storyboard", help="Storyboard JSON path; defaults to .codebase-video/storyboard.json")
    parser.add_argument("--output", help="Remotion output directory; defaults to .codebase-video/remotion")
    parser.add_argument("--force", action="store_true", help="Replace an existing generated Remotion project")
    args = parser.parse_args()

    repo = Path(args.root).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    template = skill_root / "assets" / "remotion-template"
    output = Path(args.output).resolve() if args.output else repo / ".codebase-video" / "remotion"
    if args.storyboard:
        storyboard = Path(args.storyboard).resolve()
    else:
        timed = repo / ".codebase-video" / "storyboard.timed.json"
        storyboard = timed if timed.exists() else repo / ".codebase-video" / "storyboard.json"

    if not template.is_dir():
        raise SystemExit(f"Bundled Remotion template not found: {template}")
    if output.exists():
        if not args.force:
            raise SystemExit(f"Output already exists: {output}. Re-run with --force to replace it.")
        shutil.rmtree(output)

    shutil.copytree(template, output)

    if storyboard.exists():
        try:
            data = json.loads(storyboard.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid storyboard JSON: {storyboard}: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
            raise SystemExit("Storyboard must contain a top-level scenes array")
        target = output / "src" / "storyboard.json"
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    copy_optional(repo / ".codebase-video" / "architecture.mmd", output / "public" / "architecture.mmd")
    copy_optional(repo / ".codebase-video" / "screenshots", output / "public" / "screenshots")
    copy_optional(repo / ".codebase-video" / "narration.mp3", output / "public" / "narration.mp3")
    copy_optional(repo / ".codebase-video" / "timings.json", output / "public" / "timings.json")
    copy_optional(repo / ".codebase-video" / "subtitles.srt", output / "public" / "subtitles.srt")

    print(f"Created Remotion project: {output}")
    print("Next commands:")
    print(f"  cd {output}")
    print("  npm install")
    print("  npm run studio")
    print("  npm run render")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
