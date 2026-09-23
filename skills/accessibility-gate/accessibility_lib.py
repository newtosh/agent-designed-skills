"""Flag a few accessibility defects that are almost always wrong.

Stdlib only. This is a tripwire, not a WCAG audit. The vendored
`accessibility` skill owns guidelines, contrast ratios, and manual
checks. Use that skill to decide. Use this module to stop the obvious
misses before they ship.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser

_SKIP_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
_OUTLINE_REMOVED = re.compile(r"outline\s*:\s*(?:none|0)\b", re.IGNORECASE)
_FOCUS_VISIBLE = re.compile(r":focus-visible", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    detail: str


@dataclass
class _Control:
    tag: str
    attrs: dict[str, str]
    in_label: bool


class _Scanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.controls: list[_Control] = []
        self.label_fors: set[str] = set()
        self.buttons: list[tuple[dict[str, str], str]] = []
        self.images: list[dict[str, str]] = []
        self.html_attrs: dict[str, str] | None = None
        self.style_chunks: list[str] = []
        self._label_depth = 0
        self._button_tags: list[str] = []
        self._button_attrs: dict[str, str] | None = None
        self._button_text: list[str] = []
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs)
        self.handle_endtag(tag)

    def _start(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): (value or "") for key, value in attrs}
        name = tag.lower()
        if name == "html" and self.html_attrs is None:
            self.html_attrs = attr
        if name == "label":
            self._label_depth += 1
            labelled_by = attr.get("for", "").strip()
            if labelled_by:
                self.label_fors.add(labelled_by)
        if name == "style":
            self._in_style = True
        if name == "img":
            self.images.append(attr)
        if name in {"input", "select", "textarea"}:
            self.controls.append(_Control(name, attr, self._label_depth > 0))
        if name == "button" or attr.get("role", "").lower() == "button":
            if not self._button_tags:
                self._button_attrs = attr
                self._button_text = []
            self._button_tags.append(name)
        style = attr.get("style", "")
        if style:
            self.style_chunks.append(style)

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name == "label" and self._label_depth:
            self._label_depth -= 1
        if name == "style":
            self._in_style = False
        if self._button_tags and self._button_tags[-1] == name:
            self._button_tags.pop()
            if not self._button_tags and self._button_attrs is not None:
                self.buttons.append((self._button_attrs, "".join(self._button_text)))
                self._button_attrs = None
                self._button_text = []

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.style_chunks.append(data)
        if self._button_tags:
            self._button_text.append(data)


def _has_accessible_name(attrs: dict[str, str]) -> bool:
    if attrs.get("aria-label", "").strip():
        return True
    if attrs.get("aria-labelledby", "").strip():
        return True
    if attrs.get("alt", "").strip():
        return True
    return False


def _control_named(control: _Control, label_fors: set[str]) -> bool:
    if _has_accessible_name(control.attrs):
        return True
    if control.in_label:
        return True
    control_id = control.attrs.get("id", "").strip()
    return bool(control_id and control_id in label_fors)


def analyze(text: str) -> list[Finding]:
    scanner = _Scanner()
    scanner.feed(text)
    scanner.close()
    findings: list[Finding] = []

    html_lang = (scanner.html_attrs or {}).get("lang", "").strip()
    if scanner.html_attrs is not None and not html_lang:
        findings.append(
            Finding("blocking", "html-lang", "<html> has no lang attribute")
        )

    for attrs in scanner.images:
        if "alt" not in attrs:
            src = attrs.get("src", "")
            findings.append(
                Finding("blocking", "img-alt", f"<img> missing alt ({src or 'no src'})")
            )

    for control in scanner.controls:
        if control.tag == "input":
            input_type = control.attrs.get("type", "text").lower()
            if input_type in _SKIP_INPUT_TYPES:
                continue
        if _control_named(control, scanner.label_fors):
            continue
        findings.append(
            Finding(
                "blocking",
                "control-name",
                f"<{control.tag}> has no label, aria-label, or aria-labelledby",
            )
        )

    for attrs, button_text in scanner.buttons:
        if button_text.strip() or _has_accessible_name(attrs):
            continue
        findings.append(
            Finding(
                "blocking",
                "button-name",
                "<button> (or role=button) has no accessible name",
            )
        )

    css = "\n".join(scanner.style_chunks)
    if _OUTLINE_REMOVED.search(css) and not _FOCUS_VISIBLE.search(text):
        findings.append(
            Finding(
                "blocking",
                "focus-outline",
                "outline is removed and :focus-visible is not set in this snippet",
            )
        )
    return findings


def report(text: str) -> str:
    findings = analyze(text)
    if not findings:
        return "No accessibility-gate findings."
    lines = [f"Accessibility gate: {len(findings)} finding(s)", ""]
    for finding in findings:
        lines.append(f"  [{finding.severity}] {finding.code}: {finding.detail}")
    return "\n".join(lines)
