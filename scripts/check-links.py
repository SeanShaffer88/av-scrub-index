#!/usr/bin/env python3
"""Parallel HTTP HEAD/GET endpoint health & SHA-256 drift checker."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import glob
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENDORS_GLOB = str(REPO_ROOT / "data" / "vendors" / "*.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


def probe_url(entry: dict[str, Any], timeout: int = 12) -> dict[str, Any]:
    distribution = entry.get("distribution", "public")
    portal_gated = distribution == "portal_gated"
    url = entry.get("official_docs_url") if portal_gated else entry.get("download_url")
    expected_sha256 = None if portal_gated else entry.get("expected_sha256")
    result: dict[str, Any] = {
        "id": entry.get("id"),
        "vendor": entry.get("vendor"),
        "tool_name": entry.get("tool_name"),
        "distribution": distribution,
        "file": entry.get("_file"),
        "url": url,
        "ok": False,
        "status_code": None,
        "expected_sha256": expected_sha256,
        "actual_sha256": None,
        "hash_drift": False,
        "error": None,
    }

    if not url:
        result["error"] = (
            "Missing official_docs_url" if portal_gated else "Missing download_url"
        )
        return result

    def _status_acceptable(code: int) -> bool:
        if 200 <= code < 400:
            return True
        # Authenticated enterprise portals or WAF-protected KB pages may return 401/403
        if portal_gated and code in (401, 403):
            return True
        return False

    try:
        if expected_sha256:
            with requests.get(
                url,
                headers=HEADERS,
                stream=True,
                allow_redirects=True,
                timeout=timeout,
            ) as resp:
                result["status_code"] = resp.status_code
                if not (200 <= resp.status_code < 400):
                    result["ok"] = False
                    return result

                hasher = hashlib.sha256()
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        hasher.update(chunk)

                actual = hasher.hexdigest().lower()
                expected = expected_sha256.lower()
                result["actual_sha256"] = actual
                if actual != expected:
                    result["hash_drift"] = True
                    result["ok"] = False
                    result["error"] = (
                        f"SHA-256 drift detected (expected {expected[:12]}..., got {actual[:12]}...)"
                    )
                else:
                    result["ok"] = True
        else:
            # First attempt HTTP HEAD; fall back to streaming GET for CDNs that reject HEAD
            head_ok = False
            try:
                resp = requests.head(
                    url, headers=HEADERS, allow_redirects=True, timeout=timeout
                )
                result["status_code"] = resp.status_code
                head_ok = _status_acceptable(resp.status_code)
                resp.close()
            except requests.RequestException:
                head_ok = False

            if head_ok:
                result["ok"] = True
            else:
                with requests.get(
                    url,
                    headers=HEADERS,
                    stream=True,
                    allow_redirects=True,
                    timeout=timeout,
                ) as get_resp:
                    result["status_code"] = get_resp.status_code
                    result["ok"] = _status_acceptable(get_resp.status_code)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)

    return result


def resolve_changed_vendor_files() -> list[Path]:
    """Identify added or modified data/vendors/*.json files in git."""
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        proc = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=ACMR",
                f"origin/{base_ref}...HEAD",
                "--",
                "data/vendors/",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return sorted(
                {
                    (REPO_ROOT / line.strip()).resolve()
                    for line in proc.stdout.splitlines()
                    if line.strip().endswith(".json")
                    and (REPO_ROOT / line.strip()).is_file()
                }
            )

    working_tree: set[Path] = set()
    for cmd in (
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD", "--", "data/vendors/"],
        ["git", "ls-files", "--others", "--exclude-standard", "--", "data/vendors/"],
    ):
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.splitlines():
                rel = line.strip()
                if rel.endswith(".json") and (REPO_ROOT / rel).is_file():
                    working_tree.add((REPO_ROOT / rel).resolve())

    if working_tree:
        return sorted(working_tree)

    proc = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            "HEAD~1...HEAD",
            "--",
            "data/vendors/",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return sorted(
            {
                (REPO_ROOT / line.strip()).resolve()
                for line in proc.stdout.splitlines()
                if line.strip().endswith(".json")
                and (REPO_ROOT / line.strip()).is_file()
            }
        )

    return []


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check reachability and optional SHA-256 integrity of vendor download URLs."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--all",
        action="store_true",
        help="Probe all vendor entries in data/vendors/*.json (default).",
    )
    mode.add_argument(
        "--changed-only",
        action="store_true",
        help="Probe only vendor JSON files added or modified in the current PR/commit.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report.json"),
        help="Output path for JSON probe report (default: report.json).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=12,
        help="HTTP request timeout in seconds (default: 12).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Max concurrent probe threads (default: 8).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.changed_only:
        files = resolve_changed_vendor_files()
        if not files:
            print("[*] No changed vendor entries detected; skipping endpoint probes.")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as out:
                json.dump([], out, indent=2)
            return 0
    else:
        files = [Path(p).resolve() for p in sorted(glob.glob(DEFAULT_VENDORS_GLOB))]

    entries: list[dict[str, Any]] = []
    for file_path in files:
        with file_path.open("r", encoding="utf-8") as handle:
            entry = json.load(handle)
            entry["_file"] = os.path.relpath(file_path, REPO_ROOT)
            entries.append(entry)

    print(f"[*] Probing {len(entries)} vendor endpoint(s)...")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(
            executor.map(lambda item: probe_url(item, timeout=args.timeout), entries)
        )

    failures = [r for r in results if not r["ok"]]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        json.dump(results, out, indent=2)

    in_gha = os.environ.get("GITHUB_ACTIONS") == "true"
    for fail in failures:
        msg = (
            f"{fail['vendor']} - {fail['tool_name']}: "
            f"{fail['url']} (Status: {fail['status_code']} | Err: {fail['error']})"
        )
        print(f"[ERROR] {msg}")
        if in_gha:
            file_part = f"file={fail['file']}," if fail.get("file") else ""
            print(f"::error {file_part}title=Broken Endpoint URL::{msg}")

    if failures:
        return 1

    print("[SUCCESS] All endpoints reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
