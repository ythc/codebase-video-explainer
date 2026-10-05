#!/usr/bin/env python3
"""Build a deterministic SRT subtitle file from storyboard narration and scene durations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SENTENCE_SPLIT = re.compile(r"(?<=[.!?;:。！？；：])\s*")


def timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def chunks(text: str, max_chars: int) -> list[str]:
    text = " ".join(text.strip().split())
    if not text:
        return []
    sentences = [part.strip() for part in SENTENCE_SPLIT.split(text) if part.strip()]
    result: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
            continue
        if current:
            result.append(current)
        while len(sentence) > max_chars:
            result.append(sentence[:max_chars])
            sentence = sentence[max_chars:]
        current = sentence
    if current:
        result.append(current)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storyboard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-chars", type=int, default=34)
    args = parser.parse_args()

    data = json.loads(Path(args.storyboard).read_text(encoding="utf-8"))
    scenes = data.get("scenes") or []
    if not isinstance(scenes, list):
        raise SystemExit("Storyboard scenes must be an array")

    entries: list[tuple[float, float, str]] = []
    cursor = 0.0
    for scene in scenes:
        duration = float(scene.get("duration_seconds") or 0)
        narration = str(scene.get("narration") or "").strip()
        parts = chunks(narration, args.max_chars)
        if duration <= 0:
            continue
        if not parts:
            cursor += duration
            continue
        weights = [max(1, len(part)) for part in parts]
        total_weight = sum(weights)
        local = cursor
        for index, part in enumerate(parts):
            if index == len(parts) - 1:
                end = cursor + duration
            else:
                end = local + duration * (weights[index] / total_weight)
            entries.append((local, end, part))
            local = end
        cursor += duration

    lines: list[str] = []
    for index, (start, end, text) in enumerate(entries, start=1):
        lines.extend([str(index), f"{timestamp(start)} --> {timestamp(end)}", text, ""])

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} subtitle cue(s) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
