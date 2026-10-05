#!/usr/bin/env python3
"""Build a portable Edge TTS job JSON from storyboard narration."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MARKDOWN = re.compile(r"(^|\n)#{1,6}\s+|[`*_>#-]+")


def clean_markdown(text: str) -> str:
    text = MARKDOWN.sub(" ", text)
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storyboard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice", default="zh-CN-YunyangNeural")
    parser.add_argument("--rate", default="-5%")
    parser.add_argument("--pitch", default="-2Hz")
    parser.add_argument("--volume", default="+0%")
    args = parser.parse_args()

    source = Path(args.storyboard).resolve()
    output = Path(args.output).resolve()
    try:
        storyboard = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid storyboard JSON: {source}: {exc}") from exc

    scenes = storyboard.get("scenes") if isinstance(storyboard, dict) else None
    if not isinstance(scenes, list) or not scenes:
        raise SystemExit("Storyboard must contain a non-empty scenes array")

    job_scenes = []
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise SystemExit(f"Scene {index} is not an object")
        text = clean_markdown(str(scene.get("narration", "")))
        if not text:
            raise SystemExit(f"Scene {index} has empty narration")
        job_scenes.append(
            {
                "index": index,
                "id": str(scene.get("id", index)),
                "title": str(scene.get("title", scene.get("id", index))),
                "text": text,
            }
        )

    payload = {
        "voice": args.voice,
        "rate": args.rate,
        "pitch": args.pitch,
        "volume": args.volume,
        "scenes": job_scenes,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote TTS job with {len(job_scenes)} scenes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
