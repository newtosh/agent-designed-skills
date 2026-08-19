---
name: better-interface
description: >-
  Cross-discipline interface review. Routes a screen, flow, or feature to every `better-*`
  domain skill and consolidates one ranked verdict. Use when asked for a holistic review
  rather than a single domain, and when `interface-review` hands up a change to route.
  Triggers on better-interface, holistic interface review, review the whole screen.
---

# Interface review

This skill runs a cross-discipline review. It routes the interface to each `better-*` skill, collects their evidence, and consolidates one ranked verdict.

Orchestration is all it owns. Accessibility rules belong to `better-accessibility`, structure to `better-layout`, copy to `better-writing`, type to `better-typography`, color to `better-colors`, visual polish and motion to `better-ui`. Never duplicate or override their rules here.

Change-scoped review of uncommitted work, branches, and pull requests belongs to `interface-review`, which resolves the scope and classifies findings before handing the review back here.

## Evidence, not taste

Press hard on the escalation triggers and leave deliberate project choices alone. Those pull in the same direction rather than against each other. A trigger is a failure whatever the style guide says. A density, radius, or voice you merely disagree with is not a finding.

So the bar for reporting is evidence, not taste. The bar for `Approve` is that you inspected what you claim to have inspected. A short report from a real inspection beats a long one padded to look thorough.

## Core principles

### 1. Resolve the scope first

Infer the screen, flow, feature, or repository scope from the request and current workspace. State the resolved scope in the output.

Cover all of it across every domain skill listed under **Use domain skills as the sources of truth**, including the empty, loading, error, and narrow-width states where they exist. Report at most 15 findings.

When the requested scope is too large to inspect credibly, narrow it to one complete flow. Take the flow the request centers on. Failing that, take the entry path every user of the scope must pass through. State the boundary and what it excluded. Never imply uninspected surfaces were reviewed.

### 2. Send a change to `interface-review`

When the request names a branch, pull request, commit range, or uncommitted changes, that is a change review, not a screen review. Say so and ask the user to run `interface-review`. It is user-invoked, so this skill cannot start it.

Never resolve a change scope here. Reading a diff, classifying findings, and expanding changed files to affected surfaces all belong to `interface-review`. Guess at them and you produce a report whose scope nobody can check.

When `interface-review` hands a review back, it supplies the change scope, a status per finding, and the change-scoped report format. Severity, ranking, the cap, and the verdict stay here, and all three cover `Introduced` and `Regression` only.

### 3. Recon before judgment

Identify the framework, styling system, component library, design tokens, supported viewports, and any preview or test command. Write every fix in the project's own idiom, so no finding arrives as a request to adopt a different stack. That governs the form of the fix, not whether the current code is good enough.

Then read what the project has written about its own interface: `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `AGENTS.md`, `CLAUDE.md`, a design-system doc, Storybook docs, interface ADRs. Name in the output which you found, or that there are none.

Read them to find where a finding belongs, not for permission to drop it. A documented convention is no evidence the convention is good, and "it's in the style guide" does not retire a finding. What they change is **where** you report. When a guideline or a shared token is the cause, report it once against that source, with the components as its locations.

### 4. Use domain skills as the sources of truth

Before reviewing, confirm that every owning skill below is available. Load and apply every available owner, and complete each domain review before consolidation.

Review in this order so foundational failures are not hidden by polish:

1. `better-accessibility`
2. `better-layout`
3. `better-writing`
4. `better-typography`
5. `better-colors`
6. `better-ui`

From a domain skill loaded here, take its principles, its references, and its verification checks. Its severity ladder and its format are for standalone use; the consolidated format, shared severity, and finding cap in this file replace them.

If an owning skill is unavailable, mark that domain `Not reviewed`, name the missing skill, and continue with the remaining domains. Do not recreate its rules from memory, substitute a neighboring skill, or claim holistic coverage.

When two skills appear to cover the same issue, assign it to the skill that owns the underlying rule and mention secondary effects in the **Why** cell. Report it once.

### 5. Require evidence

Every finding cites `path/to/file:line` and shows the current implementation. Do not report a code-level finding from visual appearance alone or a visual finding from source code alone when runtime behavior determines the result.

### 6. Rank by user impact

Use one shared severity scale:

- `HIGH`: blocks a task, misleads the user, hides content or controls, causes data-loss risk, or creates a repeated systemic failure.
- `MEDIUM`: meaningfully harms comprehension, efficiency, adaptability, or consistency.
- `LOW`: isolated polish with limited task impact.

Within a severity, rank by how many places the finding reaches and how much one fix buys. A token or shared-component fix outranks the same symptom in one leaf component.

**Escalation triggers.** Once the owning skill confirms one of these, it is `HIGH` on sight, never averaged down because the surface is minor:

- An interactive control with no accessible name.
- A keyboard-reachable control with no visible focus indicator.
- A control or path reachable by pointer but not by keyboard.
- Motion or auto-playing content that ignores `prefers-reduced-motion`.
- Content or a control clipped, overlapped, or unreachable at 320px width or 200% zoom.
- Body or control text whose rendered contrast pair fails its required ratio.
- State or meaning carried by color alone.
- A destructive action with no confirmation, undo, or distinct treatment.

Triggers rank above every other finding. When more fire than the cap allows, list them first and state how many the cap excluded. A cap may shorten a report. It may never be why a blocker went unreported.

These set severity, not new rules. The owning skill still decides whether the symptom is present, and this list decides what it costs. In a change review, a confirmed `Regression` against a trigger is `HIGH` even where the same symptom would be `MEDIUM` as pre-existing.

### 7. Prefer the cheaper fix

Severity says how bad a finding is. This says which kind of fix to propose. When more than one would work, take the earliest that does:

1. **Delete.** A separator that space would carry, an animation on a high-frequency interaction, an ARIA attribute a native element makes redundant, a ramp nothing imports.
2. **Use the platform.** The native element, the native control, the browser's own focus ring, in place of a custom rebuild.
3. **Reuse what the project has.** An existing token, spacing step, or motion curve, before any new value.
4. **Correct the value.** The wrong easing, radius, gap, or contrast pair, using the exact value the owning skill gives.
5. **Add.** A new token, a wrapper, a media query, an ARIA attribute the platform cannot supply.

A fix written at step 5 where step 1 was available is its own finding. Report the deletion instead.

### 8. Consolidate systemic findings

One root cause is one finding. List every confirmed location in the same row rather than producing a row per occurrence. Do not pad the report to reach the finding cap; a short review or no findings is a valid result.

### 9. Verify what can be verified

Run safe, relevant checks available in the project. Inspect the rendered interface when runtime behavior or visual judgment matters. Report the exact command or interaction and observed result. If a check cannot be run, label it **Not verified** and state what remains; never convert a verification gap into a finding.

### 10. Review without mutating by default

Treat a review request as read-only. Do not edit source code unless the user also asks to implement the findings. When implementation is requested, preserve the consolidated report as the change scope and re-run the relevant verification afterward.

## Before you finish

| Mistake | Fix |
| --- | --- |
| Six disconnected domain reports | Consolidate into one ranked findings table |
| Visual claim inferred only from source | Inspect the rendered state or mark it not verified |
| Silent gaps in coverage | Show which domains and states were actually inspected |
| Missing owning skill silently treated as covered | Mark the domain `Not reviewed` and name the unavailable skill |
| Every legacy issue in a touched file reported | Cap pre-existing findings at three in their own section |
| A pre-existing issue blocking a change review | Keep pre-existing findings out of the cap and out of the verdict |
| Domain marked `Clear` when the change never touched it | Mark it `Not reviewed: no evidence in the change scope` |

## Review output format

The format lives in [review-format.md](review-format.md): scope and coverage, the findings table, verification, and the verdict. A review is not finished until its findings are reported there.
