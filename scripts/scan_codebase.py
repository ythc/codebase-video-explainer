#!/usr/bin/env python3
"""Create a deterministic, secret-safe inventory of a software repository."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Iterable

DEFAULT_IGNORES = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".DS_Store",
    "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build",
    "out", "coverage", ".coverage", "target", "vendor", "Pods",
    ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".turbo", ".parcel-cache", ".cache",
    ".codebase-video",
}

SECRET_BASENAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "id_rsa", "id_ed25519", "credentials", "credentials.json",
}

SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff",
    ".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".mov", ".avi", ".webm",
    ".pdf", ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".exe", ".dll", ".so", ".dylib", ".class", ".jar", ".pyc", ".o",
    ".sqlite", ".sqlite3", ".db",
}

NOTABLE_NAMES = {
    "README.md", "README", "package.json", "pnpm-workspace.yaml", "yarn.lock",
    "pnpm-lock.yaml", "package-lock.json", "bun.lockb", "pyproject.toml",
    "requirements.txt", "Pipfile", "poetry.lock", "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum", "pom.xml", "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts", "Gemfile", "composer.json",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml",
    "compose.yaml", "wrangler.toml", "wrangler.json", "wrangler.jsonc",
    "vercel.json", "netlify.toml", "tsconfig.json", "vite.config.ts",
    "vite.config.js", "next.config.js", "next.config.mjs", "next.config.ts",
}

ENTRY_BASENAMES = {
    "main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py",
    "main.ts", "main.tsx", "main.js", "main.jsx", "index.ts", "index.tsx",
    "index.js", "index.jsx", "server.ts", "server.js", "app.ts", "app.js",
    "Program.cs", "Startup.cs", "main.go", "main.rs", "lib.rs",
}


def is_secret_path(path: Path) -> bool:
    name = path.name
    lower = name.lower()
    if name in SECRET_BASENAMES or lower.startswith(".env."):
        return True
    if path.suffix.lower() in SECRET_SUFFIXES:
        return True
    return False


def iter_files(root: Path, extra_ignores: set[str]) -> Iterable[Path]:
    ignore_names = DEFAULT_IGNORES | extra_ignores
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in ignore_names)
        current_path = Path(current)
        for filename in sorted(files):
            path = current_path / filename
            rel_parts = path.relative_to(root).parts
            if any(part in ignore_names for part in rel_parts[:-1]):
                continue
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--max-files", type=int, default=50000)
    parser.add_argument("--ignore", action="append", default=[], help="Additional directory basename to ignore")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Repository root does not exist or is not a directory: {root}")

    files = []
    extension_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    notable = []
    entry_candidates = []
    skipped_secret = []
    skipped_binary = 0
    truncated = False

    for idx, path in enumerate(iter_files(root, set(args.ignore))):
        if idx >= args.max_files:
            truncated = True
            break

        rel = path.relative_to(root).as_posix()
        top_level_counts[path.relative_to(root).parts[0]] += 1

        if is_secret_path(path):
            skipped_secret.append(rel)
            continue

        suffix = path.suffix.lower()
        if suffix in BINARY_SUFFIXES:
            skipped_binary += 1
            continue

        try:
            stat = path.stat()
        except OSError:
            continue

        item = {
            "path": rel,
            "size_bytes": stat.st_size,
            "extension": suffix or "[none]",
        }
        files.append(item)
        extension_counts[item["extension"]] += 1

        if path.name in NOTABLE_NAMES:
            notable.append(rel)
        if path.name in ENTRY_BASENAMES or rel.startswith(("src/main.", "src/index.", "app/")):
            entry_candidates.append(rel)

    result = {
        "root": str(root),
        "file_count": len(files),
        "truncated": truncated,
        "max_files": args.max_files,
        "ignored_directory_basenames": sorted(DEFAULT_IGNORES | set(args.ignore)),
        "skipped_binary_file_count": skipped_binary,
        "skipped_secret_paths": sorted(skipped_secret),
        "extension_counts": dict(extension_counts.most_common()),
        "top_level_file_counts": dict(top_level_counts.most_common()),
        "notable_files": sorted(set(notable)),
        "entrypoint_candidates": sorted(set(entry_candidates)),
        "files": files,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(files)} file records to {output}")
    if skipped_secret:
        print(f"Skipped {len(skipped_secret)} secret-like file(s)")
    if truncated:
        print(f"WARNING: file inventory truncated at {args.max_files} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
