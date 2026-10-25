---
name: visual-recap
description: Turn finished work (the current branch, a commit range, a PR, or uncommitted changes) into a visual recap HTML page that explains what was built and how it works: outcome, acceptance criteria checked against the spec/plan with evidence, deviations from the plan, architecture diagram, file map with stats, annotated key diffs, verification results, and where to review carefully. Use after implementing a larger change, before review or merge, and when the user asks for a recap, summary of changes, "co zrobiłeś", "podsumuj zmiany", "jak to zaimplementowałeś".
when_to_use: Work on a multi-file change has just been finished or a branch is ready for review; or the user says "visual recap", "recap", "podsumowanie", "pokaż co się zmieniło", "wyjaśnij implementację", "review this branch/PR".
argument-hint: "[branch | base...head | PR number | commit]"
---

# Visual recap

A recap explains finished work at a higher altitude than the diff. The user should come away
knowing what now exists, how it works, whether it does what the spec/plan promised, and which
lines deserve a careful look. It reports; it doesn't sell. Failures, gaps and shortcuts go in
plainly.

Before writing, read these two files. They hold the rules shared by all three visual skills
and the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `fill-diffs` → `check` → `open`), the review loop, and the
  quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Diff with
  notes"

What to recap: $ARGUMENTS

## Scope

- **No argument.** Recap the whole piece of work from this conversation: everything changed
  on the current branch since it left the base branch (`git merge-base HEAD main`, or
  `master`/the project's base), plus uncommitted changes. That includes later fixes and
  follow-ups, not only the last step. Leave out unrelated changes that were already there
  before the work started.
- **A PR number.** Use `gh pr diff <n>` and `gh pr view <n>`. **A range or commit.** Use it as
  given.
- Exclude `docs/visual/**` (the documents themselves) from the file map and the diffs.
- Find the spec and plan of this work (`docs/visual/*/spec.html`, `plan.html`, matched by the
  conversation or the slug). If they exist, put the recap in the same folder and read both:
  the recap is checked against them.

## Gather, once

```bash
git diff --stat <base>...HEAD        # footprint
git diff <base>...HEAD -- <file>     # for each file worth reading
git log --oneline <base>..HEAD
```

Read the diff in one pass and take notes: the shape of the change, the load-bearing hunks
(and their new line numbers), anything surprising. Then write from the notes; don't re-read
the whole diff. For uncommitted work, diff against the working tree (`git diff <base> --
<file>`).

**Verification is evidence, not memory.** Report what was run and its real result: the
commands from this conversation, or run the project's tests, type check and lint now if
that's cheap. Never mark a criterion `pass` without evidence. If something wasn't verified,
say so.

## Sections, in order

Leave out a section that has nothing to say. Skip the recap entirely (say so in one line) for
a tiny change that is clearer as a plain diff.

1. **Header**, `doc-kind` "Recap", status `done` (or `draft` if work remains), with the branch
   and range in the meta line.
2. `tldr`: what now exists and the verdict in 2-4 sentences, with a 🟢 (done and verified),
   🟡 (done, something pending) or 🔴 (broken or blocked) at the start. `stats`: files
   changed, +/− lines, tests added, criteria met (e.g. 7/8).
3. `acceptance`: if a spec or plan exists, every acceptance criterion as a `checks` item
   with `data-status` and `evidence`. Without a spec, list what the change claims to do,
   with evidence.
4. `deviations`: only if the work departed from the plan: planned vs done in `cols` or a
   table, each with why.
5. `architecture`: how it works now. A Mermaid diagram of the new flow or structure; a
   before/after pair when the structure changed; a `sequenceDiagram` for a new request path.
6. `ui`: only if rendered UI changed. Before/after wireframes of the entry point, the changed
   interaction and the resulting state, grounded in the components and labels in the diff.
   Mark them as reconstructed from code when they weren't captured.
7. `data`: only if a schema, API or file format changed. The new shape and what's compatible.
8. `files`: the full `files` map with `data-change`, a `why` and `stat` from `--stat`.
9. `changes`: **Key changes**. 3-8 `x-diff` blocks with `data-git`, one per load-bearing
   file, in `tabs`. Each has a `data-summary` and 1-4 notes on the hunks that carry the
   change. Keep each under ~150 lines (narrow with a path or `-U2`). Run `vdoc.py
   fill-diffs`, read the filled hunks, and set note line numbers from them.
10. `verification`: the commands run and their results (a `callout ok`, or `risk` for
    failures), plus a short excerpt of the output in `<details>`.
11. `review`: **Where to look carefully**. The 2-5 places where a bug would hide: tricky
    logic, concurrency, security, a migration, a shortcut taken. Each as `file:line` + why.
12. `followups`: known gaps, TODOs left in the code, and suggested next steps.
13. `questions`: only if a decision is genuinely needed from the user.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR, and say what's needed from the user (review, merge approval, an answer).
