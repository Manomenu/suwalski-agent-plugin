---
name: limit-guard
description: Keep long-running or parallel agent work within the user's Claude plan usage limits (the 5-hour and the weekly window) by reading the real usage between steps or waves, and pausing new work at a threshold so the user keeps headroom for their own work. Used by autopilot and orchestrate between steps; also run it when the user asks how much of their limit is left, or to set up usage tracking.
when_to_use: Work under autopilot or orchestrate that lasts more than about an hour or runs subagents in parallel; or the user says "ile mam limitu", "check my usage", "limit-guard", "pilnuj limitów".
argument-hint: "[status | setup]"
---

# Limit guard

Claude Code already waits for a limit reset and continues an interrupted task by itself
when the limit is **hit**. This guard does something different: it **stops before** the
limit, so a long autonomous run doesn't burn the whole 5-hour or weekly window and leave the
user nothing for their own work.

The helper is `${CLAUDE_PLUGIN_ROOT}/scripts/limits.py`.

Request: $ARGUMENTS

## Where the numbers come from

Claude Code passes the plan's usage (`rate_limits.five_hour` and `rate_limits.seven_day`,
each with `used_percentage` and `resets_at`) only to the status line script, and only on
Pro/Max plans. Hooks and the agent don't receive them. So the guard relies on a small tap
in the status line, which saves those numbers to `~/.claude/suwagent/rate-limits.json`
every time the status line refreshes.

## Check

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/limits.py" status
```

The output is one of:

- `OK 5h 34% (resets 16:00) · 7d 52% (resets Thu 09:00)`: continue.
- `PAUSE …`: a window is at or above its threshold (default: **5h ≥ 90%** or
  **7d ≥ 95%**; pass `--max-5h` / `--max-7d` when the user has asked for other limits).
- `UNKNOWN …`: no snapshot, or one older than 15 minutes. The tap isn't set up, or the plan
  has no such limits (API key, Bedrock and so on). Say so once, and continue without the
  guard. Don't nag.

## When the answer is PAUSE

1. Let running subagents finish; interrupting them loses their work. Start nothing new.
2. Write a self-contained hand-off in chat: the remaining steps, the exact next action, the
   check-then-continue rule, and the thresholds.
3. Wait until the window that crossed its threshold resets (`resets_at` is in the status
   output). Use the session's way of waiting without spending tokens: a background
   `sleep <seconds>` (Bash with `run_in_background`, which notifies when it ends), or a
   wake-up tool if the session has one. For waits longer than an hour, chain waits and
   re-check after each.
4. On waking, run `status` again. Continue only on `OK`; trust the numbers, not the clock.

Tell the user in one line when you pause: which window, its percentage, and when work
resumes.

## Set up the tap (once, with the user's consent)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/limits.py" setup
```

It copies the helper to `~/.claude/suwagent/limits.py`, a path that doesn't change when the
plugin updates, and prints the `statusLine` setting to use. If the user already has a status
line command, it wraps that command, so their status line looks the same. Show the user
the change, then write it to `~/.claude/settings.json` only after they agree. The tap shows
up from the next status line refresh.
