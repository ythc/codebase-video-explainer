#!/usr/bin/env python3
"""Check that narration, subtitles, and optional video end on the same timeline."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

TIMECODE = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")


def require_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise SystemExit("ffprobe is required for sync verification")
    return path


def duration(path: Path) -> float:
    ffprobe = require_ffprobe()
    output = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(output)


def parse_timecode(value: str) -> float:
    match = TIMECODE.fullmatch(value.strip())
    if not match:
        raise ValueError(value)
    hours, minutes, seconds, millis = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def last_subtitle_end(path: Path) -> float:
    last = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if " --> " not in line:
            continue
        _, end = line.split(" --> ", 1)
        last = parse_timecode(end)
    if last is None:
        raise SystemExit(f"No subtitle cues found: {path}")
    return last


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--subtitles", required=True)
    parser.add_argument("--video")
    parser.add_argument(
        "--subtitle-tail-tolerance",
        type=float,
        default=1.5,
        help="Maximum allowed gap between final spoken subtitle and audio end",
    )
    parser.add_argument(
        "--video-tolerance",
        type=float,
        default=0.35,
        help="Maximum allowed absolute duration difference between video and audio",
    )
    args = parser.parse_args()

    audio = Path(args.audio).resolve()
    subtitles = Path(args.subtitles).resolve()
    audio_duration = duration(audio)
    subtitle_end = last_subtitle_end(subtitles)
    subtitle_gap = audio_duration - subtitle_end

    print(f"audio_seconds={audio_duration:.3f}")
    print(f"last_subtitle_end_seconds={subtitle_end:.3f}")
    print(f"subtitle_tail_gap_seconds={subtitle_gap:.3f}")

    errors = []
    if subtitle_gap < -0.10 or subtitle_gap > args.subtitle_tail_tolerance:
        errors.append(
            f"subtitle tail differs from audio end by {subtitle_gap:.3f}s "
            f"(allowed: -0.100..{args.subtitle_tail_tolerance:.3f}s)"
        )

    if args.video:
        video_duration = duration(Path(args.video).resolve())
        delta = video_duration - audio_duration
        print(f"video_seconds={video_duration:.3f}")
        print(f"video_audio_delta_seconds={delta:.3f}")
        if abs(delta) > args.video_tolerance:
            errors.append(
                f"video/audio duration mismatch {delta:.3f}s exceeds "
                f"{args.video_tolerance:.3f}s"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("A/V sync checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
