---
name: ux-heuristic-audit
description: Run a severity-rated UX heuristic audit (Nielsen H1-H10 plus three Krug checks) that requires evidence, a fix, and when not to apply. Use when reviewing a flow, screen, or component for usability, not for visual polish.
---

# UX heuristic audit

Score the interface against a fixed set of heuristics. A missing check is
not a pass. A finding without evidence is not a finding.

This is an original checklist for this pack. It is not the wondelai
`ux-heuristics` skill. Nielsen's ten names and Krug's three slogans are
the usual labels. The lines under them are operational rules for the
audit, written here.

Severity, same scale used in a classic heuristic review:

| Score | Meaning |
| --- | --- |
| 0 | Not a problem, or not present in this artifact |
| 1 | Cosmetic. Fix if you are already in the file |
| 2 | Minor. Slows some people, workaround exists |
| 3 | Major. A primary task fails or becomes guesswork |
| 4 | Catastrophe. Data loss, lock-out, or the task cannot be finished |

## Heuristics

- **H1 Visibility of system status.** After an action, the interface shows
  that it happened, within about a tenth of a second, in the same place
  the person acted.
- **H2 Match the real world.** Labels use the person's words for the job,
  not the system's internal names.
- **H3 User control and freedom.** A destructive or hard-to-reverse action
  has an undo, a back path, or an explicit confirm. Cancel does not save.
- **H4 Consistency and standards.** The same action keeps the same name and
  the same place across the flow.
- **H5 Error prevention.** Constraints stop the bad input before an error
  message has to explain it.
- **H6 Recognition rather than recall.** Choices are visible. The person
  does not have to remember a code, a mode, or a previous screen.
- **H7 Flexibility and efficiency.** A repeated task has a shorter path for
  someone who already knows the product. That path is not the only path.
- **H8 Aesthetic and minimalist design.** Every visible element earns its
  place against the current task. Decoration that competes with the action
  is a finding.
- **H9 Recover from errors.** The message says what went wrong and the next
  step, next to the field that failed. No apology in place of a cause.
- **H10 Help and documentation.** If the task is not self-evident, help is
  next to the step, searchable by the task name, and short.
- **K1 Don't make me think.** The next action on this screen is obvious
  without a tour.
- **K2 Omit needless words.** Instructional copy can lose half its words
  and still say the same thing. If it can, it should.
- **K3 Billboard test.** A first-time visitor can say what this screen is
  for after a quick look, without scrolling through a manifesto.

## When not to apply a heuristic

State the exception on the finding (`when_not`). Examples that are real
exceptions, not escapes:

- H7 does not apply to a one-time setup wizard.
- H10 does not apply when K1 is already true for every branch.
- H8 does not apply to a brand moment the brief asked to be expressive,
  unless the expression hides the action.
- K2 does not apply to legal or medical text that must stay complete.

## Report shape

The checker enforces this shape. It does not decide the scores.

```markdown
## Coverage
- H1: checked
- H2: not observed
- H3: checked
- H4: checked
- H5: checked
- H6: checked
- H7: not observed
- H8: checked
- H9: checked
- H10: not observed
- K1: checked
- K2: checked
- K3: checked

## Findings
- id: H4
  severity: 3
  evidence: The confirm button says "Submit" on the form and "Done" on the toast.
  fix: Use "Publish" on the button and "Published" on the toast.
  when_not: A multi-step wizard where the last step is explicitly "Submit application".
```

Coverage lists every id exactly once, as `checked` or `not observed`.
`not observed` means the artifact has no surface for that heuristic
(a static poster has no H3). It does not mean "I skipped it".

Each finding uses `id`, `severity`, `evidence`, `fix`, `when_not`.
Severity 1 or higher needs all three text fields. Evidence quotes the
screen or the file. The fix is a specific change. `when_not` is the case
where applying the fix would be wrong.

`## Findings` may be empty when every checked heuristic scores 0. Say so
in a sentence under the heading. Do not invent mild findings to look thorough.

## Check it

```bash
python3 ~/.claude/skills/ux-heuristic-audit/check.py <file>
```

Then fix the interface for severity 3 and 4 before polish. Severity 1 can
wait. Re-run after edits if the report changed.
