# The method: spec-driven with guardrails

How this user runs software work with agents, in every repository, greenfield or brownfield.
The SessionStart hook points here; read this file at the start of any task bigger than a
one-liner, and before writing a spec, a plan, a guardrails page or a review.

## 1. Size first
/suwagent:task-triage proposes S (no behaviour visible to a user or an API caller changes: a ticket and a test, no spec), M (an existing feature's behaviour changes: a delta in its living spec) or L (a new feature or a contract change: spec and plan); the user confirms in a word. The threshold is one question: does it change behaviour someone can see, or a contract? The number of files does not decide.

## 2. One living spec per feature
One living spec per feature (one behaviour, one owner), never per task or repository, so one task can touch several specs: on M and L, /suwagent:criteria-triage routes each criterion before the spec is written (new spec, add to an existing spec, edit or remove an existing criterion, or nowhere) and the user confirms. A task edits a spec in place, no changelog; before the merge it is rewritten as if the accepted deviations had always been there, and that final spec is committed with the work. What and why, never how. Decisions are one sentence in the spec, or a file in docs/adr/ only when they span features. A spec never lists its consumers.

## 3. Criteria as guardrails
Acceptance criteria carry ids (AC-<feature>-<n>) and live outside the spec only as guardrails naming the id: a test, a lint rule, a type check. The gate's rule is one-way: every criterion needs a guardrail and every id in a guardrail must exist in this repository's spec; a test without an id is fine (regression, bug, adaptation to another repository's contract). An unprovable criterion is reworded or dropped.

## 4. Contracts on boundaries
Boundaries between repositories are contracts, not shared specs: one spec at the owner; consumers are tied by the generated contract (openapi.json, an event schema) that the owner's CI compares with the main branch and fails on a breaking change. A consumer tags adapting tests with the contract version (contract name@version), not an AC id, and gets a delta in its own spec only when its own behaviour changes.

## 5. The gate is the only proof
The gate is the only proof: one script, --quick in the hook after every agent turn within a hard budget of about 20 s, the full gate before pushing and in CI, identical. The agent never edits the gate, hooks, lint configs or characterization recordings; it asks the owner. A skipped step fails in CI. A new rule goes as low as it can: type, lint, test, hook; a sentence in AGENTS.md only for what none of these can check.

## 6. Two review paths
Review has two paths; on both the human reads the spec and the guardrails page, never the test code. /suwagent:review-triage picks: ordinary (spec, guardrails page, recap; a separate agent reads the diff through /suwagent:agent-review) or careful (the human also reads the diff) when the change touches the always-careful list: login and permissions, payments, data migrations, code without characterization tests. Guardrails and review pages are written by an agent that did not write the code, are valid until the merge request closes, and stay out of git.

**What a reviewer reads of the spec.** A living spec is a bad review link in a team: it holds everything other tasks added since, and it never says what this task touched. So a task that added or edited a spec gets one /suwagent:visual-review-spec page, frozen for that task, and that page's link goes into the merge request or ticket, not the spec's:

| The task | The page shows |
| :- | :- |
| created a spec | that spec, whole, as a copy |
| edited a spec | only the change: what and why in plain words, criteria added, changed and dropped, new diagrams and images |
| did both, or touched several specs | all on the one page, each in its own visibly marked part, so there is one link to paste |
| changed no spec (size S) | no page |

The living spec stays the source: review feedback changes the spec, then the page is generated again. The comparison starts at the merge-base, so what other tasks landed never shows. The page is named after the task, never the spec, because two tasks can edit one spec.

## 7. Brownfield first, then specs
Before an agent touches legacy code it gets AGENTS.md as a map (about 100 lines, links deeper), CONTEXT.md in the modules about to be touched (purpose, traps, where to start; written by an agent, corrected by someone who knows the code), characterization tests recorded around that code before any change (they record today's behaviour without judging it; the agent records, never changes a tracked recording; a failing one is fixed in the code) and the gate script. Only then specs, only for what changes. New things grow as separate projects in the same solution, one per group of features, with a boundary enforced by an architecture test or analyzer, not as folders in existing projects and not as microservices; legacy reaches a module only through an adapter. Greenfield starts from the owner's template.

## Where each thing lives in a repository

| Layer | What | When the agent sees it |
| :- | :- | :- |
| AGENTS.md / CLAUDE.md | map of the repository, commands, the always-careful list, rules nothing can check | always |
| docs/visual/spec/<feature>.html | the living spec: what, why, criteria with ids | when the task touches that feature |
| docs/adr/ | decisions that span features; never edited, superseded by a new file | on demand |
| the gate (check script, tests, lint, hooks) | the rules that are enforced | after every turn (quick) and before push / in CI (full) |
| CONTEXT.md in a legacy module | purpose, traps, where to start | when the task enters the module |
| plans, recaps, guardrails, review-spec and review pages | working pages of one task, gitignored | never after the merge |
