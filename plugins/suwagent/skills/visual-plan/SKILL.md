---
name: visual-plan
description: Write a visual implementation plan of HOW to build a change (approach and decisions, architecture diagram, file map, planned code shapes, ordered steps with checks, verification, risks, open questions) as an HTML page the user reviews and approves in the browser before any code is written. Use before implementing a larger or multi-file change, after a spec is approved, or when the user asks for a plan, "zaplanuj", "plan implementacji", or wants to turn an existing text plan into something reviewable.
when_to_use: The change touches several files, adds a feature, changes an API or data shape, or has more than one reasonable approach; or an approved spec.html exists for this work; or the user says "visual plan", "plan", "zaplanuj", "jak to zrobisz", "plan implementacji".
argument-hint: "[what to plan, or a path to spec.html / a text plan]"
---

# Visual plan

A plan says **how** the change gets built, concretely enough that the user can approve it, or
redirect it, before any code exists. It builds on an approved spec when one exists.

Before writing, read these two files. They hold the rules shared by all three visual skills
and the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → `open`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog

What to plan: $ARGUMENTS (if empty, use the change being discussed in the conversation).

## Inputs

- **A spec.** Look for `docs/visual/*/spec.html` for this work: the path in the arguments,
  the folder the conversation used, or the newest folder whose slug matches. If one exists,
  read it, write the plan in the same folder, link it in `doc-nav`, and plan to meet its
  acceptance criteria. Don't restate the spec; refer to it.
- **An existing text plan.** If one exists (pasted, a file, or a plan from plan mode), treat it
  as source material. Keep its facts and decisions, and rewrite it as a standalone plan
  document.
- **No spec, and the requirements are unclear.** Suggest `/suwagent:visual-spec` first, in one
  line. If the user wants the plan anyway, put the requirement gaps in Open questions.

## Rules

- **Read-only until approved.** Make no source changes while planning. The only file you
  write is the plan page. If the session is in plan mode, say that the page can be written
  once the user leaves plan mode, or present the plan through the normal plan-mode approval
  and offer the visual page right after.
- **Research first, and lead with reuse.** Read the real code. For each step, say what it
  reuses (existing functions, components, tables, helpers) before what it adds.
- **Decide the hard-to-reverse things explicitly**: data model, public IDs, API and wire
  formats, auth/ownership boundaries, migrations. Each gets a `callout decision` with its
  reason. Put alternatives you seriously weighed in `cols`, with the chosen one marked.
- **The smallest first cut.** State what's in, and what's deliberately deferred.
- **Steps keep the code working.** Order them so the build and the tests pass after each one.
  Each step names the files it touches and has a `done-when` check.
- **Verification exercises the real workflow**: the commands to run (tests, type check,
  build) and at least one end-to-end check that matches what a user does.

## Sections, in order

Leave out a section that has nothing to say.

1. **Header**, `doc-kind` "Plan", status `draft`, with `Zakres`/scope (≈ files, steps) in the
   meta line.
2. `tldr`: the approach in 2-4 sentences, plus `stats`: new files, modified files, steps, open
   questions.
3. `approach`: the key decisions (`callout decision`), the options weighed (`cols`), and the
   scope cut (in / deferred).
4. `architecture`: a Mermaid diagram of the parts and how data or control moves after the
   change. Use a before/after pair in `cols` when the structure itself changes. A
   `sequenceDiagram` when the order of calls is the point. Skip it for changes with no
   structure to show.
5. `files`: a `files` map of every file to add, change or delete, each with a `why`.
6. `code`: 2-5 load-bearing code shapes (new signatures, types, schema, config) as
   `x-code` blocks with notes on the lines that matter, grouped in `tabs` when there are
   several. Planned shapes and stubs, not full implementations.
7. `steps`: an ordered `steps` list (usually 3-8).
8. `verification`: the exact commands and the manual/end-to-end check. If a spec exists, map
   its acceptance criteria to how each will be checked (a `checks` list or a table).
9. `risks`: real risks, each with a mitigation or rollback. Include migration and
   backward-compatibility concerns where data or callers exist.
10. `questions`: the single Open questions form, each question with a recommended answer.

## Hand-off

Follow the hand-off step in authoring.md, and name the areas the work will touch. Presenting
the plan is the approval request, so don't also ask "does this look good?". After approval
(status `approved`), implement it, re-reading the plan page before each major step. If the
work has to depart from the plan, update the page first and say so in chat. When the
implementation is done and verified, suggest `/suwagent:visual-recap`.
