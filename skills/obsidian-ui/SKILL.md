---
name: obsidian-ui
description: Install and adapt ObsidianUI React components the project owns (buttons, menus, galleries, scroll animations, text streams, interface details). Discover them from llms.txt and the public registry, then install with the shadcn registry URL or by copying files. Use when the user wants an animated or interactive React UI from obsidianui.dev. Does not require MCP.
---

# ObsidianUI

ObsidianUI is a React component library the project owns and can edit.
Start from a published example, take its source, and fit it to the
project's existing design system. It is not a backend, a hosted agent, or
a place to deploy.

Official agent instructions (MIT): <https://www.obsidianui.dev/agent-instructions.md>
Index: <https://www.obsidianui.dev/llms.txt>
Registry: <https://www.obsidianui.dev/r/registry.json>
Repository: <https://gitlab.com/Atharvsinh-codez/ObsidianUI>

This skill is a homegrown guide to that public surface. It is not an
upstream `SKILL.md`. ObsidianUI is by Atharv (Atharvsinh-codez). The
library is MIT; keep that copyright and license notice when the project
license says to. Demo images and third-party packages keep their own
licenses. A component demo does not give rights to those external assets.

## When to use

The user wants a React interface piece they can customize: a button, menu,
gallery, scroll animation, text stream, or similar detail, and ObsidianUI
has a published example of it.

## When not to use

- The project is not React, or the user asked for a different library.
- The job is authentication, payments, storage, or deployment. ObsidianUI
  does not supply those.
- The job is a design decision with no component yet. Use
  `design-decision-rubric` first, then come back for a component.
- There is no published component for the request. Do not invent a name.
  Say so and pick the closest documented component, or build from the
  project's own system (`shadcn` if that is what the project uses).

## Discover

1. Read <https://www.obsidianui.dev/llms.txt> and the catalogue at
   <https://www.obsidianui.dev/markdown/components.md>. Match a documented
   name to the use case.
2. GET <https://www.obsidianui.dev/r/registry.json>. Each item has `name`,
   `type`, `dependencies`, and `files`.
3. GET `https://www.obsidianui.dev/r/{name}.json` for a real name from that
   registry. The body is a shadcn-compatible manifest. Read every
   `files[].content`, `files[].target`, `dependencies`, `docs`, and `meta`
   field that is present. A direct download does not execute code.

A missing page is not an empty document. Recover through the sitemap
(<https://www.obsidianui.dev/sitemap.xml>), `llms.txt`, or the registry.
On a temporary server error, retry with backoff.

Pages can be read without JavaScript: request `Accept: text/markdown`, or
open `/markdown/docs/{slug}.md`. The homepage markdown is
<https://www.obsidianui.dev/markdown/index.md>. Source blocks on those
pages include the install files. The JSON manifest is the machine-readable
download.

## Install

Prefer the project's existing shadcn workflow. The documented command is:

```bash
npx shadcn@latest add "https://www.obsidianui.dev/r/{name}.json"
```

Use the project's package runner (`pnpm dlx`, `bunx`) when that is how the
repo already runs shadcn. Run it only in the user's project, and only when
they asked to add the component.

Optional registry alias, in the project's `components.json`. The skill
works without this. The URL form above is enough.

```json
{
  "registries": {
    "@obsidian": "https://www.obsidianui.dev/r/{name}.json"
  }
}
```

### Manual copy

Use this when the shadcn CLI is not how the project installs components.

1. Resolve aliases from the destination `components.json`: `@ui/` is
   `aliases.ui`, `@components/` is `aliases.components`, `@lib/` is
   `aliases.lib`, `@hooks/` is `aliases.hooks`. Map those TypeScript
   aliases to real directories. On the site's own defaults, `@ui/button.tsx`
   is `src/components/ui/button.tsx` and
   `@components/block/hover-img.tsx` is
   `src/components/block/hover-img.tsx`. A `public/` target is relative to
   the project root. Do not create folders named `@ui` or `@components`.
2. Copy every required file, including CSS, hooks, utilities, shaders, and
   local assets. Stay inside the project. Read a file before replacing it.
3. Install each listed dependency with the project's package manager.
   React, React DOM, and a compatible host framework are already the
   project's job.
4. Keep `"use client"` boundaries, CSS imports, and alias config. Start
   from the usage example.
5. If `meta.remoteAssets` lists demo images or videos, replace them with
   the user's assets before calling the work done. If `meta.requiredEndpoints`
   is present, the app has to implement those endpoints. The registry does
   not provide them.

## Check the result

Copying the files is not a test. Render the component with the user's real
content. Tab through it. Turn on reduced motion. Check the target viewport.
If the interaction fails, fix the integration. Do not report the install
command as success.

## MCP is optional

Nothing above needs MCP. Public docs and the registry need no account, API
key, or token.

A checkout of the ObsidianUI repo can run a local stdio MCP server:
install dependencies, run `npm run registry:build`, then `npm run mcp` with
the checkout as the working directory. It exposes `resources/list` and
`resources/read` at `obsidian://{name}`. It does not install components and
it is not a hosted HTTP server. See <https://www.obsidianui.dev/mcp>.
Skip it unless the user already has that checkout and asked for it.
