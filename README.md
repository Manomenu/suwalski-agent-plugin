# suwalski-agent-plugin

A Claude Code plugin marketplace with one plugin, **suwagent**: review an agent's work on
visual pages instead of reading walls of text.

| Skill | When | What you get |
| :- | :- | :- |
| `/suwagent:visual-spec` | before planning a larger change | **what** and **why**: problem, goals and non-goals, scenarios, behaviour and edge cases, UI sketches, acceptance criteria, open questions |
| `/suwagent:visual-plan` | before writing code | **how**: decisions with the options weighed, an architecture diagram, a file map, planned code shapes, ordered steps with checks, verification, risks |
| `/suwagent:visual-recap` | after the work is done | **what was built and how it works**, without code or diffs: the elements and their roles, a walkthrough of a real scenario, diagrams, acceptance criteria checked against the spec/plan with evidence, deviations, verification results, where to look carefully |

Each page is one self-contained HTML file in `docs/visual/<date>-<slug>/` (`spec.html`,
`plan.html`, `recap.html`, linked to each other). It opens in your browser and works in
light and dark mode. Mermaid diagrams and syntax highlighting load from a CDN, and without
network you see the source instead.

**Feedback goes back to the agent from the page.** Answer the open questions, comment on any
section, choose ✅ Approve or ✏️ Request changes, press **Copy feedback for the agent** and
paste the result into the chat. The agent updates the same page.

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
python3 plugins/suwagent/scripts/vdoc.py check docs/visual/2026-10-25-visual-skills-plugin/recap.html
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
  scripts/vdoc.py                   new / check / open
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
