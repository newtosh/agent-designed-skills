---
name: design-decision-rubric
description: Force a fair design or UX decision into a written record with options, who is affected, when not to apply, and the tradeoff. Use before locking a visual, interaction, or information-architecture choice, and whenever a critique is about to become a vibe preference.
---

# Design decision rubric

A decision is fair when someone else can see what was given up and who
pays for it. This skill is that record. It does not pick a typeface or
restyle a page. Vendored craft skills do that work. This one stops a
preference from shipping unlabeled.

## When to use

- Two or more real options exist (layout, component, motion, copy,
  navigation, empty state).
- The choice helps one group and costs another (keyboard users, first-time
  users, dense-data users, people on small screens).
- A review comment is about to become "make it cleaner" with no cost named.

## When not to use

- The user already locked the decision. Implement it. Do not re-litigate.
- The change is a defect with one correct fix (broken focus trap, missing
  name, overlapping tap targets). Use `accessibility` or `accessibility-gate`.
- The task is pixel craft inside an accepted decision. Use `frontend-design`,
  `better-interface`, `beautiful-shadows`, or `emil-design-eng`.

## Write the record

Use these headings, in this order. Prose under each heading. Options are
a list of at least two `- ` items.

```markdown
## Decision
What is being chosen, in one or two sentences.

## Options
- A: what it is, and the concrete cost
- B: what it is, and the concrete cost

## Who is affected
Who is helped, who is excluded or slowed, and which constraint (input
method, viewport, vision, familiarity, time pressure) drives that.

## When not to apply
The situation where this recommendation is the wrong default.

## Tradeoff
The specific quality given up so another quality can win. Name both.

## Recommendation
The option to ship, and the one fact that made it win.
```

Rules while writing:

- At least two options. "Do the nice version" against a strawman is one
  option.
- "Who is affected" names people and a constraint. "Users" is not a person.
- "When not to apply" is a situation, not "use good judgment".
- The recommendation has to follow from the tradeoff. If it does not,
  change one of them.
- Do not use this record to smuggle in a visual style the brief did not ask
  for. Style belongs to the craft skills.

## Check it

```bash
python3 ~/.claude/skills/design-decision-rubric/check.py <file>
# or: python3 ~/.claude/skills/design-decision-rubric/check.py -
```

Exit 0 means every section is present, in that order, and Options has two
items. The
checker does not judge whether the tradeoff is honest. Read the record
again before treating exit 0 as agreement.
