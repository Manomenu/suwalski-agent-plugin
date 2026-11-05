---
name: task-triage
description: Size a task before any spec, plan or code. Reads the task, the living specs in docs/visual/spec/ and the code it would touch, then proposes a tier (S: ticket plus a test with an id, M: a delta in the existing spec of the feature, L: a new spec and a plan), names the spec the task belongs to and the acceptance criteria it may change, and says what the next step is. The user confirms the tier in one word; nothing is written. Use at the start of every task whose size is not obvious, and when the user asks how big a change is or whether it needs a spec.
when_to_use: A task is starting and it is not obvious whether it needs a spec; or the user asks "czy to potrzebuje specki", "jaki to rozmiar", "task-triage", "triage", "S, M czy L".
argument-hint: "[the task, in plain words, or a ticket id]"
---

# Task triage

One task, one tier, before anything else. The tier decides how much of the workflow the task
gets, so nobody skips the spec silently and nobody writes a spec for a typo.

| Tier | When | What the task gets |
| :- | :- | :- |
| **S** | a bug, a typo, a change with no new behaviour visible to a user or to a caller of the API | a ticket and, where behaviour is guarded, a test naming the existing criterion's id; no spec |
| **M** | the behaviour of an existing feature changes, inside its contract | a delta in that feature's living spec: criteria added, changed or dropped; then build |
| **L** | a new feature, or a change of a contract on the boundary (an API record, an event, a file format) | `/suwagent:visual-spec` (new or heavily changed), then `/suwagent:visual-plan` |

The threshold between S and the rest is one question: **does it change behaviour a user or a
caller can see, or a contract?** Yes → M or L. No → S. The number of files does not decide:
a one-line fix can change behaviour, a 40-file rename changes none.

## What to read

Read-only. Change nothing.

1. The task: $ARGUMENTS (if empty, the task discussed in the conversation).
2. The living specs: `docs/visual/spec/*.html` (or the folder the project's AGENTS.md names).
   Match the task's domain words against the titles, the `tldr` and the acceptance criteria.
   The spec whose feature the task touches is the one that gets the delta.
3. The code the task would touch: enough to tell whether the change stays inside the
   feature's contract (M) or crosses a boundary (L). A project with `criteria.json` lists
   the guardrails of each criterion with `vdoc.py criteria`; use it to see which criteria the
   change can break.
4. The project's contract, when it has one (a generated `openapi.json`, an event schema):
   a task that changes it is L, even when the code change is small.

## Answer

In chat, short, in the user's language:

- **Tier** with one sentence of reason, tied to the threshold question.
- **Spec**: the living spec this belongs to (title and path), or "new feature", or "none (S)".
- **Criteria**: the ids the change may add, change or drop, when the spec exists.
- **Next step**: for S the ticket and the test to touch; for M and L `/suwagent:criteria-triage`,
  which routes each criterion, then the delta or `/suwagent:visual-spec`. When several tasks are
  pasted, one row each in a table.

Then wait for the user's word. "ok", "S", "M", "L" or a correction. Do not start the next
step on your own. When the user changes the tier, take their tier without arguing; say in
one line what that means for the next step.

## Edge cases

- The task touches two features: name both specs; the delta goes into each, or the task
  is split. Say which you recommend. Which criterion goes where is `/suwagent:criteria-triage`.
- No specs in the repository yet: tier by the threshold question alone, and say that an M
  becomes L (the first spec of the feature).
- A "small" change to code with no characterization tests in a brownfield project: still S
  by behaviour, but say that the first step is recording the behaviour it touches.
