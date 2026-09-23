---
name: accessibility-gate
description: Mechanical tripwire for a few accessibility defects that are almost always wrong (missing alt, unlabeled controls, nameless icon buttons, html without lang, outline removed with no focus-visible). Use before shipping HTML or CSS, and alongside the vendored accessibility skill for a real WCAG review.
---

# Accessibility gate

Stop the obvious misses. This is not a WCAG audit and a clean run is not
conformance. The vendored `accessibility` skill is the audit: POUR,
contrast, keyboard behavior, target size, and what automated tools cannot
see. Run that when the user asks whether something is accessible. Run this
gate whenever HTML or CSS is about to be written or published.

## What it flags

- `<img>` with no `alt` attribute. `alt=""` is allowed for a decorative image.
- `<input>` (except hidden, submit, button, reset, image), `<select>`, or
  `<textarea>` with no accessible name. A wrapping `<label>`, a matching
  `label for`, `aria-label`, or `aria-labelledby` counts. The gate does not
  check that the label text is meaningful.
- `<button>` or `role="button"` with no text and no accessible name.
- `<html>` without `lang`, only when an `<html>` tag is present. A component
  snippet is not a document.
- `outline: none` or `outline: 0` when the same snippet never mentions
  `:focus-visible`.

## What it does not flag

Contrast, reading order, focus traps, captions, target size, dragged
actions, and whether the accessible name is the right name. Those belong
to `accessibility`. Do not tell the user this gate passed WCAG.

## When not to apply

- Email or markdown with no HTML.
- A design critique that has no markup yet. Write the decision or the
  heuristic audit first.
- A third-party snippet the user said not to modify. Report the finding
  and stop.

## Check it

```bash
python3 ~/.claude/skills/accessibility-gate/check.py <file>
```

Exit 1 means fix the listed lines, then re-run. On publish-shaped tool
calls this also runs as `~/.claude/hooks/accessibility-gate.py` once that
hook is wired (see the pack README). The hook fails open: a crash in the
checker must not block an unrelated tool call.
