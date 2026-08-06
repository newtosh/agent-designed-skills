# Example Report

One complete report in the change-scoped shape, which is the base format plus its four additions. A screen review is the same minus the scope block, the `Status` column, and the `Pre-existing` section.

Every value below is invented. Read it for shape, ordering, and the level of specificity each cell carries — not as findings to look for.

---

## Scope and Coverage

`full` mode. Pull request 482, "Add destructive Button variant", on a Next.js App Router app styled with Tailwind v4 and CSS custom-property tokens in `src/styles/tokens.css`. Convention documents found: `CONTRIBUTING.md` and `docs/design-system.md`. Preview: none available in CI; rendered claims are marked below.

| Field | Value |
| --- | --- |
| Target | `pr 482` |
| Base ref | `origin/main` at `a1b2c3d` |
| Head ref | `refs/remotes/pr/482` at `e4f5g6h` |
| Commits | 7 committed, 0 uncommitted |
| Files in scope | 9 after exclusions |
| Excluded | `pnpm-lock.yaml`, `src/__snapshots__/` — lockfile and snapshots |
| Surfaces expanded | `app/checkout/page.tsx`, `app/settings/layout.tsx`; 6 further `Button` consumers not expanded, ranked by importer count |

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | `Button.tsx`, `ConfirmDialog.tsx`, `button.css`; keyboard walk of the checkout confirm step | 2 |
| Layout | `Toolbar.tsx`, `ActionBar.tsx` at 320px and 1280px | 1 |
| Writing | New `destructive` strings in `ConfirmDialog.tsx` and `Button.stories.tsx` | Clear |
| Typography | No type, wrapping, or numeral change in the diff | Not reviewed — no evidence in the change scope |
| Colors | `--color-destructive` against `--color-surface` and `--color-surface-raised` | 1 |
| UI | `Button.tsx` variant styles and transitions | 1 |

## Findings

| # | Severity | Domain | Status | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | HIGH | Accessibility | Regression | `src/styles/button.css:12`, and the same removal at `src/components/IconButton.tsx:19`, `src/components/MenuItem.tsx:27` | `:focus-visible { outline: 2px solid var(--color-focus) }` deleted in favour of `outline: none` while restyling the variant | Restore `:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px }` on the shared base, not per variant | Every keyboard user lost the focus indicator on all three controls; the ring existed before this change. Escalation trigger, so `HIGH` regardless of surface |
| 2 | HIGH | Colors | Introduced | `src/styles/tokens.css:41` | `--color-destructive: oklch(0.62 0.21 25)` — measures 3.1:1 against `--color-surface` | Darken to `oklch(0.52 0.19 25)`, which measures 4.6:1 against both surface tokens | The new variant's label is body-size text and needs 4.5:1; it currently fails on the default surface. Escalation trigger |
| 3 | MEDIUM | Accessibility | Introduced | `src/components/ConfirmDialog.tsx:31` | The dialog renders open with focus left on the trigger behind it | Move focus to the dialog on open and return it to the trigger on close | Keyboard and screen-reader users land outside the dialog they just opened and must tab back through the page to reach the destructive action |
| 4 | MEDIUM | Layout | Introduced | `src/components/Toolbar.tsx:18` | `margin-left: 16px` on the new destructive action | `margin-inline-start: 16px` | The new declaration is the only physical property in a toolbar that is otherwise direction-aware, so it mirrors wrongly in RTL |
| 5 | MEDIUM | UI | Introduced | `src/components/Button.tsx:63` | `destructive` defines base and hover only | Add `disabled` and `loading` treatments matching the other variants | The PR body states the variant is "for confirm dialogs"; those dialogs disable the action while the request is in flight, and the variant has no appearance for that state |

## Considered but Rejected

| Location | Candidate | Rejected because |
| --- | --- | --- |
| `src/components/Button.tsx:71` | Deepen the destructive hover step beyond the shared ramp | The ramp is one contrast-safe step used by every variant; deviating for one would cost consistency without making the hover clearer |
| `src/styles/tokens.css:41` | Replace the token everywhere rather than darkening it | The measured failure is body text on surface; the same token passes for icon and large-text use, so finding 2 fixes the pairing without touching consumers that are already correct |
| `src/components/Toolbar.tsx` | Convert the whole toolbar to logical properties | Only one declaration arrived in this change. Finding 4 covers what the change is responsible for; a full conversion is separate work |

## Pre-existing

Not this change's responsibility, listed for context only. Outside the finding cap and the verdict.

| Severity | Domain | Location | Issue |
| --- | --- | --- | --- |
| MEDIUM | Layout | `src/components/Toolbar.tsx:7` | Fixed `height: 40px` clips the overflow menu at 320px; predates this change |
| LOW | UI | `src/components/Card.tsx:28` | Shadow does not match the shared surface ramp; predates this change |

## Verification

| Check | Command or interaction | Result |
| --- | --- | --- |
| Fetched the PR head | `git fetch origin pull/482/head:refs/remotes/pr/482 --no-tags` | Wrote `refs/remotes/pr/482` at `e4f5g6h`; working tree untouched |
| Resolved the file list | `git diff --name-status a1b2c3d...refs/remotes/pr/482` | 11 files, 9 after exclusions |
| Counted consumers | `git grep -l "<Button" refs/remotes/pr/482 -- '*.tsx' \| wc -l` | 8; expanded the 2 route-level ones |
| Measured the pair | Computed from the `oklch()` values at `tokens.css:41` and `tokens.css:8` | 3.1:1 — fails 4.5:1 for body text |
| Keyboard order | Read `ConfirmDialog.tsx` and `Button.tsx` source | Focus is never moved into the dialog |

**Not verified.** The rendered appearance of the restored focus ring and of the missing `disabled` and `loading` states — the project exposes no preview command and a rendered review was not requested. Findings 1, 3, and 5 rest on source reading, which determines the behaviour in each case; finding 5's visual result is unconfirmed.

## Verdict

`Block` — findings 1 and 2 are `HIGH` and both remain.
