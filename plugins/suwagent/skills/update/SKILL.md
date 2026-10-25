---
name: update
description: Update the installed suwagent plugin to the latest version on GitHub by running the Claude Code plugin update commands, and say what the user has to do for this session to use it. Start it only when the user explicitly asks for it (by name or by plain words), never on your own initiative.
allowed-tools:
  - Bash(claude plugin list)
  - Bash(claude plugin marketplace update suwalski-agent-plugin)
  - Bash(claude plugin update suwagent@suwalski-agent-plugin)
---

# Update suwagent

The installed copy of the plugin is cached and changes only when it is updated. Run these
commands in order (Claude Code docs: "Plugin commands reference", `plugin marketplace update`
and `plugin update`):

1. Note the installed version: the `Version:` line under `suwagent@suwalski-agent-plugin` in
   ```bash
   claude plugin list
   ```
2. Refresh the marketplace from GitHub:
   ```bash
   claude plugin marketplace update suwalski-agent-plugin
   ```
3. Update the plugin. The scope it is installed at is found by itself:
   ```bash
   claude plugin update suwagent@suwalski-agent-plugin
   ```
4. Run `claude plugin list` again and compare the version.

If a command fails, show its error and stop. Typical causes: no network or no access to
GitHub, or the plugin installed under another name (then `claude plugin list` shows the
right `name@marketplace`; use it).

Report in at most 3 lines: the version before and after, or that it was already the latest.
If it changed, tell the user to run **`/reload-plugins`** (or start a new session) to load
it in this session: the skill can't run that command itself. Mention once that
`/plugin` → **Marketplaces** → `suwalski-agent-plugin` → **Enable auto-update** makes this
automatic.
