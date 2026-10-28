---
name: visual-deviation
description: Show only where an implementation departs from its spec (and plan), as a short visual HTML page instead of a full recap. Each deviation gets what the spec promised, what was built, why it differs, what it changes for users or callers, and a recommendation (keep it and update the spec, fix the code, or decide). Things built that no spec asked for and promises left unfinished count too; what matches the spec is only counted, not described. Use when a spec or plan exists for the work and the user wants the differences, not the whole story.
when_to_use: The user asks how the implementation differs from the spec or plan, or says "visual deviation", "deviation", "odstępstwa", "czym się różni od specyfikacji", "co zrobiłeś inaczej niż w specu", "rozbieżności"; or a full recap is more than the user needs and a spec or plan for the work exists.
argument-hint: "[branch | base...head | PR number | commit]"
---

# Visual deviation

A deviation page answers one question: **where does what was built differ from what was
agreed, and why?** It is the part of a recap a reviewer who already knows the spec actually
needs. What matches the spec is a number in the TL;DR, nothing more. Everything that
differs (changed, dropped, unfinished, or added without being asked) gets its own entry with
the reason. The page reports and doesn't defend: a deviation without a good reason is shown
as one.

Before writing, read these two files. They hold the rules shared by the visual skills and
the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Side-by-side
  comparison", "Callouts", "Tags" and "Open questions"

Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

What to compare: $ARGUMENTS

## Scope

- **The baseline is the spec**, then the plan. Find them in `docs/visual/spec/` and
  `docs/visual/plan/`, matched by the conversation or the slug, and create the page with the
  **same slug**. A spec or plan given as a path, an artifact link or text in the conversation
  works too. Read the spec's goals, behaviour, scenarios, UI, data and acceptance criteria,
  and the plan's approach, decisions, file map and steps.
- **No spec and no plan: stop.** Say in one line that there is nothing to compare against,
  and suggest `/suwagent:visual-recap` instead. Never reconstruct a spec from the code and
  then compare the code with it.
- **The implementation** is chosen as in visual-recap: with no argument, everything changed
  on the current branch since it left the base branch (`git merge-base HEAD main`, or
  `master`/the project's base), plus uncommitted changes; a PR number via `gh pr diff <n>`
  and `gh pr view <n>`; a range or commit as given. Exclude `docs/visual/**`.

## Find the deviations, once

Go through the baseline item by item and check each against the code (and the tests, and the
running app when the item is about UI). Then go through the changed files and find what no
item asked for. Every difference becomes one entry with:

- **kind**: `changed` (built differently), `dropped` (not built, on purpose), `partial`
  (started, not finished), `added` (built without being in the spec or plan);
- **source**: which item of the spec or plan it departs from (a criterion, a scenario, a plan
  step or decision), named the way that document names it;
- **promised / built**: both in plain words, at the level of behaviour, not code;
- **why**: from this conversation, commit messages, code comments or the decision log of an
  autopilot run. If no reason can be found, write that the reason is unknown in a
  `callout assumption`, and never invent one;
- **impact**: what it changes for a user, a caller, the data or compatibility, and whether an
  acceptance criterion now fails;
- **recommendation**: `keep` (the deviation is better; update the spec), `fix` (change the code
  to match the spec), or `decide` (a real trade-off that is the user's call).

Leave out what doesn't change behaviour or a decision: a renamed private helper, a file split
differently than the plan's file map, a step done in another order. A plan detail counts only
when the plan made it a decision.

**Evidence, not memory.** "Built" is what the code and the test runs show now, not what was
intended. A `fail` on a criterion needs the test, command or `file:line` that shows it.

## Sections, in order

Keep it to 2-4 minutes of reading. Leave out a section that has nothing to say.

**No deviations: no page.** Say in one line that the implementation matches the spec, with
the count (e.g. "12/12 criteria as specified") and the evidence, and offer a full recap.

1. **Header**, `doc-kind` "Deviation" ("Odstępstwa" in Polish), status `done` (or `draft`
   if work on the branch continues), the branch and range in the meta line, and the nav
   links `vdoc.py links` prints (the spec and plan).
2. `tldr`: 2-3 sentences with 🟢 (none that matter, or all of them recommended `keep`), 🟡
   (some need the user's decision) or 🔴 (an acceptance criterion fails or a promise to users
   is broken) at the start. `stats`: criteria as specified (e.g. 9/12), deviations, how many
   need a decision.
3. `deviations`: a summary `table` first (# · item of the spec or plan · kind · impact ·
   recommendation, with `tag`s for kind and recommendation), worst first. Then, per
   deviation, an `<h3>` with its number and name, a `cols` of **Spec/Plan** vs **Built** (the
   built side marked `chosen` only when the recommendation is `keep`), the why as a
   `callout decision` (or `callout assumption` when the reason is unknown), and the impact.
   Add a Mermaid diagram only when a deviation changes a flow or structure: planned vs built
   in `cols`.
4. `added`: what was built without being asked, one row each with why, in a `table`. Keep
   this apart from `deviations`, so that scope creep is visible as such.
5. `unfinished`: `dropped` and `partial` items as a `checks` list with `data-status`
   (`skipped`, `partial`, `fail`) and `evidence`, each saying what is missing.
6. `questions`: one fieldset per `decide` entry (and per `keep` that changes a promise to
   users), with the options keep-and-update-spec / fix-the-code and the recommended one
   marked.

No code and no diffs: `file:line` as a reference only, as in a recap.

## After the user decides

For every one they want fixed, the work goes back to implementation.

The deviations the user keeps go into the **final spec**: once the task is finished, rewrite
the spec so that it reads as if it had assumed them from the start. No "changed from" notes,
no history, no link to this page: a reader of the spec should not be able to tell what was
planned differently. Show the rewritten spec through the review loop in authoring.md. The
final spec is the only page of the task that is committed; this page, like the plan, recap
and QA page, is a working page and stays out of git.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR, and say what's needed from the user (decisions on deviations, or nothing).
