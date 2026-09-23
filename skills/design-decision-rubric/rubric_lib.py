"""Check that a design decision record names the tradeoff.

Stdlib only. The model still makes the call. This module only checks
that the record has the sections a fair decision needs, so a vibe
preference cannot ship as if it were a reasoned choice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Decision",
    "Options",
    "Who is affected",
    "When not to apply",
    "Tradeoff",
    "Recommendation",
)

_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_OPTION = re.compile(r"(?m)^-\s+\S")
_FENCE = re.compile(r"```.*?```", re.DOTALL)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Finding:
    section: str
    detail: str


def _visible(text: str) -> str:
    text = _FENCE.sub("", text)
    return _COMMENT.sub("", text)


def _sections(text: str) -> tuple[dict[str, str], list[str]]:
    matches = list(_HEADING.finditer(text))
    found: dict[str, str] = {}
    duplicates: list[str] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if title in found:
            duplicates.append(title)
            continue
        found[title] = body
    return found, duplicates


def analyze(text: str) -> list[Finding]:
    sections, duplicates = _sections(_visible(text))
    findings: list[Finding] = []
    for title in duplicates:
        if title in REQUIRED_SECTIONS:
            findings.append(Finding(title, "duplicate heading"))
    present = [title for title in sections if title in REQUIRED_SECTIONS]
    expected = [title for title in REQUIRED_SECTIONS if title in present]
    if present != expected:
        findings.append(Finding("Order", "required headings are out of order"))
    for title in REQUIRED_SECTIONS:
        body = sections.get(title, "")
        if not body:
            findings.append(Finding(title, "missing or empty"))
    options = sections.get("Options", "")
    if options and len(_OPTION.findall(options)) < 2:
        findings.append(Finding("Options", "need at least two '- ' options"))
    return findings


def report(text: str) -> str:
    findings = analyze(text)
    if not findings:
        return "Design decision record is complete."
    lines = [f"Incomplete design decision ({len(findings)}):", ""]
    for finding in findings:
        lines.append(f"  [{finding.section}] {finding.detail}")
    return "\n".join(lines)
