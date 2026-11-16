---
name: spec-review
description: Review a spec (a new one, or a task's edit of a living one) against the user's own checklist of what a good spec is, before it is approved or merged. Answers, one check at a time: should this spec exist at all, or should its criteria be edits of existing specs; are the guardrails that realise its acceptance criteria fast, and where one is slow, is the criterion worth that cost; is the spec's text redundant, describing in prose what an acceptance criterion already says or should say. Read-only; the answer is a short verdict per check in chat. The checklist lives in this file and grows as the user adds checks.
when_to_use: A spec or a delta is written and waits for approval, or a change that added or edited a spec is about to be merged; or the user says "spec-review", "przejrzyj speckę", "sprawdź speckę", "czy ta specka ma sens", "czy ta specka powinna powstać".
argument-hint: "[spec path | task branch | empty for the specs the working tree changed]"
---

# Spec review

A spec is reviewed by its content, not its diff. `/suwagent:visual-review-spec` shows a reviewer
*what* changed; this skill says whether what changed is a good spec. The checks below are the
user's own list: run all of them, in order, and add none of your own unless asked.

## What to read

Read-only. Change nothing.

1. The spec under review: $ARGUMENTS, or the specs under `docs/visual/spec/` that the branch or
   the working tree created or edited (`git diff --name-only` against the merge-base). For an
   edited spec, review only what the task changed, judged in the context of the whole spec.
2. Every other living spec's acceptance criteria, for check 1.
3. The guardrails of each criterion: `vdoc.py criteria` when the project has `criteria.json`,
   otherwise a search for the id in the tests and the gate.

## The checklist

**1. Should this spec exist?** For a new spec only. Ask of each of its criteria the
criteria-triage question: *if this feature were removed later, would the criterion go with it?*
When most criteria belong to features that already have a spec, the spec shouldn't exist: its
criteria become additions or edits there. Also a no: a spec holding one or two criteria that
extend another feature, or a spec named after the task rather than a behaviour. Verdict: keep,
fold into the named spec(s), or split (two behaviours that could change independently).

**2. Are the guardrails fast?** For each criterion the change added or edited, find the
guardrail and its run time: the test runner's timings (`pytest --durations=0`, `dotnet test`
with a console logger at normal verbosity, `vitest --reporter=verbose`) or the last CI log.
Run the guardrails only, never the whole suite, when no timing exists. Slow means it doesn't
fit `--quick` (about 20 s for the whole quick gate, so a single test over a second or two is
suspect), or it needs a browser, a container, a network or a real database.
A slow guardrail is a cost, not a defect. Don't recommend dropping it by reflex; for each, say:
- what makes it slow, and whether the same promise can be guarded lower (a unit or contract
  test instead of e2e, a type or lint rule instead of a test);
- if not, whether the criterion is worth that cost: what breaks unnoticed without it. Verdict:
  keep (worth it, say why), move lower (name how), or reword or drop the criterion.

**3. Is the text redundant?** Read the prose around the criteria (problem, behaviour,
scenarios, notes). Flag every passage that:
- restates a criterion in other words: delete it, the criterion is the promise;
- states an observable rule no criterion holds: it should be a criterion (with a guardrail), or
  it is an unchecked promise; propose the criterion text;
- describes how instead of what: it belongs in the plan, not the spec.
Keep prose that explains *why*, or that a criterion cannot say (a sketch, a scenario's context).

*New checks go here, as another numbered item in the same shape: the question, how to answer
it, the possible verdicts.*

## Answer

In chat, short, in the user's language:

- **Verdict**: one line: ready, or the number of findings per check.
- **One table per check** with findings only: what (criterion id, or a quoted passage), the
  finding, the recommendation. For check 2 also the guardrail and its measured time, and say
  when a time was estimated, not measured. A check with no findings is one line: "1: ok".
- **Unsure**: a finding you can't settle carries your recommendation and the question that
  decides it.

Then wait. The user decides; changes to the spec go through `/suwagent:visual-spec` or a direct
edit the user asks for. Under `/suwagent:autopilot`, apply the redundancy fixes of check 3,
log the rest as decisions for the user.

## Edge cases

- **No guardrails yet** (spec before code): check 2 judges the planned guardrail kind (e2e,
  integration, unit) from the criterion's wording, and says it is a forecast.
- **Size S, no spec changed**: nothing to review; don't run.
- **Several specs changed**: run every check on each, one block per spec.
