---
name: criteria-triage
description: Decide where each acceptance criterion of a proposed feature or change belongs, one criterion at a time, before any spec is written. Reads the proposal or the draft criteria and the acceptance criteria of all living specs in docs/visual/spec/, then recommends for each one: a new spec, an addition to an existing spec, an edit of an existing criterion, a removal of an existing criterion, or nowhere. It also sweeps the existing criteria for promises the change would break. The user corrects the routing in chat; nothing is written. Use after task-triage and before visual-spec writes the criteria, so they don't all land in one new file by default.
when_to_use: A proposed feature or change has criteria, or is about to get them, and they may belong in more than one place; visual-spec is about to write criteria; or the user says "criteria-triage", "gdzie te AC", "gdzie to umieścić", "do której specki", "nowy spec czy istniejący", "czy te AC mają sens".
argument-hint: "[the feature or change in plain words, draft criteria, or a draft spec page]"
---

# Criteria triage

One proposal is not one destination. Some of its criteria describe a new behaviour, some extend a
feature that already has a spec, some change a promise made earlier, and some aren't criteria at
all. This skill routes them **one by one**, so the feature's spec doesn't collect criteria that
belong elsewhere and old promises aren't left contradicting new ones.

| Verdict | When | What happens to the spec |
| :- | :- | :- |
| **New spec** | a behaviour no existing feature owns | goes into the named new spec |
| **Add** | the behaviour belongs to a feature that already has a spec | a new criterion in that spec |
| **Edit** | an existing criterion stays the same promise, but its details change | reworded in place, keeping its id |
| **Remove** | the change ends an existing promise | dropped from its spec; the id is never reused |
| **Nowhere** | not a criterion, or already promised | written in no spec, and the reason is named |

## What to read

Read-only. Change nothing.

1. The proposal: $ARGUMENTS (if empty, the feature or draft discussed in the conversation). When
   it has no draft criteria yet, write the candidates yourself: each an observable result, stated
   without an id.
2. Every living spec's acceptance criteria: `docs/visual/spec/*.html` (or the folder the project's
   AGENTS.md names). Read all of them, not only the spec the feature's name suggests: a new feature
   often breaks a promise made by a feature with another name.
3. The code, only where a spec doesn't settle who owns a behaviour. A project with `criteria.json`
   lists each criterion's guardrails with `vdoc.py criteria`; use it to name the guardrails that
   an edit or a removal affects.

## How to route

**Each candidate.** Take the first answer that fits:

1. **Is it a criterion at all?** It must be observable and checkable, and must survive a refactor
   that changes no behaviour. A chosen library or an internal structure fails this: nowhere.
2. **Is it already promised?** The same promise in an existing criterion: nowhere, naming that id.
3. **Does it change an existing promise?** The same promise with other details: edit. A different
   promise in the old one's place: remove the old one and route the new one as a new criterion, so
   a guardrail of the old id can't silently guard the new text.
4. **Who owns the behaviour?** Ask: *if the proposed feature were removed later, would this
   criterion go with it?* Yes: new spec. No: add it to the spec of the feature that owns it. Judge
   by the behaviour, never by the task that brought it up.

A new spec is one behaviour with one owner. When the candidates of "new spec" describe two
behaviours that could change or disappear independently, propose two specs.

**The sweep over existing criteria.** Candidates only show what the proposal says out loud. For
every existing criterion the change touches, ask: *is this still true once the proposal is built?*
No: an edit or a removal, even when no candidate mentioned it. Report what you find here as its
own rows, because this is what a draft spec never surfaces.

**Another repository's behaviour** is not routed here: a spec holds only its own repository's
criteria, and boundaries are contracts. Name it as a contract change for the owner.

## Answer

In chat, short, in the user's language:

- **Summary**: one line per destination, such as "1 new spec, 2 existing specs edited, 1 skipped".
- **The routing**, one table: the criterion (proposed text, or the id and its new wording), the
  verdict, the destination (spec title and path, or the name for a new spec), and a reason of a few
  words. Group the rows by destination, sweep findings included. An edit shows the old and new
  wording; a removal names the guardrails it leaves behind, when the project lists them.
- **Unsure**: a row you can't settle carries your recommendation and the question that decides it.
- **Next step**: `/suwagent:visual-spec` with this routing. When every row is "nowhere", no spec
  work is needed: say so, and say the task is then size S (a regression test without an id is
  still fine).

Then wait for the user's word: "ok", or corrections to single rows. Take a correction without
arguing. Nothing is written and no id is assigned here: `vdoc.py ids` numbers new criteria when
`/suwagent:visual-spec` writes them. Under `/suwagent:autopilot`, take the recommended routing and
log it as a decision.

## Edge cases

- **No specs in the repository yet**: there is nothing to add to, edit or remove, but nowhere and
  the split into separate behaviours still apply.
- **Size S, nothing observable changes**: there is nothing to route; don't run.
- **A criterion moves to another feature's spec**: a removal plus a new criterion, so that the
  guardrails get renamed to the new id on purpose.
- **Too many specs to read in one go**: delegate reading the criteria to a subagent, and make every
  routing decision yourself.
