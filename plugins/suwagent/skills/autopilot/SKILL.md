---
name: autopilot
description: Work through a task to the end without stopping for routine questions, turning ordinary ambiguity into recorded assumptions and decisions, stopping only for real blockers, and finishing with a visual recap that lists every decision made without the user. Run it when the user leaves the agent alone with a task.
disable-model-invocation: true
argument-hint: "[the task to finish]"
---

# Autopilot

The user is away and wants the task finished, not a list of questions. Keep moving: decide
what a sensible colleague would decide, write each decision down, verify as you go, and
leave a recap good enough that the user can audit every choice in five minutes.

Task: $ARGUMENTS

## What changes under autopilot

- **No routine questions.** Where you would ask "A or B?", pick the option that is smallest,
  reversible and closest to existing patterns, then **log it** (see Decision log) and keep
  going.
- **No approval gates.** The spec and plan approval steps of the working agreement are
  skipped. For a larger task, still think through a plan, and keep it in the decision log
  rather than waiting for sign-off.
- **The decision log replaces the conversation.** Everything the user would have been asked
  goes there, with the choice made and why.

## Hard stops: stop and ask only for these

- A secret, credential, account, paid service or private data is missing.
- The next step is destructive, irreversible, or touches production: deleting data, a
  migration on a real database, a deploy, a force push, rewriting history.
- **Merging, pushing or opening a PR.** Leave the work on its branch: the user approves
  merges themselves.
- The user explicitly reserved a decision for themselves.
- Legal, security or privacy risk that a conservative local choice can't reduce.
- The same verification fails again after a real investigation, and the next fix would be
  a guess.

When you stop, leave a self-contained hand-off in chat: what's done, what blocks, the exact
input needed, and the next command or file to look at.

## Decision rules

1. Reuse what the codebase already does before inventing anything.
2. Prefer local, reversible changes with a small blast radius.
3. Keep scope to what was asked. Note ideas for later in the recap; don't build them.
4. Correctness and readability over cleverness.
5. Verify with the smallest meaningful check first, and widen it only when risk justifies it.
6. Between two close options, pick the one easier to explain later.

## Work loop

1. Pin the goal and its acceptance criteria. Write them at the top of the decision log.
2. Read the real code, docs and tests before changing anything. Follow mandatory-docs for
   external libraries and APIs.
3. Work in small coherent steps on a feature branch (follow the user's and the project's
   branch conventions), committing at stable points.
4. After each step, run the relevant check and fix what it finds.
5. For work longer than about an hour, or with parallel subagents, apply the `limit-guard`
   skill between steps.
6. Repeat until the acceptance criteria are met or a hard stop applies.
7. Review the whole change against the original task before finishing.

## Decision log

Keep it as you go, in a scratch file (not in the repository) or in your notes. Each entry
has the question you would have asked, the choice made, why, and how easy it is to undo:

```
- Separator CSV: wybrano średnik (Excel PL otwiera bez importu). Odwracalne: 1 stała w export.ts.
```

## Finish

Write a visual recap with the `visual-recap` skill without asking first, because the user
expects it. It adds a **Decisions made without you** section (role `decisions`): a table of
every logged decision with its reason and how hard it is to undo, the risky ones first. End
the chat message with the recap link and the status line.
