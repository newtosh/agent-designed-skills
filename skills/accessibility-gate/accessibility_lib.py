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
_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
_OUTLINE_REMOVED = re.compile(
    r"outline\s*:\s*(?:none|0+(?:\.0+)?"
    r"(?:px|pt|pc|in|cm|mm|em|rem|ex|ch|vw|vh|vmin|vmax|%)?)"
    r"(?![\w.])",
    re.IGNORECASE,
)
_FOCUS_VISIBLE = re.compile(r":focus-visible", re.IGNORECASE)
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LOCATOR_LIMIT = 80


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


@dataclass
class _ButtonFrame:
    attrs: dict[str, str]
    text: list[str]
    depth: int


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
        self._stack: list[str] = []
        self._open_buttons: list[_ButtonFrame] = []
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
            alt = attr.get("alt", "").strip()
            if alt:
                for frame in self._open_buttons:
                    frame.text.append(alt)
        if name in {"input", "select", "textarea"}:
            self.controls.append(_Control(name, attr, self._label_depth > 0))
        if name == "button" or attr.get("role", "").lower() == "button":
            text: list[str] = []
            if name == "img" and attr.get("alt", "").strip():
                text.append(attr["alt"].strip())
            self._open_buttons.append(_ButtonFrame(attr, text, len(self._stack)))
        if name not in _VOID_ELEMENTS:
            self._stack.append(name)
        style = attr.get("style", "")
        if style:
            self.style_chunks.append(style)

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name == "label" and self._label_depth:
            self._label_depth -= 1
        if name == "style":
            self._in_style = False
        if self._stack and self._stack[-1] == name:
            self._stack.pop()
            while self._open_buttons and self._open_buttons[-1].depth == len(
                self._stack
            ):
                frame = self._open_buttons.pop()
                self.buttons.append((frame.attrs, "".join(frame.text)))

    def flush_open_buttons(self) -> None:
        while self._open_buttons:
            frame = self._open_buttons.pop(0)
            self.buttons.append((frame.attrs, "".join(frame.text)))

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.style_chunks.append(data)
        for frame in self._open_buttons:
            frame.text.append(data)


def looks_like_markup(text: str) -> bool:
    return "<" in text or _OUTLINE_REMOVED.search(text) is not None


def _has_accessible_name(attrs: dict[str, str]) -> bool:
    if attrs.get("aria-label", "").strip():
        return True
    return bool(attrs.get("aria-labelledby", "").strip())


def _control_named(control: _Control, label_fors: set[str]) -> bool:
    if _has_accessible_name(control.attrs):
        return True
    if control.in_label:
        return True
    control_id = control.attrs.get("id", "").strip()
    return bool(control_id and control_id in label_fors)


def _locator(src: str) -> str:
    path = src.split("#", 1)[0].split("?", 1)[0]
    cleaned = "".join(
        char if char.isprintable() and char not in "\n\r\t" else " " for char in path
    )
    collapsed = " ".join(cleaned.split())
    if not collapsed:
        return "no src"
    return collapsed[:_LOCATOR_LIMIT]


def _outline_css(text: str, style_chunks: list[str]) -> str:
    css = "\n".join(style_chunks)
    if css:
        return css
    if _OUTLINE_REMOVED.search(text):
        return text
    return ""


def analyze(text: str) -> list[Finding]:
    scanner = _Scanner()
    scanner.feed(text)
    scanner.close()
    scanner.flush_open_buttons()
    findings: list[Finding] = []

    html_lang = (scanner.html_attrs or {}).get("lang", "").strip()
    if scanner.html_attrs is not None and not html_lang:
        findings.append(
            Finding("blocking", "html-lang", "<html> has no lang attribute")
        )

    for attrs in scanner.images:
        if "alt" not in attrs:
            findings.append(
                Finding(
                    "blocking",
                    "img-alt",
                    f"<img> missing alt ({_locator(attrs.get('src', ''))})",
                )
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

    css = _CSS_COMMENT.sub("", _outline_css(text, scanner.style_chunks))
    if _OUTLINE_REMOVED.search(css) and not _FOCUS_VISIBLE.search(css):
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
