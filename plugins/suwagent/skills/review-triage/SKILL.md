---
name: review-triage
description: Tell a reviewer which of the two review paths a finished change takes and what to read. Checks the change (the branch, a merge request or the working tree) against the project's always-careful list (login and permissions, payments, data migrations, code without characterization tests, and whatever the project's AGENTS.md adds), and answers in chat: the path, the reason, and the reading list: the review-spec page (or the spec), the guardrails page and the recap on the ordinary path, plus the diff, and where in it, on the careful path. Use when a change is ready for review or the user asks what to look at.
when_to_use: A branch or merge request is ready for review, or the user asks "co mam przejrzeć", "którą ścieżką", "review-triage", "czy muszę czytać diff".
argument-hint: "[branch | base...head | MR number | empty for the working tree]"
---

# Review triage

Two paths, not a ladder. On both, the human reads the spec and the guardrails page and never
judges guardrails by reading test code. The difference is the diff.

| Path | Human reads | Diff read by | When |
| :- | :- | :- | :- |
| **ordinary** | the review-spec page (the spec when the task changed none), the guardrails page, the recap | a reviewing agent in its own session (`/suwagent:agent-review`) | everything not on the list |
| **careful** | the same, plus the diff, in the places this skill names | the human and the reviewing agent | the change touches the always-careful list |

## The always-careful list

Default, for every project: **login and permissions, payments and billing, data migrations,
code without characterization tests** (in a project that took over legacy code). The project's
AGENTS.md may add or drop items in a section named "Review" or "Always careful"; read it first.
The list is short on purpose. It changes after incidents, by a person, not by metrics.

## What to do

Read-only. Change nothing.

1. Take the change: $ARGUMENTS, or the current branch against its base, or the working tree.
   List the files it touches (`git diff --stat`), and the spec and guardrails page of the
   work when they exist (`docs/visual/spec/`, `docs/visual/guardrails/`, same slug).
2. Match the touched files and the spec's criteria against the list. A file under an auth,
   payment or migration folder, a changed migration script, a changed permission check, a
   touched legacy module with no recordings in the characterization folder: careful.
3. Answer in chat, in the user's language:
   - **Path** and the one reason (the list item it hit, or "nothing from the list").
   - **Read**: the review-spec page (if the task added or edited a spec and it is missing, say
     to run `/suwagent:visual-review-spec` first; the living spec is not a review link, because it
     also holds what other tasks added), the guardrails page (if it is missing, say to run
     `/suwagent:visual-guardrails` first), the recap or deviation page.
   - On the careful path, **where in the diff**: the files and functions that touched the
     list item, so the human reads those, not everything.
   - **Agent review**: whether `docs/visual/review/` already has this change's page; if not,
     suggest `/suwagent:agent-review` in one line.

Nothing is written; the answer is the triage. Do not start the agent review on your own.
