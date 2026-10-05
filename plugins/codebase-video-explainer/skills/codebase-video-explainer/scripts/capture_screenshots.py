#!/usr/bin/env python3
"""Capture planned web UI screenshots with Playwright when available."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def load_plan(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("shots"), list):
        raise SystemExit("Screenshot plan must be an object with a shots array")
    return data


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"Only http/https screenshot targets are allowed: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--validate-plan", action="store_true")
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    base_url = str(plan.get("base_url") or "")
    output_dir = Path(args.output_dir).resolve()

    normalized = []
    for index, shot in enumerate(plan["shots"]):
        if not isinstance(shot, dict):
            raise SystemExit(f"Shot {index} must be an object")
        raw_url = str(shot.get("url") or shot.get("path") or "")
        if not raw_url:
            raise SystemExit(f"Shot {index} is missing url/path")
        url = raw_url if raw_url.startswith(("http://", "https://")) else urljoin(base_url.rstrip("/") + "/", raw_url.lstrip("/"))
        validate_url(url)
        name = SAFE_NAME.sub("-", str(shot.get("name") or f"shot-{index + 1}")).strip("-") or f"shot-{index + 1}"
        normalized.append((name, url, shot))

    if args.validate_plan:
        print(f"Validated {len(normalized)} screenshot target(s)")
        for name, url, _ in normalized:
            print(f"  {name}: {url}")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for name, url, shot in normalized:
            viewport = shot.get("viewport") or {}
            if viewport:
                page.set_viewport_size({"width": int(viewport.get("width", 1440)), "height": int(viewport.get("height", 900))})
            page.goto(url, wait_until=str(shot.get("wait_until") or "networkidle"), timeout=int(shot.get("timeout_ms") or 30000))
            selector = shot.get("wait_for_selector")
            if selector:
                page.wait_for_selector(str(selector), timeout=int(shot.get("timeout_ms") or 30000))
            wait_for_ms = int(shot.get("wait_for_ms") or 0)
            if wait_for_ms > 0:
                page.wait_for_timeout(wait_for_ms)
            output = output_dir / f"{name}.png"
            page.screenshot(path=str(output), full_page=bool(shot.get("full_page", True)))
            print(f"Captured {output}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
