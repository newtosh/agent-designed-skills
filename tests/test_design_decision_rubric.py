"""Tests for the design-decision record checker."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "design-decision-rubric"))

from rubric_lib import analyze  # noqa: E402

COMPLETE = """
## Decision
Use a single primary action on the review screen.

## Options
- A: one Publish button. Costs a second path for draft-only users.
- B: Publish and Save draft. Costs a quieter primary action.

## Who is affected
First-time authors on a phone, who need one obvious next step.
Returning editors, who already know they want a draft.

## When not to apply
A legal filing flow where saving a draft is the main task.

## Tradeoff
Draft speed is given up so the first publish is clear.

## Recommendation
Option A. The screen is the first publish, not the editor.
"""


class RubricTests(unittest.TestCase):
    def test_complete_record(self) -> None:
        self.assertEqual(analyze(COMPLETE), [])

    def test_missing_section(self) -> None:
        text = COMPLETE.replace(
            "## Tradeoff\nDraft speed is given up so the first publish is clear.\n\n",
            "",
        )
        codes = [finding.section for finding in analyze(text)]
        self.assertIn("Tradeoff", codes)

    def test_one_option_is_incomplete(self) -> None:
        text = COMPLETE.replace(
            "- B: Publish and Save draft. Costs a quieter primary action.\n",
            "",
        )
        codes = [finding.section for finding in analyze(text)]
        self.assertIn("Options", codes)

    def test_cli_exit_codes(self) -> None:
        script = ROOT / "skills" / "design-decision-rubric" / "check.py"
        ok = subprocess.run(
            [sys.executable, str(script), "-"],
            input=COMPLETE,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ok.returncode, 0, ok.stdout)
        bad = subprocess.run(
            [sys.executable, str(script), "-"],
            input="## Decision\nJust ship it.\n",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
