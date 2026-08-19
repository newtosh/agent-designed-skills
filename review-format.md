# Review output format

This is the format for a review `better-interface` orchestrates. A domain skill reporting on its own carries its own smaller format, in its `## Reporting` section.

## Scope and coverage

State the mode, exact scope, stack and styling conventions, the project convention documents found in recon, and any review boundary. Then show coverage:

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | Files, components, states, or checks | Findings count or `Clear` |

Include every domain listed under `better-interface`'s **Use domain skills as the sources of truth**. `Clear` means inspected with no actionable finding; `Not reviewed` must explain why.

## Findings

One table, ordered by severity, then by reach:

| # | Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | HIGH | Accessibility | `src/Dialog.tsx:42` | `<button><XIcon /></button>` | Add `aria-label="Close"` and hide the icon from the accessibility tree | The icon-only control has no accessible name |

- **Severity** comes from `better-interface`'s **Rank by user impact**.
- **Location** cites `path/to/file:line`. Cite the exact screen and component when the artifact has no source files.
- **Before / After** show the current implementation and an actionable replacement. Never split them into separate "Before:" and "After:" lines.
- **Why** names the violated principle and its user impact.
- **Domain** is the owning skill without the `better-` prefix.

Each row is one root cause. Consolidate a repeated systemic issue into one row and list every affected location. Respect the mode's finding cap. With no findings, omit the table and state "No actionable interface findings."

## Considered but rejected

Include 1–3 candidates in `quick` mode and 2–5 in `full` mode:

| Location | Candidate | Rejected because |
| --- | --- | --- |
| `src/Card.tsx:28` | Increase the shadow | Existing depth matches the shared surface token; changing one card would reduce consistency |

These are real candidates inspected during the review, not invented filler. If the scope genuinely contains fewer borderline candidates, include the ones that exist and say so.

## Verification

List each check or interaction, the exact command or steps, and the observed result. Separate checks that passed from checks marked **Not verified**.

## Verdict

End with exactly one:

- `Block`: one or more `HIGH` findings remain.
- `Needs changes`: only `MEDIUM` or `LOW` findings remain.
- `Approve`: no actionable findings remain and the claimed coverage was verified.

## Change-scoped reviews

When `interface-review` resolved the scope from version control, the format above applies with these four additions.

1. **Scope block.** Open **Scope and Coverage** with the change scope table `interface-review` produced, then the coverage table above unchanged. A domain with no evidence in the change scope is `Not reviewed: no evidence in the change scope`, which is a coverage statement, not a gap.
2. **Status column.** The findings table gains a `Status` column after `Domain`, carrying `Introduced` or `Regression`:

   | # | Severity | Domain | Status | Location | Before | After | Why |
   | --- | --- | --- | --- | --- | --- | --- | --- |
   | 1 | HIGH | Accessibility | Regression | `src/Dialog.tsx:42` | `aria-label="Close"` removed in this change | Restore `aria-label="Close"` on the icon-only control | The close control had an accessible name before this change and no longer does |

   With no `Introduced` or `Regression` findings, omit the table and state "No actionable interface findings in this change."

3. **Pre-existing section.** Place it after **Considered but Rejected**, at most three, highest severity first, stated plainly as not this change's responsibility. Omit when there are none.

   | Severity | Domain | Location | Issue |
   | --- | --- | --- | --- |
   | MEDIUM | Typography | `src/Toolbar.tsx:7` | Numeric badges use proportional figures; predates this change |

4. **Cap and verdict.** Both cover `Introduced` and `Regression` only. `Pre-existing` findings sit outside the cap, so touching a legacy file cannot turn into a full-file audit. They sit outside the verdict too, so a change whose only findings are pre-existing is an `Approve`.
