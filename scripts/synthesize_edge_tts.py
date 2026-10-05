#!/usr/bin/env python3
"""Generate natural Edge TTS narration and exact SentenceBoundary subtitles.

Two modes are supported:

1. Storyboard mode (preferred for final videos): synthesize each scene as one
   continuous utterance, derive SRT cues from Edge TTS SentenceBoundary events,
   normalize scene audio, concatenate it, and emit a timed storyboard.
2. Single-file mode (backward compatible): synthesize one narration text file.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

MARKDOWN = re.compile(r"(^|\n)#{1,6}\s+|[`*_>#-]+")
TICKS_PER_SECOND = 10_000_000


def clean_markdown(text: str) -> str:
    text = MARKDOWN.sub(" ", text)
    return " ".join(text.split())


def require_command(name: str) -> str:
    value = shutil.which(name)
    if not value:
        raise SystemExit(f"Required command is missing: {name}")
    return value


def ffprobe_duration(path: Path) -> float:
    require_command("ffprobe")
    output = subprocess.check_output(
        [
            "ffprobe",
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


def srt_timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


async def import_edge_tts():
    try:
        import edge_tts  # type: ignore
    except ImportError as exc:
        raise SystemExit("edge-tts is not installed. Run: pip install edge-tts") from exc
    return edge_tts


async def synthesize_single(
    text: str,
    output: Path,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
) -> None:
    edge_tts = await import_edge_tts()
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await communicate.save(str(output))


async def synthesize_scene(
    text: str,
    audio_output: Path,
    metadata_output: Path,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
) -> None:
    edge_tts = await import_edge_tts()
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
        boundary="SentenceBoundary",
    )
    with audio_output.open("wb") as audio, metadata_output.open("w", encoding="utf-8") as metadata:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                metadata.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def normalize_to_wav(source: Path, destination: Path) -> None:
    require_command("ffmpeg")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(destination),
        ],
        check=True,
    )


def append_wav(target: wave.Wave_write, source: Path) -> None:
    with wave.open(str(source), "rb") as handle:
        if handle.getnchannels() != 2 or handle.getsampwidth() != 2 or handle.getframerate() != 48000:
            raise SystemExit(f"Unexpected WAV format after normalization: {source}")
        target.writeframes(handle.readframes(handle.getnframes()))


def write_silence(target: wave.Wave_write, seconds: float) -> None:
    frames = max(0, round(seconds * 48000))
    target.writeframes(b"\x00\x00\x00\x00" * frames)


def encode_mp3(source_wav: Path, destination_mp3: Path) -> None:
    require_command("ffmpeg")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_wav),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            str(destination_mp3),
        ],
        check=True,
    )


def read_storyboard(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid storyboard JSON: {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
        raise SystemExit("Storyboard must contain a top-level scenes array")
    if not data["scenes"]:
        raise SystemExit("Storyboard contains no scenes")
    for index, scene in enumerate(data["scenes"]):
        if not isinstance(scene, dict):
            raise SystemExit(f"Scene {index} is not an object")
        narration = clean_markdown(str(scene.get("narration", "")))
        if not narration:
            raise SystemExit(f"Scene {index} has empty narration")
    return data


async def storyboard_mode(args: argparse.Namespace) -> int:
    storyboard_path = Path(args.storyboard).resolve()
    output_dir = Path(args.output_dir).resolve()
    storyboard = read_storyboard(storyboard_path)

    print(
        f"Scenes: {len(storyboard['scenes'])}; voice: {args.voice}; rate: {args.rate}; "
        f"pitch: {args.pitch}; gap: {args.scene_gap}s"
    )
    if args.dry_run:
        return 0

    require_command("ffmpeg")
    require_command("ffprobe")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "tts-raw"
    metadata_dir = output_dir / "tts-metadata"
    scene_dir = output_dir / "tts-scenes"
    raw_dir.mkdir(exist_ok=True)
    metadata_dir.mkdir(exist_ok=True)
    scene_dir.mkdir(exist_ok=True)

    for index, scene in enumerate(storyboard["scenes"]):
        text = clean_markdown(str(scene["narration"]))
        raw = raw_dir / f"{index:02d}.mp3"
        meta = metadata_dir / f"{index:02d}.jsonl"
        print(f"Synthesizing scene {index}: {scene.get('title', scene.get('id', 'untitled'))}")
        await synthesize_scene(
            text,
            raw,
            meta,
            args.voice,
            args.rate,
            args.pitch,
            args.volume,
        )
        normalize_to_wav(raw, scene_dir / f"{index:02d}.wav")

    cursor = 0.0
    cue_number = 1
    srt_lines: list[str] = []
    timings: list[dict[str, Any]] = []
    timed_storyboard = copy.deepcopy(storyboard)
    scene_count = len(storyboard["scenes"])

    narration_wav = output_dir / "narration.wav"
    with wave.open(str(narration_wav), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(48000)

        for index, scene in enumerate(storyboard["scenes"]):
            wav_path = scene_dir / f"{index:02d}.wav"
            meta_path = metadata_dir / f"{index:02d}.jsonl"
            audio_duration = ffprobe_duration(wav_path)
            scene_start = cursor
            scene_end = scene_start + audio_duration

            rows = [
                json.loads(line)
                for line in meta_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if not rows:
                rows = [
                    {
                        "offset": 0,
                        "duration": int(audio_duration * TICKS_PER_SECOND),
                        "text": clean_markdown(str(scene["narration"])),
                    }
                ]

            for row in rows:
                local_start = float(row.get("offset", 0)) / TICKS_PER_SECOND
                local_end = (
                    float(row.get("offset", 0)) + float(row.get("duration", 0))
                ) / TICKS_PER_SECOND
                start = scene_start + local_start
                end = min(scene_end, scene_start + local_end)
                text = str(row.get("text", "")).strip()
                if not text or end <= start:
                    continue
                srt_lines.extend(
                    [
                        str(cue_number),
                        f"{srt_timestamp(start)} --> {srt_timestamp(end)}",
                        text,
                        "",
                    ]
                )
                cue_number += 1

            gap_after = args.scene_gap if index < scene_count - 1 else 0.0
            timed_storyboard["scenes"][index]["duration_seconds"] = round(
                audio_duration + gap_after, 3
            )
            timed_storyboard["scenes"][index]["tts_start_seconds"] = round(scene_start, 3)
            timed_storyboard["scenes"][index]["tts_end_seconds"] = round(scene_end, 3)

            timings.append(
                {
                    "index": index,
                    "id": scene.get("id", str(index)),
                    "title": scene.get("title", ""),
                    "start_seconds": round(scene_start, 3),
                    "speech_duration_seconds": round(audio_duration, 3),
                    "gap_after_seconds": round(gap_after, 3),
                    "end_seconds": round(scene_end + gap_after, 3),
                }
            )

            append_wav(target, wav_path)
            if gap_after:
                write_silence(target, gap_after)
            cursor = scene_end + gap_after

    timed_storyboard["target_duration_seconds"] = round(cursor, 3)

    (output_dir / "subtitles.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    (output_dir / "timings.json").write_text(
        json.dumps(
            {
                "voice": args.voice,
                "rate": args.rate,
                "pitch": args.pitch,
                "volume": args.volume,
                "scene_gap_seconds": args.scene_gap,
                "total_seconds": round(cursor, 3),
                "scenes": timings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "storyboard.timed.json").write_text(
        json.dumps(timed_storyboard, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    encode_mp3(narration_wav, output_dir / "narration.mp3")

    print(f"Wrote narration: {output_dir / 'narration.mp3'}")
    print(f"Wrote exact subtitles: {output_dir / 'subtitles.srt'}")
    print(f"Wrote timed storyboard: {output_dir / 'storyboard.timed.json'}")
    print(f"Total duration: {cursor:.3f}s")
    return 0


async def single_file_mode(args: argparse.Namespace) -> int:
    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    text = clean_markdown(source.read_text(encoding="utf-8"))
    if not text:
        raise SystemExit("Narration input is empty after Markdown cleanup")
    print(f"Voice: {args.voice}; characters: {len(text)}; output: {output}")
    if args.dry_run:
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    await synthesize_single(text, output, args.voice, args.rate, args.pitch, args.volume)
    print(f"Wrote narration audio to {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--storyboard", help="Storyboard JSON for exact multi-scene narration")
    mode.add_argument("--input", help="Single narration text/Markdown file")
    parser.add_argument("--output", help="Single-file mode output audio path")
    parser.add_argument(
        "--output-dir",
        help="Storyboard mode output directory; defaults to the storyboard directory",
    )
    parser.add_argument("--voice", default="zh-CN-YunyangNeural")
    parser.add_argument("--rate", default="-5%")
    parser.add_argument("--pitch", default="-2Hz")
    parser.add_argument("--volume", default="+0%")
    parser.add_argument("--scene-gap", type=float, default=0.7)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.scene_gap < 0:
        parser.error("--scene-gap must be >= 0")

    if args.storyboard:
        storyboard = Path(args.storyboard).resolve()
        args.output_dir = str(Path(args.output_dir).resolve()) if args.output_dir else str(storyboard.parent)
        return asyncio.run(storyboard_mode(args))

    if not args.output:
        parser.error("--output is required with --input")
    return asyncio.run(single_file_mode(args))


if __name__ == "__main__":
    raise SystemExit(main())
