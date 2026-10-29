"""End-to-end validation and unit tests for AV-Scrub-Index payloads and scripts."""

from __future__ import annotations

import copy
import glob
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "data" / "schema" / "uninstaller.schema.json"
VENDORS_DIR = REPO_ROOT / "data" / "vendors"
DIST_DIR = REPO_ROOT / "dist"
README_PATH = REPO_ROOT / "README.md"


def _load_script_module(name: str, filename: str):
    script_path = REPO_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_mod = _load_script_module("validate_schema", "validate-schema.py")
compile_mod = _load_script_module("compile_dist", "compile-dist.py")
readme_mod = _load_script_module("generate_readme", "generate-readme.py")
links_mod = _load_script_module("check_links", "check-links.py")


class TestPayloadsAndSchema(unittest.TestCase):
    def setUp(self) -> None:
        self.vendor_files = [
            Path(p) for p in sorted(glob.glob(str(VENDORS_DIR / "*.json")))
        ]
        self.assertGreater(len(self.vendor_files), 0, "Expected vendor JSON files")
        with self.vendor_files[0].open("r", encoding="utf-8") as handle:
            self.sample_entry = json.load(handle)

    def test_all_vendor_payloads_pass_schema(self) -> None:
        errors = validate_mod.validate_entries(SCHEMA_PATH, self.vendor_files)
        self.assertEqual(errors, [], f"Schema validation errors: {errors}")

    def test_rejects_invalid_id_pattern(self) -> None:
        bad = copy.deepcopy(self.sample_entry)
        bad["id"] = "Invalid_ID!"
        self._assert_invalid(bad)

    def test_rejects_invalid_tier(self) -> None:
        bad = copy.deepcopy(self.sample_entry)
        bad["tier"] = "prosumer"
        self._assert_invalid(bad)

    def test_rejects_invalid_download_url(self) -> None:
        bad = copy.deepcopy(self.sample_entry)
        bad["download_url"] = "ftp://invalid.example.com/tool.exe"
        self._assert_invalid(bad)

    def test_rejects_invalid_sha256_and_accepts_valid(self) -> None:
        bad = copy.deepcopy(self.sample_entry)
        bad["expected_sha256"] = "not-a-sha256"
        self._assert_invalid(bad)

        good = copy.deepcopy(self.sample_entry)
        good["expected_sha256"] = hashlib.sha256(b"av-scrub-index").hexdigest()
        self._assert_valid(good)

    def test_rejects_missing_execution_fields_and_unknown_properties(self) -> None:
        bad_exec = copy.deepcopy(self.sample_entry)
        del bad_exec["execution"]["requires_safe_mode"]
        self._assert_invalid(bad_exec)

        unknown_prop = copy.deepcopy(self.sample_entry)
        unknown_prop["unexpected_field"] = True
        self._assert_invalid(unknown_prop)

    def test_rejects_duplicate_ids_across_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p1 = Path(tmp) / "one.json"
            p2 = Path(tmp) / "two.json"
            entry_two = copy.deepcopy(self.sample_entry)
            entry_two["download_url"] = "https://example.com/other.exe"
            p1.write_text(json.dumps(self.sample_entry), encoding="utf-8")
            p2.write_text(json.dumps(entry_two), encoding="utf-8")
            errors = validate_mod.validate_entries(SCHEMA_PATH, [p1, p2])
            self.assertTrue(any("duplicate id" in err for err in errors))

    def _assert_invalid(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "candidate.json"
            target.write_text(json.dumps(payload), encoding="utf-8")
            errors = validate_mod.validate_entries(SCHEMA_PATH, [target])
            self.assertGreater(len(errors), 0, f"Expected errors for {payload}")

    def _assert_valid(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "candidate.json"
            target.write_text(json.dumps(payload), encoding="utf-8")
            errors = validate_mod.validate_entries(SCHEMA_PATH, [target])
            self.assertEqual(errors, [])


class TestDistAndReadmeSync(unittest.TestCase):
    def test_dist_bundles_in_sync_with_vendors(self) -> None:
        expected = compile_mod.load_vendor_entries()
        index_path = DIST_DIR / "index.json"
        min_path = DIST_DIR / "index.min.json"
        self.assertTrue(index_path.is_file(), "dist/index.json missing")
        self.assertTrue(min_path.is_file(), "dist/index.min.json missing")

        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        min_data = json.loads(min_path.read_text(encoding="utf-8"))
        self.assertEqual(index_data, expected)
        self.assertEqual(min_data, expected)
        self.assertNotIn("\n", min_path.read_text(encoding="utf-8").strip())

    def test_readme_in_sync_with_generator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_readme = Path(tmp) / "README.md"
            rendered = readme_mod.render_readme(readme_path=temp_readme)
            current = README_PATH.read_text(encoding="utf-8")
            self.assertEqual(current, rendered, "README.md is out of sync with vendor data")
            self.assertNotIn("{table_rows}", current)
            for item in compile_mod.load_vendor_entries():
                self.assertIn(item["download_url"], current)
                self.assertIn(item["tool_name"], current)


class TestLinkChecker(unittest.TestCase):
    def test_head_200_succeeds(self) -> None:
        mock_resp = MagicMock(status_code=200)
        with patch.object(links_mod.requests, "head", return_value=mock_resp) as head_mock:
            res = links_mod.probe_url(
                {"id": "t", "vendor": "V", "tool_name": "T", "download_url": "https://example.com/a.exe"}
            )
            head_mock.assert_called_once()
            self.assertTrue(res["ok"])
            self.assertEqual(res["status_code"], 200)

    def test_head_405_falls_back_to_streaming_get(self) -> None:
        head_resp = MagicMock(status_code=405)
        get_resp = MagicMock(status_code=200)
        get_resp.__enter__.return_value = get_resp
        get_resp.__exit__.return_value = False

        with (
            patch.object(links_mod.requests, "head", return_value=head_resp),
            patch.object(links_mod.requests, "get", return_value=get_resp) as get_mock,
        ):
            res = links_mod.probe_url(
                {"id": "t", "vendor": "V", "tool_name": "T", "download_url": "https://example.com/a.exe"}
            )
            get_mock.assert_called_once()
            self.assertTrue(res["ok"])
            self.assertEqual(res["status_code"], 200)

    def test_head_404_fails(self) -> None:
        head_resp = MagicMock(status_code=404)
        with patch.object(links_mod.requests, "head", return_value=head_resp):
            res = links_mod.probe_url(
                {"id": "t", "vendor": "V", "tool_name": "T", "download_url": "https://example.com/dead.exe"}
            )
            self.assertFalse(res["ok"])
            self.assertEqual(res["status_code"], 404)

    def test_sha256_verification_and_drift_detection(self) -> None:
        body = b"binary-payload-bytes"
        good_hash = hashlib.sha256(body).hexdigest()

        def make_stream_resp():
            resp = MagicMock(status_code=200)
            resp.iter_content.return_value = [body]
            resp.__enter__.return_value = resp
            resp.__exit__.return_value = False
            return resp

        with patch.object(links_mod.requests, "get", side_effect=lambda *a, **kw: make_stream_resp()):
            ok_res = links_mod.probe_url(
                {
                    "id": "t",
                    "vendor": "V",
                    "tool_name": "T",
                    "download_url": "https://example.com/a.exe",
                    "expected_sha256": good_hash,
                }
            )
            self.assertTrue(ok_res["ok"])
            self.assertFalse(ok_res["hash_drift"])
            self.assertEqual(ok_res["actual_sha256"], good_hash)

            drift_res = links_mod.probe_url(
                {
                    "id": "t",
                    "vendor": "V",
                    "tool_name": "T",
                    "download_url": "https://example.com/a.exe",
                    "expected_sha256": "0" * 64,
                }
            )
            self.assertFalse(drift_res["ok"])
            self.assertTrue(drift_res["hash_drift"])
            self.assertIn("SHA-256 drift", drift_res["error"])

    def test_changed_only_noop_when_no_files_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            with patch.object(links_mod, "resolve_changed_vendor_files", return_value=[]):
                rc = links_mod.main(["--changed-only", "--output", str(report_path)])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
