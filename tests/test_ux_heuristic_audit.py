"""Tests for the heuristic audit report checker."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "ux-heuristic-audit"))

from audit_lib import HEURISTIC_IDS, analyze  # noqa: E402


def coverage(status: str = "checked") -> str:
    lines = ["## Coverage"]
    lines.extend(f"- {hid}: {status}" for hid in HEURISTIC_IDS)
    return "\n".join(lines)


FINDING = """
## Findings
- id: H4
  severity: 3
  evidence: The button says Submit and the toast says Done.
  fix: Use Publish on the button and Published on the toast.
  when_not: A filing flow whose last step is legally named Submit.
"""


class AuditTests(unittest.TestCase):
    def test_complete_report(self) -> None:
        self.assertEqual(analyze(coverage() + "\n" + FINDING), [])

    def test_missing_coverage_id(self) -> None:
        text = coverage().replace("- H7: checked\n", "")
        details = [finding.detail for finding in analyze(text + "\n## Findings\n")]
        self.assertTrue(any("H7" in detail for detail in details))

    def test_severity_needs_when_not(self) -> None:
        broken = FINDING.replace(
            "  when_not: A filing flow whose last step is legally named Submit.\n",
            "",
        )
        codes = [finding.detail for finding in analyze(coverage() + "\n" + broken)]
        self.assertTrue(any("when_not" in detail for detail in codes))

    def test_not_observed_conflicts_with_finding(self) -> None:
        text = coverage("not observed") + "\n" + FINDING
        details = [finding.detail for finding in analyze(text)]
        self.assertTrue(any("not observed" in detail for detail in details))

    def test_bad_severity(self) -> None:
        text = coverage() + "\n" + FINDING.replace("severity: 3", "severity: 9")
        details = [finding.detail for finding in analyze(text)]
        self.assertTrue(any("0-4" in detail for detail in details))


if __name__ == "__main__":
    unittest.main()
