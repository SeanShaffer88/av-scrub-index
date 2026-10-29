#!/usr/bin/env python3
"""Render root README.md directly from data/vendors/*.json."""

from __future__ import annotations

import glob
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDORS_GLOB = str(REPO_ROOT / "data" / "vendors" / "*.json")
README_PATH = REPO_ROOT / "README.md"

TEMPLATE = """<!-- AUTO-GENERATED FILE: Do not edit README.md directly. Run `python scripts/generate-readme.py` -->
# AV-Scrub-Index

An automated, machine-readable dataset of official uninstallation and scrub utilities for Antivirus and Endpoint Security products.

> **Direct Data Endpoint:** [`dist/index.json`](dist/index.json) | [`dist/index.min.json`](dist/index.min.json) | **Schema:** [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json)

## Removal Tools Directory

| Vendor | Tool Name | Tier | Download URL | Safe Mode? | Silent / Force Args | Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
{table_rows}

## Automation & Consumption

```powershell
# PowerShell Quick-Fetch Example
$tools = Invoke-RestMethod -Uri "https://raw.githubusercontent.com/SeanShaffer88/av-scrub-index/main/dist/index.json"
$avast = $tools | Where-Object { $_.id -eq "avast-clear" }
Start-BitsTransfer -Source $avast.download_url -Destination "$env:TEMP\\avastclear.exe"
```

## Contributing & Local Validation

Vendor records live in [`data/vendors/`](data/vendors/) (one JSON file per vendor) and are validated against [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json).

```bash
# Validate all vendor entries against the JSON Schema
python scripts/validate-schema.py

# Probe vendor download endpoints
python scripts/check-links.py --all --output report.json

# Rebuild dist/index.json, dist/index.min.json, and README.md
python scripts/compile-dist.py
python scripts/generate-readme.py
```
"""


def _escape_md_cell(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip()


def _format_cli_args(exec_cfg: dict[str, Any]) -> str:
    silent = exec_cfg.get("silent_flags")
    force = exec_cfg.get("force_flags")
    if silent and force and silent != force:
        return f"`{_escape_md_cell(silent)}` / `{_escape_md_cell(force)}`"
    chosen = silent or force
    if chosen:
        return f"`{_escape_md_cell(chosen)}`"
    return "`None`"


def render_readme(
    vendors_glob: str = VENDORS_GLOB, readme_path: Path = README_PATH
) -> str:
    files = sorted(glob.glob(vendors_glob))
    items: list[dict[str, Any]] = []
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as handle:
            items.append(json.load(handle))

    items.sort(key=lambda item: (item["vendor"].lower(), item["id"]))

    rows: list[str] = []
    for item in items:
        exec_cfg = item["execution"]
        vendor = _escape_md_cell(item["vendor"])
        tool_name = _escape_md_cell(item["tool_name"])
        docs_url = item.get("official_docs_url")
        tool_cell = f"[{tool_name}]({docs_url})" if docs_url else tool_name
        tier = _escape_md_cell(item["tier"])
        download_url = item["download_url"]
        safe_mode = "Yes" if exec_cfg["requires_safe_mode"] else "No"
        cli_args = _format_cli_args(exec_cfg)
        notes = _escape_md_cell(item.get("notes", ""))
        rows.append(
            f"| **{vendor}** | {tool_cell} | `{tier}` | [Download]({download_url}) | {safe_mode} | {cli_args} | {notes} |"
        )

    output = TEMPLATE.replace("{table_rows}", "\n".join(rows))
    readme_path.write_text(output, encoding="utf-8")
    print("[*] README.md compiled successfully.")
    return output


def main() -> int:
    render_readme()
    return 0


if __name__ == "__main__":
    sys.exit(main())
