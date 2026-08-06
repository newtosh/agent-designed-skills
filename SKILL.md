---
name: better-interface
description: >-
  User-invoked, cross-discipline interface review that coordinates better-accessibility, better-layout, better-writing, better-typography, better-colors, and better-ui. Use when explicitly invoked for a holistic review of a screen, flow, feature, or product interface. Supports quick and full review modes. Triggers on better-interface, full interface review, holistic UI audit, cross-discipline design review, review the whole interface.
---

# Review the interface as one system

A strong interface is not six independent audits stapled together. Review the whole experience, let each `better-*` skill own its domain rules, then consolidate the evidence into one prioritized verdict.

This skill owns orchestration only. Accessibility rules belong to `better-accessibility`; structure to `better-layout`; copy to `better-writing`; type to `better-typography`; color to `better-colors`; visual polish and motion to `better-ui`. Never duplicate or override their rules here. Change-scoped review — uncommitted work, branches, and pull requests — belongs to `interface-review`, which resolves the scope and classifies findings before handing the review back here.

## Core Principles

### 1. Resolve Scope and Mode First

Parse the invocation as `[quick|full] [scope]`. The first token is a mode only when it is exactly `quick` or `full`; anything else is part of the scope. Mode defaults to `full`.

Infer the screen, flow, feature, or repository scope from the request and current workspace. State the resolved scope in the output.

| Mode | Coverage | Finding cap |
| --- | --- | --- |
| `quick` | Primary user path and highest-traffic states; report only `HIGH` and `MEDIUM` issues | 5 |
| `full` | Entire requested scope across all six domain skills, including empty, loading, error, and narrow-width states when present | 15 |

If the requested scope is too large to inspect credibly, narrow it to the highest-traffic complete flow and state the boundary. Never imply uninspected surfaces were reviewed.

When the request names a branch, pull request, commit range, or uncommitted changes, hand scope resolution to `interface-review`. It returns the resolved change scope, the affected surfaces, and a status for each finding; severity, consolidation, the cap, the output format, and the verdict stay here, under **Change-Scoped Reviews** below.

### 2. Recon Before Judgment

Identify the framework, styling system, component library, design tokens, supported viewports, and available preview or test commands. Write every proposed fix in the project's own idiom — its Tailwind, plain CSS, or CSS-in-JS, its tokens, its component patterns — so a finding never arrives as a request to adopt a different stack. That governs the form of the fix, not whether the current implementation is good enough.

Then find what the project has already written down about its own interface: `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `AGENTS.md`, `CLAUDE.md`, a design-system or component-guidelines doc, Storybook docs pages, and any ADR covering the interface. Name in the output which of these you found, or state that the project documents none.

Read them for context and leverage, not for permission. They tell you what is deliberate, what vocabulary to use, and where a fix belongs — but a documented convention is not evidence that the convention is good, and "it's in the style guide" does not retire a finding. The point of the review is to make the interface better, including where the project has written the weaker choice down.

What they change is **where** you report, not **whether**. When a documented convention or a shared token is the cause, report it once against that source instead of once per component: the finding is the ramp, the scale, or the guideline, and the components are its locations. That is the highest-leverage fix available and it is the reason to read these files at all.

### 3. Use Domain Skills as the Sources of Truth

Before reviewing, confirm that all six owning skills below are available. Load and apply every available owner. In `quick` mode, inspect all six domains but spend depth only where the primary flow has evidence. In `full` mode, complete each available domain review before consolidation.

Review in this order so foundational failures are not hidden by polish:

1. `better-accessibility`
2. `better-layout`
3. `better-writing`
4. `better-typography`
5. `better-colors`
6. `better-ui`

This skill owns the final response. When a domain skill is loaded through `better-interface`, apply its principles and references but ignore its standalone **Review Output Format**. Use the consolidated format, shared severity, and finding cap in this file instead.

If an owning skill is unavailable, mark that domain `Not reviewed`, name the missing skill, and continue with the remaining domains. Do not recreate its rules from memory, substitute a neighboring skill, or claim holistic coverage.

When two skills appear to cover the same issue, assign it to the skill that owns the underlying rule and mention secondary effects in the **Why** cell. Report it once.

### 4. Require Evidence

Every finding cites `path/to/file:line` and shows the current implementation. If the review artifact has no source files, cite the exact screen and component. Do not report a code-level finding from visual appearance alone or a visual finding from source code alone when runtime behavior determines the result.

### 5. Rank by User Impact

Use one shared severity scale:

- `HIGH`: blocks a task, misleads the user, hides content or controls, causes data-loss risk, or creates a repeated systemic failure.
- `MEDIUM`: meaningfully harms comprehension, efficiency, adaptability, or consistency.
- `LOW`: isolated polish with limited task impact. Include only in `full` mode.

Within a severity, rank by reach and leverage. A token or shared-component fix outranks the same symptom in one leaf component.

**Escalation triggers.** Once the owning skill confirms one of these, it is `HIGH` on sight. Do not deliberate, do not average it down because the surface is minor, and do not hold it back in `quick` mode:

- An interactive control with no accessible name.
- A keyboard-reachable control with no visible focus indicator.
- A control or path reachable by pointer but not by keyboard.
- Motion or auto-playing content that ignores `prefers-reduced-motion`.
- Content or a control clipped, overlapped, or unreachable at 320px width or 200% zoom.
- Body or control text whose rendered contrast pair fails its required ratio.
- State or meaning carried by color alone.
- A destructive action with no confirmation, undo, or distinct treatment.

Triggers rank above every other finding, so when more of them fire than the mode's cap allows, list them first and state how many further findings the cap excluded. A cap may shorten the report; it may never be the reason a blocker went unreported.

These name symptoms the owning skills already define; they set severity, not new rules. The owner still decides whether the symptom is present — `better-accessibility` for a name or a focus ring, `better-colors` for a measured pair — and this list decides what it costs. In a change review, a confirmed `Regression` against any trigger is `HIGH` even when the same symptom would rank `MEDIUM` as a pre-existing issue, because the change is what removed it.

### 6. Consolidate Systemic Findings

One root cause is one finding. List every confirmed location in the same row rather than producing a row per occurrence. Do not pad the report to reach the finding cap; a short review or no findings is a valid result.

### 7. Make Restraint Visible

Record candidates considered but deliberately rejected. A candidate is rejected when the owning skill permits the current implementation, evidence is insufficient, the project's convention is a defensible choice and not merely an established one, or the proposed change would add complexity without user benefit.

### 8. Verify What Can Be Verified

Run safe, relevant checks available in the project. Inspect the rendered interface when runtime behavior or visual judgment matters. Report the exact command or interaction and observed result. If a check cannot be run, label it **Not verified** and state what remains; never convert a verification gap into a finding.

### 9. Review Without Mutating by Default

Treat a review request as read-only. Do not edit source code unless the user also asks to implement the findings. When implementation is requested, preserve the consolidated report as the change scope and re-run the relevant verification afterward.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Six disconnected domain reports | Consolidate into one ranked findings table |
| Same issue reported by multiple skills | Assign it to the skill that owns the underlying rule |
| Finding with no exact location | Cite `path/to/file:line` and the current implementation |
| Visual claim inferred only from source | Inspect the rendered state or mark it not verified |
| Unlimited low-impact polish | Respect the mode cap; omit `LOW` findings in `quick` |
| Silent gaps in coverage | Show which domains and states were actually inspected |
| Missing owning skill silently treated as covered | Mark the domain `Not reviewed` and name the unavailable skill |
| No rejected candidates | Include the required considered-but-rejected table |
| Review silently edits code | Stay read-only unless implementation was requested |
| “Approve” with pending actionable findings | Use `Needs changes` or `Block` |
| Every legacy issue in a touched file reported | Cap pre-existing findings at three in their own section |
| A pre-existing issue blocking a change review | Keep pre-existing findings out of the cap and out of the verdict |
| Domain marked `Clear` when the change never touched it | Mark it `Not reviewed — no evidence in the change scope` |

## Review Output Format

Always use the following sections.

### Scope and Coverage

State the mode, exact scope, stack and styling conventions, the project convention documents found in recon, and any review boundary. Then show coverage:

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | Files, components, states, or checks | Findings count or `Clear` |

Include all six domains. `Clear` means inspected with no actionable finding; `Not reviewed` must explain why.

### Findings

Use one table ordered by severity, then reach and leverage:

| # | Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | HIGH | Accessibility | `src/Dialog.tsx:42` | `<button><XIcon /></button>` | Add `aria-label="Close"` and hide the icon from the accessibility tree | The icon-only control has no accessible name |

Each row is one root cause. The **Domain** value is the owning skill without the `better-` prefix. Respect the mode's finding cap. If there are no findings, omit the table and state "No actionable interface findings."

### Considered but Rejected

Include 1–3 candidates in `quick` mode and 2–5 in `full` mode:

| Location | Candidate | Rejected because |
| --- | --- | --- |
| `src/Card.tsx:28` | Increase the shadow | Existing depth matches the shared surface token; changing one card would reduce consistency |

These are real candidates inspected during the review, not invented filler. If the scope genuinely contains fewer borderline candidates, include the ones that exist and say so.

### Verification

List each check or interaction, the exact command or steps, and the observed result. Separate checks that passed from checks marked **Not verified**.

### Verdict

End with exactly one:

- `Block` — one or more `HIGH` findings remain.
- `Needs changes` — only `MEDIUM` or `LOW` findings remain.
- `Approve` — no actionable findings remain and the claimed coverage was verified.

### Change-Scoped Reviews

When `interface-review` resolved the scope from version control, the format above applies with these four additions. They belong here because this file owns the format, the cap, and the verdict; `interface-review` supplies the resolved scope and the per-finding status.

1. **Scope block.** Open **Scope and Coverage** with the change scope table `interface-review` produced — target, base and head refs, commit and file counts, exclusions, surfaces expanded — then the coverage table above, unchanged, covering all six domains. A domain with no evidence anywhere in the change scope is `Not reviewed — no evidence in the change scope`, which is a coverage statement rather than a gap.
2. **Status column.** The findings table gains a `Status` column after `Domain`, carrying `Introduced` or `Regression` as `interface-review` classified it:

   | # | Severity | Domain | Status | Location | Before | After | Why |
   | --- | --- | --- | --- | --- | --- | --- | --- |
   | 1 | HIGH | Accessibility | Regression | `src/Dialog.tsx:42` | `aria-label="Close"` removed in this change | Restore `aria-label="Close"` on the icon-only control | The close control had an accessible name before this change and no longer does |

   With no `Introduced` or `Regression` findings, omit the table and state "No actionable interface findings in this change."

3. **Pre-existing section.** Place it after **Considered but Rejected**. At most three, highest severity first, and state plainly that they are not this change's responsibility. Omit the section when there are none.

   | Severity | Domain | Location | Issue |
   | --- | --- | --- | --- |
   | MEDIUM | Typography | `src/Toolbar.tsx:7` | Numeric badges use proportional figures; predates this change |

4. **Cap and verdict.** The mode's finding cap and the verdict both cover `Introduced` and `Regression` findings only. `Pre-existing` findings sit outside the cap, so a change touching a legacy file cannot turn into a full-file audit, and outside the verdict, so a change whose only findings are pre-existing is an `Approve`.
