---
name: visual-recap
description: Explain finished work (the current branch, a commit range, a PR, or uncommitted changes) as a visual recap HTML page at a high level, without code or diffs. It covers what now exists, how it works (elements and their roles, a walkthrough of a real scenario, before/after behaviour, diagrams), the acceptance criteria checked against the spec/plan with evidence, deviations from the plan, verification results, and where a reviewer should look. Use after implementing a larger change, before review or merge, and when the user asks for a recap, a summary of changes, "co zrobiłeś", "podsumuj zmiany", "jak to zaimplementowałeś".
when_to_use: Work on a multi-file change has just been finished or a branch is ready for review; or the user says "visual recap", "recap", "podsumowanie", "pokaż co się zmieniło", "wyjaśnij implementację", "review this branch/PR".
argument-hint: "[branch | base...head | PR number | commit]"
---

# Visual recap

A recap explains finished work the way a colleague would at a whiteboard: what now exists,
how it works, and whether it does what was promised. The reader should understand the
implementation **without reading code**. There are no diffs and no code listings: you read
the code, and the page explains it in behaviour, roles, flows and pictures. The recap reports
and doesn't sell, so failures, gaps and shortcuts go in plainly.

Before writing, read these two files. They hold the rules shared by all three visual skills
and the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Elements and
  their roles" and "Walkthrough"


Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

What to recap: $ARGUMENTS

## Scope

- **No argument.** Recap the whole piece of work from this conversation: everything changed
  on the current branch since it left the base branch (`git merge-base HEAD main`, or
  `master`/the project's base), plus uncommitted changes. That includes later fixes and
  follow-ups, not only the last step. Leave out unrelated changes that were already there
  before the work started.
- **A PR number.** Use `gh pr diff <n>` and `gh pr view <n>`. **A range or commit.** Use it as
  given.
- Exclude `docs/visual/**` (the documents themselves).
- Find the spec and plan of this work in `docs/visual/spec/` and `docs/visual/plan/`, matched by
  the conversation or the slug. If they exist, create the recap with the **same slug** and read
  both: the recap is checked against them.

## Understand it, once

```bash
git diff --stat <base>...HEAD        # footprint
git log --oneline <base>..HEAD
git diff <base>...HEAD -- <file>     # read the files that carry the change
```

Read the change in one pass and take notes **at the level of behaviour**: which elements are
new or changed and what each is responsible for, how a request or piece of data now moves
through them, what a user sees differently, which decisions were made in the code, and what
is fragile. Then write from the notes.

**Verification is evidence, not memory.** Report what was run and its real result: the
commands from this conversation, or run the project's tests, type check and lint now if
that's cheap. Never mark a criterion `pass` without evidence. If something wasn't verified,
say so.

## Sections, in order

Leave out a section that has nothing to say. Skip the recap entirely (say so in one line) for
a tiny change that is clearer described in one sentence.

1. **Header**, `doc-kind` "Recap", status `done` (or `draft` if work remains), with the branch
   and range in the meta line.
2. `tldr`: what now exists and the verdict in 2-4 sentences, with a 🟢 (done and verified),
   🟡 (done, something pending) or 🔴 (broken or blocked) at the start. `stats`: elements
   added/changed, tests added, criteria met (e.g. 7/8).
3. `acceptance`: if a spec or plan exists, every acceptance criterion as a `checks` item,
   starting with the spec's id (`AC-<feature>-<n>`), with `data-status` and `evidence`. Without a spec, list what the change claims to do,
   with evidence.
4. `how`: **How it works**, the heart of the recap:
   - a Mermaid diagram of the structure or flow after the change, or a before/after pair in
     `cols` when the structure itself changed; a `sequenceDiagram` for a new request path;
     a `stateDiagram-v2` for new states;
   - **elements and their roles**: one card per new or substantially changed element, with
     its responsibility, inputs/outputs and what it talks to, in plain words;
   - a **walkthrough** of one or two real scenarios ("what happens when…") through those
     elements, including what happens on the main failure path.
5. `ui`: only if rendered UI changed. **Prefer real screenshots with numbered marks** (the
   "Screenshot with numbered marks" block) over diagrams here: they show the reader where on
   the screen each change is. Shoot the running app with `vdoc.py shot` (or a browser tool
   of this session): the entry point, the changed interaction and the resulting state, and
   the before state too when you can still reach it (the base branch, or a deployed
   version). Frame every changed element, number it, and explain it in the legend. Fall back
   to before/after wireframes, grounded in the components and labels in the code, only when
   the app can't be run here, and then mark them as reconstructed from code.
6. `data`: only if a schema, API or file format changed. The new shape as a table or an
   `erDiagram`, and what stays compatible.
6b. `decisions`: only when the work ran under autopilot. **Decisions made without you**: a
   `table` of every decision from the decision log (question, choice, why, how hard to
   undo), the hard-to-undo ones first.
7. `deviations`: only if the work departed from the plan: planned vs done in `cols` or a
   table, each with why.
8. `files`: the `files` map, grouped by area (`li.dir`), with `data-change`, a one-line
   `why` and `stat` from `--stat`. For a large change, put it in `<details>`.
9. `verification`: the commands run and their results (a `callout ok`, or `risk` for
   failures), plus a short excerpt of the output in `<details>` if it helps.
10. `review`: **Where to look carefully**. The 2-5 places where a bug would hide: tricky
    logic, concurrency, security, a migration, a shortcut taken. Describe each in words
    (`file:line` as a reference, not a code excerpt) and say why it is risky.
11. `followups`: known gaps, TODOs left in the code, and suggested next steps.
12. `questions`: only if a decision is genuinely needed from the user.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR, and say what's needed from the user (review, merge approval, an answer).
