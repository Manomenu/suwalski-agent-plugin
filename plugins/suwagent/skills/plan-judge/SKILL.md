---
name: plan-judge
description: Compare two or more competing plans for the same task (from different agents or models such as Claude and Codex, from different sessions, as visual plans, files or pasted text), check each against the real codebase, and choose one, merge the best parts, or send them back, publishing the result as a visual plan with a side-by-side comparison. Use when the user has several plans and wants one direction.
when_to_use: The user gives two or more plans, plan files, visual plan links, session transcripts or PR descriptions and asks which is better, to compare, merge or choose; or says "porównaj plany", "który plan lepszy", "plan-judge".
argument-hint: "[plans: paths, links or 'pasted above']"
---

# Plan judge

Turn competing plans into one executable direction. Keep the best ideas, reject weak
assumptions, and avoid blending everything into a compromise nobody chose. Judging is
read-only: change no code unless the user asks you to implement the winner afterwards.

Plans to judge: $ARGUMENTS

## 1. Collect

Gather every plan in full: pasted text, files, `docs/visual/plan/*.html`, artifact links (read
them with the Artifact tool), session transcripts, PR descriptions. If a plan can't be
found, continue with the rest and list the missing one as a risk.

## 2. Normalize

For each plan, extract the same fields, so the plans can be compared line by line:
objective and scope, key assumptions, files/APIs/data/UI it touches, the order of work,
verification, rollback or migration story, open questions, and rough cost. Don't reward
length: a short plan grounded in real code beats a long generic one.

## 3. Cross-check against reality

Check each plan's claims against the repository, the docs (follow mandatory-docs) and the
tests. Look for hidden dependencies, missing verification, risky ordering, vague steps,
scope creep, and hard-to-reverse decisions made implicitly. Note complementary strengths:
one plan may have the better architecture, another the safer migration. For large plans or
a wide codebase, check plans in parallel with subagents, one per plan.

## 4. Decide

Pick one outcome:

- **Adopt**: one plan, mostly as written.
- **Hybrid**: one plan as the base, plus named pieces from the others.
- **Revise**: every plan misses a key constraint or depends on an open decision. Say what
  it is, and stop there.

Tie-break in this order: fits the request → grounded in real code → simplest first cut that
doesn't block the future → better verification and rollback → cheaper to execute.

## 5. Publish the verdict as a visual plan

Follow the `visual-plan` skill's document rules (authoring.md, components.md, publishing
and `register`) with these additions. Put them right after the TL;DR:

- `comparison`, **Comparison of plans**:
  - a matrix `table`, with one row per criterion (fit, grounding, simplicity, verification,
    rollback, cost) and one column per plan, using ✓ / ~ / ✗ and a 2-5-word reason per cell;
  - the plans side by side in `cols`, the winner marked `chosen` and the others `rejected`,
    each with its one-line strength and its deciding weakness;
  - a `callout decision` with the verdict (Adopt / Hybrid / Revise) and the deciding
    evidence.
- `borrowed`: only for a hybrid. A list of each piece taken from a non-winning plan, and
  where it lands in the steps.
- `rejected`: ideas deliberately not taken, each with its reason.

The rest of the document is the chosen plan in standard visual-plan form (approach, files,
steps, verification, risks, open questions), so it can be approved and executed directly.
Its title is the work's name, not "Plan comparison".
