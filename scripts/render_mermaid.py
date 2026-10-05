#!/usr/bin/env python3
"""Render Mermaid source to SVG/PNG using mmdc or an npx fallback."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--theme", default="dark")
    parser.add_argument("--background", default="transparent")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    if not source.is_file():
        raise SystemExit(f"Mermaid input not found: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)

    mmdc = shutil.which("mmdc")
    if mmdc:
        command = [mmdc, "-i", str(source), "-o", str(output), "-t", args.theme, "-b", args.background]
    elif shutil.which("npx"):
        command = [
            "npx", "--yes", "@mermaid-js/mermaid-cli",
            "-i", str(source), "-o", str(output), "-t", args.theme, "-b", args.background,
        ]
    else:
        raise SystemExit("Neither mmdc nor npx is available. Install @mermaid-js/mermaid-cli first.")

    print("Command:", " ".join(command))
    if args.dry_run:
        return 0
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    print(f"Rendered Mermaid diagram to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
