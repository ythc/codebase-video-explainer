#!/usr/bin/env python3
"""Build a compact project manifest from common ecosystem metadata files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def read_text(path: Path, limit: int = 2_000_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def parse_json(path: Path) -> dict[str, Any] | None:
    text = read_text(path)
    if text is None:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def parse_package_json(path: Path) -> dict[str, Any] | None:
    data = parse_json(path)
    if not data:
        return None
    return {
        "path": path.name if path.parent == path.parent.parent else path.as_posix(),
        "name": data.get("name"),
        "private": data.get("private"),
        "type": data.get("type"),
        "package_manager": data.get("packageManager"),
        "scripts": data.get("scripts", {}),
        "dependencies": sorted((data.get("dependencies") or {}).keys()),
        "dev_dependencies": sorted((data.get("devDependencies") or {}).keys()),
        "workspaces": data.get("workspaces"),
        "main": data.get("main"),
        "module": data.get("module"),
        "bin": data.get("bin"),
    }


def parse_pyproject(path: Path) -> dict[str, Any]:
    text = read_text(path) or ""
    name = None
    m = re.search(r"(?ms)^\[project\].*?^name\s*=\s*[\"']([^\"']+)", text)
    if m:
        name = m.group(1)
    deps = []
    dep_block = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)\]", text)
    if dep_block:
        deps = re.findall(r"[\"']([^\"']+)[\"']", dep_block.group(1))
    tools = sorted(set(re.findall(r"(?m)^\[tool\.([A-Za-z0-9_.-]+)\]", text)))
    return {"path": path.name, "project_name": name, "dependencies_raw": deps, "tool_sections": tools}


def parse_go_mod(path: Path) -> dict[str, Any]:
    text = read_text(path) or ""
    module = None
    m = re.search(r"(?m)^module\s+(.+)$", text)
    if m:
        module = m.group(1).strip()
    requires = re.findall(r"(?m)^\s*([A-Za-z0-9_.~/-]+)\s+v[^\s]+", text)
    return {"path": path.name, "module": module, "requires": sorted(set(requires))}


def parse_cargo(path: Path) -> dict[str, Any]:
    text = read_text(path) or ""
    package_name = None
    m = re.search(r"(?ms)^\[package\].*?^name\s*=\s*[\"']([^\"']+)", text)
    if m:
        package_name = m.group(1)
    deps = []
    dep_block = re.search(r"(?ms)^\[dependencies\]\s*(.*?)(?:^\[|\Z)", text)
    if dep_block:
        deps = re.findall(r"(?m)^([A-Za-z0-9_-]+)\s*=", dep_block.group(1))
    return {"path": path.name, "package_name": package_name, "dependencies": sorted(set(deps))}


def detect_frameworks(package: dict[str, Any] | None) -> list[str]:
    if not package:
        return []
    names = set(package.get("dependencies", [])) | set(package.get("dev_dependencies", []))
    mapping = {
        "next": "Next.js", "react": "React", "vue": "Vue", "nuxt": "Nuxt",
        "svelte": "Svelte", "@sveltejs/kit": "SvelteKit", "express": "Express",
        "fastify": "Fastify", "hono": "Hono", "@remix-run/react": "Remix",
        "astro": "Astro", "remotion": "Remotion", "@remotion/cli": "Remotion",
        "wrangler": "Cloudflare Workers", "@cloudflare/workers-types": "Cloudflare Workers",
        "electron": "Electron", "vite": "Vite", "typescript": "TypeScript",
    }
    return sorted({label for pkg, label in mapping.items() if pkg in names})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--scan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    scan = json.loads(Path(args.scan).read_text(encoding="utf-8"))
    paths = {item["path"] for item in scan.get("files", [])}

    package = parse_package_json(root / "package.json") if "package.json" in paths else None
    pyproject = parse_pyproject(root / "pyproject.toml") if "pyproject.toml" in paths else None
    go_mod = parse_go_mod(root / "go.mod") if "go.mod" in paths else None
    cargo = parse_cargo(root / "Cargo.toml") if "Cargo.toml" in paths else None

    ecosystem = []
    if package:
        ecosystem.append("node")
    if pyproject or "requirements.txt" in paths:
        ecosystem.append("python")
    if go_mod:
        ecosystem.append("go")
    if cargo:
        ecosystem.append("rust")
    if "pom.xml" in paths or "build.gradle" in paths or "build.gradle.kts" in paths:
        ecosystem.append("jvm")

    package_manager = None
    for lock, manager in [
        ("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"), ("bun.lockb", "bun")
    ]:
        if lock in paths:
            package_manager = manager
            break
    if package and package.get("package_manager"):
        package_manager = package["package_manager"]

    deployment_hints = [p for p in sorted(paths) if Path(p).name in {
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
        "wrangler.toml", "wrangler.json", "wrangler.jsonc", "vercel.json", "netlify.toml"
    }]

    result = {
        "root": str(root),
        "ecosystems": ecosystem,
        "package_manager": package_manager,
        "framework_hints": detect_frameworks(package),
        "entrypoint_candidates": scan.get("entrypoint_candidates", []),
        "notable_files": scan.get("notable_files", []),
        "deployment_hints": deployment_hints,
        "node": package,
        "python": pyproject,
        "go": go_mod,
        "rust": cargo,
        "analysis_note": "This manifest is heuristic orientation data. Verify architecture and runtime behavior from source before narrating it as fact."
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote project manifest to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
