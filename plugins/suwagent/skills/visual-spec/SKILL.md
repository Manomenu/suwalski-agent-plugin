---
name: visual-spec
description: Write a visual specification of WHAT to build and WHY (problem, goals, scenarios, behaviour, UI sketches, acceptance criteria, open questions) as an HTML page the user reviews and approves in the browser, before any plan or code. Use before a larger change, a new feature, or any change of behaviour whose requirements are not yet pinned down, and when the user asks for a spec, specification, requirements, "spisz wymagania" or "zrób specyfikację".
when_to_use: The user describes a feature or change in a few sentences and the details (edge cases, scope, UX, data) are still open; or the user says "visual spec", "spec", "specyfikacja", "wymagania", "co dokładnie ma robić".
argument-hint: "[what to specify]"
---

# Visual spec

A spec settles **what** the change does and **why**, so the user can approve it before anyone
plans **how**. It says nothing about files or functions to change. That belongs in
`/visual-plan`, which builds on the approved spec.

Before writing, read these two files. They hold the rules shared by all three visual skills
and the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog


Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

What to specify: $ARGUMENTS (if empty, use the change being discussed in the conversation).

## Rules

- **Read-only.** Make no source changes while specifying. The only file you write is the
  spec page.
- **Research first.** Read the code involved so the "current state" is real: today's
  behaviour, screens, data and limits, with paths. Delegate wide exploration to a subagent
  if it's large.
- **Ask little, up front.** Ask a clarifying question in chat only when the answer changes the
  whole shape of the spec (up to 3, batched). Everything else goes in as a recommended
  default in the Open questions form.
- **Specify the behaviour, not the code.** Talk about users, inputs, outputs, states, rules and
  limits. Mention a component or endpoint only where it is part of the contract (a public
  API, a file format, a database shape that others depend on).
- **Acceptance criteria are the contract.** Each one is observable and checkable (a user
  action and the visible result, or an input and its output), concrete enough that
  `/visual-recap` can later mark it pass or fail with evidence.

## Sections, in order

Leave out a section that has nothing to say. Never write one that only says "N/A".

1. **Header** (see authoring.md), `doc-kind` "Spec", status `draft`.
2. `tldr`: 2-4 sentences: the change, who it's for, and why now. Add `stats` only if the counts
   help (scenarios, criteria, open questions).
3. `problem`: today's state, grounded in the code (what happens now, with a real example),
   and the pain it causes. A small diagram of the current flow, if it's a flow.
4. `goals`: **Goals** and **Non-goals** as two `cols`. Non-goals are things a reader might
   reasonably expect but that are explicitly out.
5. `scenarios`: 2-5 concrete scenarios. Each names a real user and real data, then gives the
   steps and the outcome. The first scenario is the main happy path.
6. `behaviour`: rules and flow. A Mermaid `flowchart` or `stateDiagram-v2` when there are
   branches or states, plus a table of edge cases (situation → expected behaviour): empty, too
   large, no permission, concurrent edit, network failure, invalid input.
7. `ui`: only if something visible changes. Wireframes: before/after of the entry point, and
   one per new state (empty, loading, error, success). Real labels in the user's language.
8. `data`: only if a contract changes: a new field, an API, a file format, an event. An
   `erDiagram` or a table of fields with types and meaning.
9. `acceptance`: a `checks` list without statuses, 4-12 items.
10. `risks`: real risks and assumptions (`callout risk` / `callout assumption`). Include
    rollout and migration concerns if users or data are affected.
11. `questions`: the single Open questions form, each question with a recommended answer.

## Hand-off

Follow the hand-off step in authoring.md. End by asking the user to review the page and
comment on it or paste the feedback. Once the spec is approved (status `approved`), suggest
`/suwagent:visual-plan` as the next step. Don't start planning or coding before that.
