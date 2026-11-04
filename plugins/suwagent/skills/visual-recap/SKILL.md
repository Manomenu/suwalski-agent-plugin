---
name: visual-recap
description: Explain finished work (the current branch, a commit range, a PR, or uncommitted changes) to its reviewer as a visual recap HTML page at a high level, without code or diffs. It covers what now exists, how it works (elements and their roles, a walkthrough of a real scenario, and where they help class and sequence diagrams of the real types), the acceptance criteria with the check that guards each, deviations from the spec while they are undecided, and where a reviewer should look. Use after implementing a larger change, before review or merge, and when the user asks for a recap, a summary of changes, "co zrobiłeś", "podsumuj zmiany", "jak to zaimplementowałeś".
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

## Who reads it

The reader is the reviewer of the change. When a spec exists, the reader knows it: refer to
its criteria by id and to the spec instead of repeating its requirements, but write every
sentence so it is understood on its own. When there is no spec, the recap stands alone.
Never assume the reader knows the plan: no "step 3 of the plan", no plan vocabulary the recap
doesn't explain. Write in the language of the conversation.

Where a picture explains something better than text or a table (a structure, a flow, how a
check works), draw it; otherwise a sentence is enough.

## Sections, in order

Leave out a section that has nothing to say. Skip the recap entirely (say so in one line) for
a tiny change that is clearer described in one sentence.

1. **Header**, `doc-kind` "Recap", status `done` (or `draft` if work remains), with the branch
   and range in the meta line.
2. `tldr`: what now exists and the verdict in 1-3 sentences, with a 🟢 (done and verified),
   🟡 (done, something pending) or 🔴 (broken or blocked) at the start. If something was not
   run or does not pass, say it here in one sentence.
3. `how`: **How it works**: the new or changed elements and their roles, and a walkthrough of
   one real scenario through them, including the main failure path. Recommended when they
   carry meaning for this change, never drawn for their own sake:
   - a Mermaid `classDiagram` of the real types from the diff (their names as in the code)
     and how they use each other;
   - a `sequenceDiagram` of one real call through those types;
   - a `stateDiagram-v2` for new states, a before/after pair in `cols` when the structure
     itself changed.
4. `acceptance`: if a spec exists, every acceptance criterion as a `checks` item, starting
   with its id (`AC-<feature>-<n>`), with `data-status` and `evidence`: the test or check that
   guards it, with its repository-relative path and line (`tests/export/test_csv.py:42`).
   Explain how that check keeps the criterion true: what it sets up, what it asserts, and what
   break turns it red. A criterion with no check that guards it says so. Without a spec, list
   what the change claims to do, with evidence.
5. `deviations`: **only while undecided**. Each place the work departs from the spec: what
   the spec says, what was built, and a recommendation (keep it and update the spec, or fix
   the code). The section is temporary: once the user decides, an accepted deviation goes
   into the spec and a rejected one into the code, and the section is removed.
6. `review`: **Where to look carefully**. The 2-4 places where a bug would hide: tricky logic,
   concurrency, security, a migration, a shortcut taken. Describe each in words (`file:line`
   as a reference, not a code excerpt) and say why it is risky.

Only when the user asks for them: `stats` (counts of elements, tests, criteria) and `files`
(the `files` map grouped by area).

## UI changes

When rendered UI changed, add a `ui` section after `how`. **Prefer real screenshots with
numbered marks** (the "Screenshot with numbered marks" block): shoot the running app with
`vdoc.py shot` (or a browser tool of this session), the before state too when you can still
reach it, frame and number every changed element, and explain it in the legend. Fall back to
before/after wireframes, grounded in the code, only when the app can't be run here, and then
mark them as reconstructed from code.

## Autopilot

When the work ran under autopilot, add a `decisions` section before `review`: a `table` of
every decision from the decision log (question, choice, why, how hard to undo), the
hard-to-undo ones first.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR, and say what's needed from the user (review, merge approval, an answer).
