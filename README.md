# suwalski-agent-plugin

A Claude Code plugin marketplace with one plugin, **suwagent**: review an agent's work on
visual pages instead of reading walls of text.

| Skill | When | What you get |
| :- | :- | :- |
| `/suwagent:visual-spec` | before planning a larger change | **what** and **why**: problem, goals and non-goals, scenarios, behaviour and edge cases, UI sketches, acceptance criteria, open questions |
| `/suwagent:visual-plan` | before writing code | **how**: decisions with the options weighed, an architecture diagram, a file map, planned code shapes, ordered steps with checks, verification, risks |
| `/suwagent:visual-recap` | after the work is done | **what was built and how it works**, without code or diffs: the elements and their roles, a walkthrough of a real scenario, diagrams, acceptance criteria checked against the spec/plan with evidence, deviations, verification results, where to look carefully |

Each page is one self-contained HTML file in `docs/visual/<spec|plan|recap>/<date>-<slug>.html`.
The spec, plan and recap of the same work share a file name and link to each other. Pages
work in light and dark mode, and Mermaid diagrams load from a CDN (offline you see their
source).

**By default each page is also published as a claude.ai artifact**, so you open it from a link
on any device and comment on it. The local file stays the source, and every published link
is recorded in `docs/visual/<kind>/claude-artifacts.md`, so the next update goes to the same
artifact. For client or confidential repositories, set *Where visual documents go* to
`local` in `/plugin` → suwagent → Configure. Then nothing leaves the machine and the page
opens in your browser.

**Feedback goes back to the agent from the page.** Comment on the artifact, or answer the
open questions, comment on sections, choose ✅ Approve or ✏️ Request changes, press **Copy
feedback for the agent** and paste it into the chat. The agent updates the same page and the
same artifact.

**The plugin also tells the agent about the workflow.** A `SessionStart` hook adds a short
working agreement to Claude's context: before a larger change, offer a spec and then a plan,
code only after the plan is approved, and offer a recap at the end. Small changes are done
directly. To turn it off, run `/plugin`, open suwagent, choose **Configure**, and set
*Suggest spec → plan → recap* to off.

## Install

In Claude Code:

```
/plugin marketplace add Manomenu/suwalski-agent-plugin
/plugin install suwagent@suwalski-agent-plugin
```

Requirements: `git` and `python3` (the helper script uses only the standard library).

### Updates

Your installed copy is cached, so it does not change on its own unless you turn
auto-update on:

- **Automatic**: go to `/plugin` → **Marketplaces** → `suwalski-agent-plugin` → **Enable
  auto-update**. Third-party marketplaces have it off by default.
- **Manual**: run `/plugin marketplace update suwalski-agent-plugin`.

`plugin.json` has no `version` on purpose, so every pushed commit counts as a new version.
If you add a `version`, users only get an update when you bump it.

## Develop

```bash
claude --plugin-dir ./plugins/suwagent        # try local changes without installing
claude plugin validate .                      # check the marketplace and the plugin
python3 plugins/suwagent/scripts/vdoc.py check docs/visual/recap/2026-10-25-suwagent-plugin.html
```

After editing the plugin in a running session, run `/reload-plugins`.

## Layout

```
.claude-plugin/marketplace.json     the catalog: lists the plugins in this repository
plugins/suwagent/
  .claude-plugin/plugin.json        manifest: name, description, userConfig
  skills/visual-{spec,plan,recap}/  the three skills (SKILL.md each)
  shared/template.html              the page: CSS + JS that render every block
  shared/authoring.md               rules shared by the three skills
  shared/components.md              the block catalog (HTML snippets)
  scripts/vdoc.py                   new / check / open / links / register
  hooks/hooks.json                  SessionStart → scripts/session-context.sh
  hooks/session-context.md          the working agreement added to Claude's context
docs/visual/                        visual documents of this repository (a real recap example)
```

Plugins can also carry subagents (`agents/`), MCP servers (`.mcp.json`), LSP servers,
output styles, themes, monitors, workflows and `bin/` executables. A `CLAUDE.md` inside a
plugin is **not** loaded: always-on instructions go in a hook like the one above, and
instructions for a task go in a skill.

Inspired by [BuilderIO/skills](https://github.com/BuilderIO/skills) (`/visual-plan`,
`/visual-recap`). Those skills publish to Builder's hosted Plans app; suwagent writes local
HTML files with no account or service.
