#!/usr/bin/env python3
"""
Smoke tests for the CLI tools.

These guard against the class of failure where a tool crashes before doing any
work (import errors, argparse conflicts, missing dependencies) — bugs that the
ontology-data tests can never catch because they don't execute the tools.
"""

import py_compile
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Tools that expose an argparse CLI: `--help` must exit 0 and print usage.
CLI_TOOLS = [
    PROJECT_ROOT / "tools" / "sync_formats.py",
    PROJECT_ROOT / "tools" / "monitor_aws_changes.py",
    PROJECT_ROOT / "tools" / "import_to_arangodb.py",
    PROJECT_ROOT / "automation" / "schedule_monitoring.py",
]

# Every Python module in these directories must at least byte-compile.
MODULE_DIRS = ["tools", "utils", "automation", "tests"]


class TestCLISmoke(unittest.TestCase):
    """Every CLI tool must start up and answer --help."""

    def run_help(self, script: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=60,
        )

    def test_cli_tools_answer_help(self):
        for script in CLI_TOOLS:
            with self.subTest(tool=script.name):
                self.assertTrue(script.exists(), f"{script} does not exist")
                result = self.run_help(script)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{script.name} --help exited {result.returncode}:\n{result.stderr}",
                )
                self.assertIn("usage", result.stdout.lower())

    def test_sync_check_passes(self):
        """The shipped TTL and OWL serializations must be in sync."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tools" / "sync_formats.py"), "check"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, f"sync check failed:\n{result.stdout}")


class TestProposalFileName(unittest.TestCase):
    """The monitor's proposal file is unique per GitHub Actions run (two runs a day must not clash)."""

    def write(self, run_number):
        import os
        import tempfile
        from unittest import mock

        from tools.propose_ontology_updates import write_proposal

        finding = {
            "service_name": "Example",
            "rationale": "r",
            "source_link": "https://example.com",
            "candidate_classes": [],
            "candidate_properties": [],
            "example_arn_format": None,
        }
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_RUN_NUMBER"}
        if run_number:
            env["GITHUB_RUN_NUMBER"] = run_number
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, env, clear=True):
            return write_proposal([finding], Path(tmp)).name

    def test_name_includes_run_number_in_actions(self):
        self.assertRegex(self.write("57"), r"^\d{4}-\d{2}-\d{2}-run57-monitor-findings\.md$")

    def test_name_is_date_only_locally(self):
        self.assertRegex(self.write(None), r"^\d{4}-\d{2}-\d{2}-monitor-findings\.md$")


class TestModulesCompile(unittest.TestCase):
    """Every module must byte-compile (catches syntax errors in rarely-run paths)."""

    def test_all_modules_compile(self):
        for dirname in MODULE_DIRS:
            for module in sorted((PROJECT_ROOT / dirname).glob("*.py")):
                with self.subTest(module=f"{dirname}/{module.name}"):
                    py_compile.compile(str(module), doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
