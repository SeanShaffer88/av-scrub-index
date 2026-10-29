#!/usr/bin/env python3
"""Compile data/vendors/*.json into dist/index.json and dist/index.min.json."""

from __future__ import annotations

import glob
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDORS_GLOB = str(REPO_ROOT / "data" / "vendors" / "*.json")
DIST_DIR = REPO_ROOT / "dist"


def load_vendor_entries(vendors_glob: str = VENDORS_GLOB) -> list[dict[str, Any]]:
    files = sorted(glob.glob(vendors_glob))
    entries: list[dict[str, Any]] = []
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as handle:
            entries.append(json.load(handle))
    entries.sort(key=lambda item: (item["vendor"].lower(), item["id"]))
    return entries


def compile_dist(
    vendors_glob: str = VENDORS_GLOB, dist_dir: Path = DIST_DIR
) -> tuple[Path, Path]:
    entries = load_vendor_entries(vendors_glob)
    dist_dir.mkdir(parents=True, exist_ok=True)

    index_path = dist_dir / "index.json"
    min_path = dist_dir / "index.min.json"

    with index_path.open("w", encoding="utf-8") as out:
        json.dump(entries, out, indent=2, ensure_ascii=False)
        out.write("\n")

    with min_path.open("w", encoding="utf-8") as out:
        json.dump(entries, out, separators=(",", ":"), ensure_ascii=False)

    print(
        f"[*] Compiled {len(entries)} vendor entries into "
        f"{index_path.relative_to(REPO_ROOT) if index_path.is_relative_to(REPO_ROOT) else index_path} "
        f"and {min_path.relative_to(REPO_ROOT) if min_path.is_relative_to(REPO_ROOT) else min_path}."
    )
    return index_path, min_path


def main() -> int:
    compile_dist()
    return 0


if __name__ == "__main__":
    sys.exit(main())
