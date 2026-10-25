<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/hero-dark.png">
  <img alt="suwagent, a Claude Code plugin: review your coding agent's work on visual pages, not walls of text. Spec → plan → recap, a 🟢🟡🔴 status line, autopilot and orchestrate, docs before code. 3 kinds of page, 10 skills, 1 hook, 0 accounts or API keys." src="docs/visual/board/img/readme/hero-light.png" width="100%">
</picture>

## Install

In a Claude Code session:

```
/plugin marketplace add Manomenu/suwalski-agent-plugin
/plugin install suwagent@suwalski-agent-plugin
```

Pick a scope (user scope gives it to you in every project), then type `/suwagent:` to see the skills.
Requirements: `git` and `python3` (standard library only).

> [!NOTE]
> **The working agreement is the owner's.** Replies come in the language you write in, Polish or
> English, short, with pictures over prose. To change any of it, fork the repository and edit
> [`working-with-user.md`](plugins/suwagent/hooks/context/working-with-user.md)
> ([Make it yours](#make-it-yours)).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/why-dark.png">
  <img alt="Why. Without: the plan is 200 lines of chat; 'Done!' after code nobody ran; you read a diff to learn what changed; API calls from memory; every session starts from zero. With suwagent: a plan page approved with one button; every answer ends with 🟢 🟡 🔴; a recap with roles, a real scenario and the spec's criteria; official docs of the installed version; a session hook with the same working agreement everywhere." src="docs/visual/board/img/readme/why-light.png" width="100%">
</picture>

## How it works

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/flow-dark.png">
  <img alt="One larger task: Spec (what and why, approve) → Plan (how, approve) → Build (only after approval, docs first, optionally autopilot or orchestrate) → Recap (what was built, criteria checked). On every page: comment, answer questions, Approve or Request changes, Copy feedback for the agent, and the same page is updated. Answers end with a status line: 🟢 done, 🟡 pending, 🔴 waiting for you." src="docs/visual/board/img/readme/flow-light.png" width="100%">
</picture>

You don't have to remember any command: the agent offers each page in one line when a task is big
enough. Every page is a self-contained HTML file in `docs/visual/<spec|plan|recap>/`, and by
default also a private claude.ai artifact you can open and comment on from any device.

This is what one looks like — [the recap of this repository](docs/visual/recap/2026-10-25-suwagent-plugin.html), in Polish:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/recap-dark.png">
  <img alt="A real visual recap page: TL;DR, stats, a diagram of the plugin, and the feedback bar" src="docs/assets/recap-light.png" width="100%">
</picture>

## The skills

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/skills-dark.png">
  <img alt="Visual documents: visual-spec (what and why), visual-plan (how), visual-recap (what was built), plan-judge (several plans into one), visual-readme (you start it; a README told in pictures, light and dark). Ways of working: autopilot (you start it; no routine questions, decisions logged), orchestrate (you start it; the main model decides, haiku and sonnet subagents do the volume), limit-guard (pauses at 90% of the 5-hour or 95% of the weekly limit), mandatory-docs (automatic; official docs of the installed version)." src="docs/visual/board/img/readme/skills-light.png" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/choose-dark.png">
  <img alt="Which one, when: a typo or question → just done; details still open → visual-spec; requirements clear → visual-plan; two plans → plan-judge; 'do it without me' → autopilot; mostly reading, tests, mechanical edits → orchestrate; a long run on Pro/Max → limit-guard; work finished → visual-recap; the README is a wall of text → visual-readme." src="docs/visual/board/img/readme/choose-light.png" width="100%">
</picture>

All skills are invoked as `/suwagent:<name>`; `/suwagent:efficient-frontier` is an alias of
`orchestrate`. Only you start `autopilot`, `orchestrate` and `visual-readme`.

The pictures in this README were made by `/suwagent:visual-readme`: panels on a board page,
drawn with the same styles as the spec, plan and recap pages and rendered in both themes.

<details>
<summary><b>orchestrate</b> and <b>limit-guard</b>, inside</summary>

```mermaid
flowchart LR
  M["Main model<br/>plan · decisions · integration · review"]
  subgraph Wave["wave of ≤ 3 in parallel"]
    H1["haiku<br/>search, inventory, logs"]
    S1["sonnet<br/>edits, tests"]
    S2["sonnet<br/>edits, tests"]
  end
  M -->|"brief: goal, scope, commands,<br/>answer format, when to stop"| Wave
  Wave -->|"evidence: file:line, commands, results"| M
  M --> LG["limit-guard<br/>between waves"]
```

```mermaid
flowchart LR
  CC["Claude Code<br/>rate_limits 5h / 7d"] -->|JSON| TAP["status line:<br/>limits.py tap<br/>(your own status line keeps working)"]
  TAP --> F[("~/.claude/suwagent/<br/>rate-limits.json")]
  F --> ST["limits.py status"] --> AG{"agent"}
  AG -->|OK| GO["continues"]
  AG -->|PAUSE| W["finishes the current step,<br/>waits for the reset"]
  AG -->|UNKNOWN| NG["works without the guard<br/>(says so once)"]
```

limit-guard needs a one-time `/suwagent:limit-guard setup`, which adds the status line tap.

</details>

## Settings and privacy

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/visual/board/img/readme/settings-dark.png">
  <img alt="Settings in /plugin → Installed → suwagent → Configure options: 'How to work with me' is always on; switches for Suggest spec → plan → recap, Status line, Read the docs before coding (all on by default); Where visual documents go: artifact (default: local HTML plus a private claude.ai artifact) or local (nothing leaves the machine, for client repositories)." src="docs/visual/board/img/readme/settings-light.png" width="100%">
</picture>

- An artifact is private until you share it; its link is recorded in `docs/visual/<kind>/claude-artifacts.md`.
- Pages load Mermaid and highlight.js from public CDNs; offline they still read, with diagram source in place of diagrams.
- `limit-guard` keeps a usage snapshot in `~/.claude/suwagent/rate-limits.json`. No accounts or API keys.

## Make it yours

The working agreement is plain Markdown that a `SessionStart` hook adds to every session
(on start, `/clear` and compaction):

| File | Part |
| :- | :- |
| [`working-with-user.md`](plugins/suwagent/hooks/context/working-with-user.md) | language, length, pictures over prose, no raw code, honest status (always on) |
| [`visual-workflow.md`](plugins/suwagent/hooks/context/visual-workflow.md) | when to offer a spec, plan or recap, and which way of working to recommend |
| [`quick-recap.md`](plugins/suwagent/hooks/context/quick-recap.md) | the 🟢 🟡 🔴 status line |
| [`mandatory-docs.md`](plugins/suwagent/hooks/context/mandatory-docs.md) | docs before code |

Fork the repository, change `working-with-user.md`, and install from your fork with
`/plugin marketplace add <you>/suwalski-agent-plugin`.

## Updates and removal

<details>
<summary>Auto-update, update now, disable, uninstall</summary>

Your installed copy is cached and does not change on its own.

| | |
| :- | :- |
| **Auto-update** | `/plugin` → **Marketplaces** → `suwalski-agent-plugin` → **Enable auto-update** (off by default for third-party marketplaces); the new version loads in the next session or after `/reload-plugins` |
| **Update now** | `/suwagent:update` runs the update commands for you; or `/plugin` → **Installed** → suwagent → **Update now**; or `claude plugin update suwagent@suwalski-agent-plugin` |
| **Turn off** | `claude plugin disable suwagent@suwalski-agent-plugin` |
| **Remove** | `claude plugin uninstall suwagent@suwalski-agent-plugin`; your pages in `docs/visual/` stay |

`plugin.json` has no `version` on purpose, so every pushed commit is a new version.
Plugins installed on your machine are not loaded in cloud sessions (claude.ai/code).

</details>

## Troubleshooting

<details>
<summary>Common problems</summary>

| Symptom | Fix |
| :- | :- |
| `/suwagent:` skills don't show up | `/reload-plugins`; if still missing, see the **Errors** tab in `/plugin` |
| No spec offers or status line | check **Configure options**, then start a new session (the hook runs at session start) |
| Diagrams show as source text | the page couldn't reach the Mermaid CDN (offline or blocked) |
| limit-guard says `UNKNOWN` | run `/suwagent:limit-guard setup` once; until then the agent works without the guard |
| A page looks broken | `python3 plugins/suwagent/scripts/vdoc.py check <page.html>` lists what is wrong |

</details>

## Develop

<details>
<summary>Commands and repository layout</summary>

```bash
claude --plugin-dir ./plugins/suwagent        # try local changes without installing
claude plugin validate .                      # check the marketplace and the plugin
python3 plugins/suwagent/scripts/vdoc.py check docs/visual/recap/2026-10-25-suwagent-plugin.html
python3 plugins/suwagent/scripts/vdoc.py render docs/visual/board/readme.html   # redraw the README pictures
```

After editing the plugin in a running session, run `/reload-plugins`.

```
.claude-plugin/marketplace.json     the catalog: lists the plugins in this repository
plugins/suwagent/
  .claude-plugin/plugin.json        manifest: name, description, userConfig
  skills/visual-{spec,plan,recap}/  the visual document skills (SKILL.md each)
  skills/visual-readme/             the README told in pictures, from a board page
  skills/mandatory-docs/            docs-before-code procedure
  skills/autopilot/ orchestrate/ plan-judge/ limit-guard/   ways of working
  skills/efficient-frontier/        alias of orchestrate
  skills/update/                    updates the installed plugin
  shared/template.html              the page: CSS + JS that render every block
  shared/authoring.md               rules shared by the visual skills
  shared/components.md              the block catalog (HTML snippets)
  scripts/vdoc.py                   new / check / open / links / register / refresh / shot / render
  scripts/limits.py                 status line tap and usage check for limit-guard
  scripts/session-context.sh        prints the working agreement, part by part
  hooks/hooks.json                  SessionStart → scripts/session-context.sh
  hooks/context/*.md                the working agreement
docs/visual/                        visual documents of this repository (a real recap example)
docs/visual/board/readme.html       the source of the README pictures → img/readme/<panel>-light/dark.png
```

To change a README picture, edit its section in `docs/visual/board/readme.html` and run the
`render` command above (Firefox or Chrome; `--only <id>` redraws one).

A `CLAUDE.md` inside a plugin is **not** loaded: always-on instructions go in a hook like the one
above, and instructions for a task go in a skill.

</details>

## Credits

Inspired by [BuilderIO/skills](https://github.com/BuilderIO/skills) (MIT, © Builder.io):
`/visual-plan` and `/visual-recap` gave the idea for the visual documents, and the status line
and `mandatory-docs`, `autopilot`, `plan-judge`, `orchestrate` and `limit-guard` are adapted from
their `quick-recap`, `read-the-damn-docs`, `plow-ahead`, `plan-arbiter`, `efficient-frontier` and
`stay-within-limits`. Their visual skills need Builder's hosted Plans app; suwagent writes plain
HTML into the repository and publishes it as a claude.ai artifact, or keeps it local.

[MIT](LICENSE) © 2026 Piotr Gugnowski
