#!/usr/bin/env python3
"""PreToolUse hook: block markup that fails the accessibility tripwire.

Reads the Claude Code hook JSON on stdin, pulls string values out of
tool_input, and blocks (exit 2) when accessibility-gate finds a blocking
pattern. Fails open on any error so this hook is never the reason a real
send or publish breaks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root / "skills" / "accessibility-gate"))

MIN_LEN = 20


def collect_strings(obj: object, out: list[str]) -> None:
    if isinstance(obj, str):
        if len(obj) >= MIN_LEN and "<" in obj:
            out.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            collect_strings(value, out)
    elif isinstance(obj, list):
        for value in obj:
            collect_strings(value, out)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        from accessibility_lib import analyze  # noqa: E402

        strings: list[str] = []
        collect_strings(payload.get("tool_input", {}), strings)
        findings = analyze("\n".join(strings))
        if findings:
            lines = [
                "accessibility-gate: blocking pattern in outgoing markup. Fix it first."
            ]
            for finding in findings[:20]:
                lines.append(f"  [{finding.code}] {finding.detail}")
            print("\n".join(lines), file=sys.stderr)
            return 2
        return 0
    except Exception as exc:  # fail open
        print(f"accessibility-gate: skipped ({exc})", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
