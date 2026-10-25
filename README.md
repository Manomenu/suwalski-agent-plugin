# suwalski-agent-plugin

A Claude Code plugin marketplace with one plugin, **suwagent**: review an agent's work on
visual pages instead of reading walls of text.

**Visual documents** (the agent offers them for larger changes, or you run them yourself):

| Skill | When | What you get |
| :- | :- | :- |
| `/suwagent:visual-spec` | before planning a larger change | **what** and **why**: problem, goals and non-goals, scenarios, behaviour and edge cases, UI sketches, acceptance criteria, open questions |
| `/suwagent:visual-plan` | before writing code | **how**: decisions with the options weighed, an architecture diagram, a file map, ordered steps with checks, verification, risks |
| `/suwagent:visual-recap` | after the work is done | **what was built and how it works**, without code or diffs: elements and their roles, a walkthrough of a real scenario, diagrams, acceptance criteria checked with evidence, deviations, where to look carefully |
| `/suwagent:plan-judge` | you have 2+ plans for the same task (Claude vs Codex, two sessions) | the plans compared side by side against the real code, and one verdict (adopt / hybrid / revise) published as a visual plan |

**Ways of working:**

| Skill | Invoked | When | How it works |
| :- | :- | :- | :- |
| `/suwagent:autopilot` | only by you | you leave the agent alone with a task | no routine questions: it decides, logs every decision, stops only for real blockers (secrets, destructive steps, merge/push), and ends with a visual recap listing **decisions made without you** |
| `/suwagent:orchestrate` (alias `/suwagent:efficient-frontier`) | only by you | a big task with lots of reading, testing or mechanical edits | the main (expensive) model plans, decides and reviews; cheaper subagents (`haiku` for search, `sonnet` for edits and tests) do the volume, at most 3 at a time |
| `/suwagent:limit-guard` | by autopilot and orchestrate, or by you | long or parallel work on a Pro/Max plan | reads the real 5-hour and weekly usage between steps and pauses new work at 90% / 95%, so your own work keeps headroom. Needs a one-time status line tap (`/suwagent:limit-guard setup`) |
| `/suwagent:mandatory-docs` | automatically | before code that uses a library, framework, CLI or provider API | reads the official docs **of the installed version** instead of coding from memory, and names its sources |

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

**The plugin also gives the agent a standing working agreement.** A `SessionStart` hook
adds three short rules to Claude's context, and each one can be switched off in `/plugin`
→ suwagent → Configure:

- **Spec → plan → recap.** Before a larger change, the agent offers a spec and then a plan,
  writes code only after the plan is approved, and offers a recap at the end. Small changes
  are done directly.
- **Status line.** Every finished piece of work ends with one line: 🟢 done, 🟡 something
  specific pending, or 🔴 waiting for you.
- **Docs before code.** Before using a library, framework, CLI or provider API, the agent
  reads the current official docs (`/suwagent:mandatory-docs`).

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
  skills/visual-{spec,plan,recap}/  the visual document skills (SKILL.md each)
  skills/mandatory-docs/            docs-before-code procedure
  skills/autopilot/ orchestrate/ plan-judge/ limit-guard/   ways of working
  skills/efficient-frontier/        alias of orchestrate
  scripts/limits.py                 status line tap and usage check for limit-guard
  shared/template.html              the page: CSS + JS that render every block
  shared/authoring.md               rules shared by the three skills
  shared/components.md              the block catalog (HTML snippets)
  scripts/vdoc.py                   new / check / open / links / register
  hooks/hooks.json                  SessionStart → scripts/session-context.sh
  hooks/context/*.md                the parts of the working agreement added to Claude's context
docs/visual/                        visual documents of this repository (a real recap example)
```

Plugins can also carry subagents (`agents/`), MCP servers (`.mcp.json`), LSP servers,
output styles, themes, monitors, workflows and `bin/` executables. A `CLAUDE.md` inside a
plugin is **not** loaded: always-on instructions go in a hook like the one above, and
instructions for a task go in a skill.

Inspired by [BuilderIO/skills](https://github.com/BuilderIO/skills) (MIT, © Builder.io):
`/visual-plan` and `/visual-recap` gave the idea for the visual documents, and the status line
and `mandatory-docs`, `autopilot`, `plan-judge`, `orchestrate` and `limit-guard` are adapted from
their `quick-recap`, `read-the-damn-docs`, `plow-ahead`, `plan-arbiter`, `efficient-frontier` and
`stay-within-limits`. Their
visual skills need Builder's hosted Plans app. suwagent writes plain HTML into the repository
and publishes it as a claude.ai artifact, or keeps it local.
