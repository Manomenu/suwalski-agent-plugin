---
name: orchestrate
description: Run a large task as an orchestrator. The session's own expensive model keeps planning, decisions, integration and final review, and hands token-heavy work (repository scans, docs extraction, test runs, log reduction, bounded code edits) to cheaper parallel subagents with precise hand-off packets. Use for big, parallelizable work where the main model would otherwise spend most of its tokens reading and running things. Start it only when the user explicitly asks for it (by name or by plain words), never on your own initiative.
argument-hint: "[the task to run as an orchestrator]"
---

# Orchestrate

Spend the expensive model on judgment, and cheaper subagents on volume. The main model
decides what to do, splits the work, checks the evidence and integrates. Subagents read,
search, run and make bounded edits, then report back compactly.

Task: $ARGUMENTS

## 1. Split the work

- **Keep with the main model**: understanding the goal, architecture and trade-offs,
  resolving ambiguity, choosing between conflicting findings, integrating changes, and the
  final review.
- **Delegate**: broad repository scans and inventories, extracting facts from long docs,
  running test suites and browser checks, reducing logs, clustering test failures, and
  bounded edits in files no other agent touches.
- **Don't delegate** the immediate blocker your next step depends on. Do it yourself.

## 2. Pick the model per slice

Use the Agent tool's `model` option. Choose the cheapest model that can do the slice well:

| Slice | Model |
| :- | :- |
| search, inventory, log or output reduction, docs extraction | `haiku` |
| bounded code edits, writing tests, running and diagnosing tests | `sonnet` |
| a slice that needs real design judgment | keep it in the main session |

## 3. Write hand-off packets

Each subagent starts cold, so its prompt has to stand alone:

- the repository path and the exact objective;
- what is in scope (files, packages, surfaces) and what is explicitly out of scope;
- the commands that verify the work, and what success looks like;
- the return format: findings with file:line, changed files, commands run with results,
  open uncertainties, and what the main model must decide;
- the stop conditions: the code doesn't match the packet's assumptions, a command fails
  twice after a reasonable fix, or the work needs files outside the scope. In any of these
  cases, stop and report rather than improvise.

## 4. Run in waves

- At most **3 subagents in parallel** per wave, unless the user sets another number.
- Never let two agents edit the same files at once. Give editing agents disjoint files, or
  `isolation: "worktree"`.
- Between waves, apply the `limit-guard` skill when the work is long.

## 5. Review before you believe

Treat subagent reports as leads, not verdicts. Before building on a high-impact finding or
declaring the task done, reopen the cited files, re-run the verification that matters, and
review the final change as a whole. Resolve disagreements between subagents yourself.

## Finish

Report like any task under the working agreement: for a larger change, offer (or, under
autopilot, write) the visual recap, and end with the status line. Mention in one line how
the work was split: how many subagents, on which models.
