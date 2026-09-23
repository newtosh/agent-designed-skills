"""Validate a severity-rated heuristic audit report.

Stdlib only. Heuristic names are the standard Nielsen and Krug labels.
The judgment stays with the model. This module checks that every id was
accounted for and that a real finding carries evidence, a fix, and a
case where it should not be applied.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

HEURISTIC_IDS: tuple[str, ...] = (
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "H7",
    "H8",
    "H9",
    "H10",
    "K1",
    "K2",
    "K3",
)

_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_COVERAGE = re.compile(r"(?m)^-\s+(H\d+|K\d+)\s*:\s*(checked|not observed)\s*$")
_FIELD = re.compile(r"(?m)^-\s+id:\s*(\S+)\s*$")
_KV = re.compile(r"(?m)^\s{2}(severity|evidence|fix|when_not):\s*(.*?)\s*$")


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str


def _section(text: str, title: str) -> str:
    matches = list(_HEADING.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip() != title:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return ""


def _findings_block(body: str) -> list[dict[str, str]]:
    starts = list(_FIELD.finditer(body))
    rows: list[dict[str, str]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(body)
        chunk = body[match.start() : end]
        row: dict[str, str] = {"id": match.group(1)}
        for key, value in _KV.findall(chunk):
            row[key] = value.strip()
        rows.append(row)
    return rows


def analyze(text: str) -> list[Finding]:
    findings: list[Finding] = []
    coverage_body = _section(text, "Coverage")
    if not coverage_body:
        findings.append(Finding("Coverage", "missing or empty"))
        covered: dict[str, str] = {}
    else:
        covered: dict[str, str] = {}
        for hid, status in _COVERAGE.findall(coverage_body):
            if hid in covered:
                findings.append(Finding("Coverage", f"duplicate coverage {hid}"))
                continue
            covered[hid] = status
        for hid in HEURISTIC_IDS:
            if hid not in covered:
                findings.append(Finding("Coverage", f"{hid} missing"))
        unknown = sorted(set(covered) - set(HEURISTIC_IDS))
        for hid in unknown:
            findings.append(Finding("Coverage", f"unknown id {hid}"))

    rows = _findings_block(_section(text, "Findings"))
    seen: set[str] = set()
    for row in rows:
        hid = row.get("id", "")
        if hid not in HEURISTIC_IDS:
            findings.append(Finding(hid or "?", "unknown finding id"))
            continue
        if hid in seen:
            findings.append(Finding(hid, "duplicate finding"))
        seen.add(hid)
        if covered.get(hid) == "not observed":
            findings.append(Finding(hid, "not observed, but a finding is present"))
        severity_raw = row.get("severity", "")
        if not severity_raw.isdigit() or not 0 <= int(severity_raw) <= 4:
            findings.append(Finding(hid, "severity must be an integer 0-4"))
            severity = -1
        else:
            severity = int(severity_raw)
        if severity >= 1:
            for key in ("evidence", "fix", "when_not"):
                if not row.get(key, "").strip():
                    findings.append(Finding(hid, f"severity {severity} needs {key}"))
    return findings


def report(text: str) -> str:
    findings = analyze(text)
    if not findings:
        return "Heuristic audit report is complete."
    lines = [f"Heuristic audit report incomplete ({len(findings)}):", ""]
    for finding in findings:
        lines.append(f"  [{finding.code}] {finding.detail}")
    return "\n".join(lines)
