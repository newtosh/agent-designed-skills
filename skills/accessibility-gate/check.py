#!/usr/bin/env python3
"""CLI: python3 check.py <file-or-'-' for stdin>

Exit 0 = no tripwire findings.
Exit 1 = at least one blocking pattern.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from accessibility_lib import analyze, report  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <file|->", file=sys.stderr)
        return 2
    src = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text()
    print(report(src))
    return 1 if analyze(src) else 0


if __name__ == "__main__":
    raise SystemExit(main())
