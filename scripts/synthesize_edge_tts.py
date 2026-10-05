#!/usr/bin/env python3
"""Synthesize narration with edge-tts when it is installed."""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

MARKDOWN = re.compile(r"(^|\n)#{1,6}\s+|[`*_>#-]+")


def clean_markdown(text: str) -> str:
    text = MARKDOWN.sub(" ", text)
    return " ".join(text.split())


async def synthesize(text: str, output: Path, voice: str, rate: str, volume: str) -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit("edge-tts is not installed. Run: pip install edge-tts") from exc
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(str(output))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--rate", default="+0%")
    parser.add_argument("--volume", default="+0%")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    text = clean_markdown(source.read_text(encoding="utf-8"))
    if not text:
        raise SystemExit("Narration input is empty after Markdown cleanup")
    print(f"Voice: {args.voice}; characters: {len(text)}; output: {output}")
    if args.dry_run:
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize(text, output, args.voice, args.rate, args.volume))
    print(f"Wrote narration audio to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
