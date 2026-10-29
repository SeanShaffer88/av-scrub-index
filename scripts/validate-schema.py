#!/usr/bin/env python3
"""Validate all vendor JSON files against data/schema/uninstaller.schema.json."""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = REPO_ROOT / "data" / "schema" / "uninstaller.schema.json"
DEFAULT_VENDORS_GLOB = str(REPO_ROOT / "data" / "vendors" / "*.json")


def build_format_checker() -> FormatChecker:
    checker = FormatChecker()

    @checker.checks("uri")
    def check_uri(value: object) -> bool:
        if not isinstance(value, str):
            return True
        if any(ch.isspace() for ch in value):
            return False
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    return checker


def validate_entries(schema_path: Path, vendor_files: list[Path]) -> list[str]:
    errors: list[str] = []

    if not schema_path.is_file():
        return [f"Schema file not found: {schema_path}"]

    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in schema {schema_path}: {exc}"]

    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=build_format_checker())

    if not vendor_files:
        return ["No vendor JSON files found to validate."]

    seen_ids: dict[str, Path] = {}
    seen_urls: dict[str, Path] = {}

    for file_path in sorted(vendor_files):
        rel = os.path.relpath(file_path, REPO_ROOT)
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: malformed JSON ({exc})")
            continue

        for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
            loc = ".".join(str(p) for p in err.path) or "<root>"
            errors.append(f"{rel} [{loc}]: {err.message}")

        if isinstance(payload, dict):
            entry_id = payload.get("id")
            if isinstance(entry_id, str):
                if entry_id in seen_ids:
                    prev_rel = os.path.relpath(seen_ids[entry_id], REPO_ROOT)
                    errors.append(
                        f"{rel}: duplicate id '{entry_id}' (already defined in {prev_rel})"
                    )
                else:
                    seen_ids[entry_id] = file_path

            download_url = payload.get("download_url")
            if isinstance(download_url, str):
                if download_url in seen_urls:
                    prev_rel = os.path.relpath(seen_urls[download_url], REPO_ROOT)
                    errors.append(
                        f"{rel}: duplicate download_url '{download_url}' (already defined in {prev_rel})"
                    )
                else:
                    seen_urls[download_url] = file_path

    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate AV-Scrub-Index vendor JSON records against the JSON schema."
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to JSON Schema file (default: data/schema/uninstaller.schema.json)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional explicit vendor JSON files to validate (defaults to data/vendors/*.json)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    vendor_files = (
        [p.resolve() for p in args.files]
        if args.files
        else [Path(p).resolve() for p in sorted(glob.glob(DEFAULT_VENDORS_GLOB))]
    )

    errors = validate_entries(args.schema.resolve(), vendor_files)
    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        print(
            f"[FAILED] Validation failed with {len(errors)} error(s).",
            file=sys.stderr,
        )
        return 1

    print(f"[SUCCESS] Validated {len(vendor_files)} vendor file(s) against schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
