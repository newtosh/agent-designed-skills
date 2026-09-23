"""Guards on vendor-update.sh that do not need a network clone."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "vendor-update.sh"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class VendorUpdateTests(unittest.TestCase):
    def test_script_parses(self) -> None:
        parsed = subprocess.run(
            ["bash", "-n", str(SCRIPT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(parsed.returncode, 0, parsed.stderr)

    def test_skill_name_is_not_a_jq_program(self) -> None:
        result = _run(['foo"; .repo'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill name", result.stderr)
        self.assertNotIn("https://", result.stdout)

    def test_unknown_skill_exits_before_clone(self) -> None:
        result = _run(["not-a-skill"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown vendored skill", result.stderr)

    def test_untracked_file_exits_before_clone(self) -> None:
        extra = ROOT / ".vendor-update-untracked"
        extra.write_text("x")
        try:
            result = _run(["accessibility"])
        finally:
            extra.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not clean", result.stderr)

    def test_dirty_tree_exits_before_clone(self) -> None:
        readme = ROOT / "README.md"
        original = readme.read_text()
        remotes_before = subprocess.check_output(["git", "remote"], cwd=ROOT, text=True)
        readme.write_text(original + "\n")
        try:
            result = _run(["accessibility"])
        finally:
            readme.write_text(original)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not clean", result.stderr)
        remotes_after = subprocess.check_output(["git", "remote"], cwd=ROOT, text=True)
        self.assertEqual(remotes_before, remotes_after)


if __name__ == "__main__":
    unittest.main()
