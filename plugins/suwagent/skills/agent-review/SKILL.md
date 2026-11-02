---
name: agent-review
description: Review a finished change at diff level as a separate reviewer, never as its author. A subagent with a clean context reads the diff of the branch, merge request or working tree together with the spec and the guardrails page, and reports what is wrong in the code (bugs, unhandled edge cases, duplicated logic, needless complexity, security slips, and anything the diff does beyond the spec), each with file:line and a severity. The result is a one-off page in docs/visual/review/, valid until the merge request closes, which the human reads instead of the diff on the ordinary review path. It never re-judges the spec or the concept: that is the human's job on the spec and the guardrails page.
when_to_use: A change is ready for review and the human will not read the diff; or the user says "agent-review", "zrób review diffu", "niech agent przejrzy kod", "review kodu".
argument-hint: "[branch | base...head | MR number | empty for the working tree]"
---

# Agent review

The human reads the spec and the guardrails page; this page is what reads the diff for
them. It has one job, the code, and it is written by a reviewer that did not write the code.

Before writing, read:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Table",
  "Callouts", "Code with notes" and "Open questions"

Publishing mode: **${user_config.publish_mode}** (`artifact` or `local`; see authoring.md;
a placeholder here means `artifact`).

What to review: $ARGUMENTS (if empty, the current branch against its base, or the working
tree when the branch has no commits of its own).

## Rules

- **A separate reviewer.** The review runs in a subagent with a clean context (the Agent
  tool, general-purpose, a different model from the author when one is available), never in
  the session that wrote the code. Give it the diff, the spec, the guardrails page and the
  rules below, and build the page from its report. If this session wrote nothing of the
  change, it may review directly, and the page says so.
- **Diff level only.** The reviewer judges the code: correctness, edge cases the spec names,
  duplicated logic, complexity a reader would stumble on, security (input handling, secrets,
  permissions), and **scope**: anything the diff does that no criterion asks for. It does not
  judge whether the spec is right, whether the feature should exist, or whether the
  architecture is the best one; those belong to the human reading the spec.
- **Evidence.** Every finding has `file:line`, what is wrong in one sentence, how it fails
  (an input or a state and the wrong result), and a severity: `blocker` (wrong result or data
  loss), `should fix` (a real defect with a workaround), `nit` (clarity). No finding without a
  failure scenario; style alone is a nit at most.
- **Read-only.** The reviewer changes nothing. Fixing is the author's next step.
- **The spec's slug.** Create the page with the slug of the living spec the change belongs to
  (`vdoc.py new review <spec-slug>`), so `links` finds the spec. A review page of an earlier
  merge request of the same feature may still be on disk (the folder is gitignored): start
  over with `--force`; a review is never carried from one merge request to the next.

## Sections, in order

1. **Header**, `doc-kind` "Review", status `done`, the branch and commit in the meta line,
   the nav links `vdoc.py links` prints, and one line saying who reviewed (a subagent with a
   clean context, and its model when known).
2. `tldr`: 🟢 (nothing above nit), 🟡 (should-fix findings) or 🔴 (a blocker), the counts per
   severity, and in one sentence whether the diff stays inside the spec.
3. `findings`: one `<h3>` per finding, worst first: severity `tag`, `file:line`, what is wrong,
   the failure scenario, and the fix in one sentence. A `Code with notes` block only when a
   few lines make the finding clearer than words.
4. `scope`: what the diff does beyond the spec's criteria, if anything, as a `table`
   (what · where · keep or drop, recommended).
5. `questions`: one fieldset with a checkbox per finding, blockers and should-fix marked
   `data-recommended`, so the user picks what the author fixes now.

No diffs on the page beyond the `Code with notes` blocks: `file:line` is the reference.

## After the user decides

The chosen findings are the author's work: fix them, run the gate once over all of them,
and republish the recap if one exists. This page is a working page of one merge request:
it stays out of git (`docs/visual/review/` in `.gitignore`) and is not updated after the
merge.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR and the counts, and say what the user decides (which findings the author fixes).
