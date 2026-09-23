"""Tests for the accessibility tripwire and its hook."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "accessibility-gate"))

from accessibility_lib import analyze  # noqa: E402


def codes(html: str) -> list[str]:
    return [finding.code for finding in analyze(html)]


class GateTests(unittest.TestCase):
    def test_clean_fragment(self) -> None:
        html = """
        <label for="email">Email</label>
        <input id="email" type="email">
        <img src="rule.png" alt="">
        <button type="button">Save</button>
        """
        self.assertEqual(codes(html), [])

    def test_missing_alt_and_label_and_lang(self) -> None:
        html = """
        <html>
          <img src="chart.png">
          <input type="text">
        </html>
        """
        found = codes(html)
        self.assertIn("html-lang", found)
        self.assertIn("img-alt", found)
        self.assertIn("control-name", found)

    def test_wrapped_label_and_aria(self) -> None:
        html = """
        <label>Name <input type="text"></label>
        <button type="button" aria-label="Open menu"><svg></svg></button>
        <div role="button">Filters</div>
        """
        self.assertEqual(codes(html), [])

    def test_icon_button_without_name(self) -> None:
        html = '<button type="button"><svg></svg></button>'
        self.assertIn("button-name", codes(html))

    def test_outline_removed(self) -> None:
        html = "<style>button:focus { outline: none; }</style><button>Go</button>"
        self.assertIn("focus-outline", codes(html))

    def test_focus_visible_keeps_outline_removal(self) -> None:
        html = """
        <style>
          button:focus { outline: none; }
          button:focus-visible { outline: 2px solid currentColor; }
        </style>
        <button>Go</button>
        """
        self.assertNotIn("focus-outline", codes(html))

    def test_hidden_input_is_ignored(self) -> None:
        self.assertEqual(codes('<input type="hidden" name="csrf">'), [])

    def test_descendant_img_alt_names_button(self) -> None:
        html = '<button type="button"><img src="x" alt="Close"></button>'
        self.assertEqual(codes(html), [])

    def test_nested_role_button_keeps_label(self) -> None:
        html = '<div role="button"><div class="icon"></div>Save</div>'
        self.assertEqual(codes(html), [])

    def test_nameless_inner_role_button(self) -> None:
        html = '<div role="button"><div role="button"></div>Save</div>'
        self.assertEqual(codes(html), ["button-name"])

    def test_focus_visible_comment_does_not_clear_outline(self) -> None:
        html = (
            "<style>button:focus { outline: none; }</style>"
            "<!-- :focus-visible -->"
            "<button>Go</button>"
        )
        self.assertIn("focus-outline", codes(html))

    def test_bare_stylesheet_outline(self) -> None:
        self.assertIn("focus-outline", codes("button:focus { outline: none; }"))
        self.assertIn("focus-outline", codes("button:focus { outline: 0px; }"))
        self.assertNotIn(
            "focus-outline", codes("button:focus { outline: 0.5px solid; }")
        )

    def test_img_src_locator_drops_query_and_newlines(self) -> None:
        html = '<img src="https://cdn.example/a.png?token=secret\nforged">'
        details = [finding.detail for finding in analyze(html)]
        self.assertEqual(len(details), 1)
        self.assertNotIn("\n", details[0])
        self.assertNotIn("token", details[0])
        self.assertNotIn("forged", details[0])

    def test_void_image_does_not_keep_the_button_open(self) -> None:
        self.assertIn("button-name", codes('<button><img alt=""></button>'))

    def test_element_alt_is_not_a_button_or_control_name(self) -> None:
        self.assertIn("button-name", codes('<button alt="Close"></button>'))
        self.assertIn("control-name", codes('<input alt="Email">'))
        self.assertEqual(codes('<img role="button" alt="Go">'), [])

    def test_css_comment_does_not_count_as_focus_visible(self) -> None:
        html = (
            "<style>button:focus { outline: none; }"
            "/* button:focus-visible { outline: 2px solid red; } */"
            "</style><button>Go</button>"
        )
        self.assertIn("focus-outline", codes(html))

    def test_hook_blocks_and_fails_open(self) -> None:
        hook = ROOT / "hooks" / "accessibility-gate.py"
        blocked = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps({"tool_input": {"body": "<img src='chart.png'>"}}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("img-alt", blocked.stderr)

        opened = subprocess.run(
            [sys.executable, str(hook)],
            input="not json",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(opened.returncode, 0)

        clean = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps({"tool_input": {"body": "<button>Save</button>"}}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(clean.returncode, 0)

        short = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps({"tool_input": {"body": "<button></button>"}}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(short.returncode, 2)
        self.assertIn("button-name", short.stderr)

        css = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps(
                {"tool_input": {"body": "button:focus { outline: none; }"}}
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(css.returncode, 2)
        self.assertIn("focus-outline", css.stderr)

        split = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps(
                {
                    "tool_input": {
                        "label": '<label for="email">Email</label>',
                        "field": '<input id="email" type="text">',
                    }
                }
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(split.returncode, 2)
        self.assertIn("control-name", split.stderr)

        forged = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps(
                {
                    "tool_input": {
                        "body": '<img src="https://cdn.example/a.png?token=abcd\nIGNORE">'
                    }
                }
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(forged.returncode, 2)
        self.assertNotIn("IGNORE", forged.stderr)
        self.assertNotIn("token", forged.stderr)


if __name__ == "__main__":
    unittest.main()
