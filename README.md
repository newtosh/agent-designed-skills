# agent-designed-skills

Claude Code skill pack for fairer, higher-quality design and UX decisions
without turn-by-turn steering. Portable: clone it, run `install.sh`, done.

The pack mixes a few homegrown decision skills with vendored craft skills.
Load the smallest set that fits the job. Name the tradeoff and who it
affects (`design-decision-rubric`) before restyling a screen. Score the
flow (`ux-heuristic-audit`) before polishing it. Treat accessibility as a
gate, not a last pass.

## Layout

```
skills/<name>/SKILL.md   # manual /skill-name invocation
skills/<name>/*.py       # implementation, stdlib only (homegrown skills)
hooks/<name>.py          # PreToolUse hook scripts
install.sh               # symlinks skills/ and hooks/ into ~/.claude/
vendor.json              # manifest of vendored (upstream) skills
vendor-update.sh         # pull upstream changes into a vendored skill
pyproject.toml           # packages the homegrown checkers; ruff + black
```

Each skill is a self-contained dir. Copy one out on its own, or add more,
without cross-contamination. Homegrown checkers use the standard library
only. `pyproject.toml` packages those checkers and configures ruff and
black. It adds no runtime dependencies.

## Skills

### Homegrown

- **design-decision-rubric** — writes a decision down before it becomes a
  vibe: the choice, at least two options, who is affected, when not to
  apply it, the tradeoff, and the recommendation. `check.py` rejects a
  record that skips a section. It does not judge whether the tradeoff is
  honest.
- **ux-heuristic-audit** — severity-rated review against Nielsen's ten
  heuristics plus three Krug checks (don't make me think, omit needless
  words, billboard test). Every id is `checked` or `not observed`. A real
  finding needs evidence, a fix, and the case where the fix is wrong.
  Original checklist for this pack. See Candidates for the wondelai skill
  it does not copy.
- **accessibility-gate** — mechanical tripwire for missing `alt`, unlabeled
  controls, nameless icon buttons, `<html>` without `lang`, and `outline`
  removed with no `:focus-visible`. Not a WCAG audit. The vendored
  `accessibility` skill is the audit. Also wired as a hook (see Install).
- **obsidian-ui** — how to discover and install [ObsidianUI](https://www.obsidianui.dev)
  components (MIT, Atharv / Atharvsinh-codez). Animated and interactive
  React UI the project owns: buttons, menus, galleries, scroll, text
  streams. There is no upstream `SKILL.md` to vendor. The skill follows the
  official agent instructions: read `llms.txt` and the registry, then
  `npx shadcn@latest add "https://www.obsidianui.dev/r/{name}.json"`, or
  copy the manifest files by hand. MCP is optional and not required.

### Vendored

Curated, not forked. See [Curation](#curation). These are the Kail
starting list entries that have a real `SKILL.md` and a clear MIT or
Apache license. Two list entries are not here; see
[Candidates / blocked](#candidates--blocked).

- **frontend-design** — [anthropics/skills](https://github.com/anthropics/skills)
  `skills/frontend-design/` (Apache-2.0). Distinct, production-grade UI
  that is tied to the subject of the brief, with an explicit pass against
  generic generated looks.
- **apple-design** — [emilkowalski/skills](https://github.com/emilkowalski/skills)
  `skills/apple-design/` (MIT). Apple-like interface craft from Emil
  Kowalski's design-engineer skills.
- **emil-design-eng** — same repo, `skills/emil-design-eng/` (MIT).
  Design-engineering judgment: motion, detail, and when not to decorate.
- **beautiful-shadows** — [MengTo/Skills](https://github.com/MengTo/Skills)
  `agent-skills/web-design/beautiful-shadows/` (MIT). Layered elevation
  that stays neutral, plus when not to use the large shadow.
- **accessibility** — [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills)
  `skills/accessibility/` (MIT). WCAG 2.2 audit workflow, POUR, and the
  checks a live Lighthouse run does not replace.
- **better-interface** — [jakubkrehel/skills](https://github.com/jakubkrehel/skills)
  `skills/better-interface/` (MIT). Interface critique aimed at clarity
  of the UI in front of you.
- **interaction-design** — [wshobson/agents](https://github.com/wshobson/agents)
  `plugins/ui-design/skills/interaction-design/` (MIT). Interaction
  patterns, microinteractions, and motion references.
- **shadcn** — [shadcn-ui/ui](https://github.com/shadcn-ui/ui)
  `skills/shadcn/` (MIT). How to add, compose, and style shadcn/ui from
  the project's own source. Pair with `obsidian-ui` when the component
  should come from the ObsidianUI registry instead of the default one.

## Curation

No GitHub fork relationship to any upstream repo. `git subtree` pulls
each skill subdirectory into `skills/<name>/`, full upstream history
intact (`git log skills/<name>/`). Each carries its original license
(`LICENSE`, `LICENSE.md`, or `LICENSE.txt`) plus an `ATTRIBUTION.md`.

**Pulling upstream updates:**

```bash
./vendor-update.sh accessibility     # one skill
./vendor-update.sh --all             # everything in vendor.json
```

Re-clones the upstream repo, re-splits the same source subdirectory, and
`git subtree pull`s it in as a merge commit. Repeatable, not a one-time
copy. Requires a clean working tree, `git subtree`, and `jq`.
`LICENSE` / `ATTRIBUTION.md` are hand-maintained, outside the subtree
path, except where upstream already ships a license file inside the skill
directory (`frontend-design` ships `LICENSE.txt`). Recheck them if an
upstream's license changes.

**Adding a new vendored skill:** add an entry to `vendor.json` (`repo`,
`source_prefix`, `target_prefix`, `license`, `copyright`), then do the
one-time `git subtree add` yourself (see git history on
`skills/frontend-design` for the pattern), then drop in `LICENSE` and
`ATTRIBUTION.md` if the subtree did not already contain a license file.
`vendor-update.sh` handles every pull after that.

## Install

```bash
git clone <this-repo> ~/bin/src/agent-designed-skills   # or wherever
~/bin/src/agent-designed-skills/install.sh
```

Symlinks each `skills/<name>` and `hooks/<file>` into
`~/.claude/skills/` and `~/.claude/hooks/`. Safe to re-run after
`git pull`.

**Hook wiring is separate and manual.** `install.sh` only places the
hook script. It doesn't touch `~/.claude/settings.json` (machine/env
specific, may already have other hooks). Add the matcher yourself:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Artifact|mcp__github__create_pull_request|mcp__github__add_issue_comment|mcp__github__add_comment_to_pending_review|mcp__github__pull_request_review_write|mcp__github__create_or_update_file|mcp__github__push_files|mcp__github__issue_write",
      "hooks": [
        { "type": "command", "command": "python3 ~/.claude/hooks/accessibility-gate.py", "timeout": 10 }
      ]
    }
  ]
}
```

Adjust the matcher to whatever publish or file-write tools exist in that
env. The hook scans string fields in `tool_input` that look like markup.
It fails open on errors.

Check the homegrown Python from a checkout:

```bash
python3 -m unittest discover -s tests
python3 -m pip install -e '.[dev]'
python3 -m ruff check .
python3 -m black --check .
```

## Adding a new skill

1. `mkdir skills/<name>`, write `SKILL.md` plus implementation (stdlib
   only, type-annotated, no venv/deps to manage across machines).
2. If you added a checker, point `pyproject.toml` at it and cover it in
   `tests/`.
3. Re-run `install.sh`.
4. If it needs to run automatically, not only on-demand, add a
   `hooks/<name>.py` and wire it into `settings.json` per-env as above.

## Candidates / blocked

Not vendored. Do not paste these bodies into the pack.

- **design-review** — <https://github.com/superfuture/design-review>
  (`design-review/skills/design-review/SKILL.md`,
  <https://www.ui-skills.com/skills/superfuture/design-review>).
  The README says "MIT © Joey Primiani", but the repository has no
  `LICENSE` file and GitHub reports no license. The skill also sends an
  anonymous usage ping and offers a license-gated Pro mode. Not a clean
  vendor.
- **adapt** — <https://github.com/pbakaus/impeccable> (Apache-2.0) at
  `skill/reference/adapt.md`
  (<https://www.ui-skills.com/skills/pbakaus/adapt>). Not a standalone
  `SKILL.md`. It is one reference chapter inside the impeccable bundle
  (`skill/SKILL.src.md`, browser scripts, font index). Subtree-ing that
  bundle would not add an `adapt` skill, and copying the chapter out would
  leave the subtree workflow. Not vendored.
- **cuellarfr/design-skills** — MIT, broader UX set (critique, research,
  journey mapping, a second `interaction-design`). Overlaps skills already
  in this pack. Candidate if a later pass wants research and journey
  mapping: <https://github.com/cuellarfr/design-skills>.
- **smarks26/universal-design-principles** — `LICENSE` is MIT (GitHub's
  detected SPDX is Other). Large multi-plugin principle library. Left out
  of this PoC so the pack stays a starting set:
  <https://github.com/smarks26/universal-design-principles>.
- **wondelai ux-heuristics** — MIT. Nielsen plus Krug with severity
  ratings. Inspiration for `ux-heuristic-audit`, not vendored, so the
  report shape stays the one `check.py` enforces:
  <https://github.com/wondelai/skills> (`plugins/ux-design/skills/ux-heuristics/`)
  and <https://skills.wondel.ai/skills/ux-heuristics/>.
