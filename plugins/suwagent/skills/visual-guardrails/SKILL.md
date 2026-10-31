---
name: visual-guardrails
description: Check whether every acceptance criterion of a spec is guarded on the project's gate (CI pipeline, check script, pre-commit) by an automated check that fails when the criterion breaks (a unit, integration or e2e test, a lint rule, a type check, a schema or contract test), as a visual HTML page with a criterion → guardrail coverage matrix. Gaps, weak guardrails (skipped, not run on the gate, asserting too little) and criteria that only a human can check get a proposed guardrail each. Use so that the code and the spec don't drift apart unnoticed.
when_to_use: The user asks whether the spec is covered by tests or other checks, or says "visual guardrails", "guardrails", "spec guardrail coverage", "pokrycie specyfikacji", "pokrycie guardrailami", "czy specka jest pokryta testami", "co pilnuje kryteriów akceptacji", "czy się nie rozjedzie"; or a spec exists and work is about to be merged or released.
argument-hint: "[which spec, in plain words | all]"
---

# Visual guardrails

A guardrails page answers one question: **if someone breaks what the spec promises, will the
gate notice?** A recap checks that the criteria pass today; this page checks that something
keeps checking them tomorrow. For each acceptance criterion it names the guardrail that
guards it, shows that the guardrail runs on the gate, and judges whether it really asserts
the criterion. What has no guardrail gets a proposal for one.

A **guardrail** is an automated check that runs on the gate and fails when the criterion is
broken: a unit, integration, contract or e2e test, a lint or architecture rule, a type
check, a schema validation, a snapshot or visual test. A test that exists but doesn't run on
the gate is not a guardrail yet.

Before writing, read these two files. They hold the rules shared by the visual skills and
the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Table",
  "Checklist", "Tags", "Callouts" and "Open questions"

Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

What to check: $ARGUMENTS

## Rules

- **Read-only.** Change no code, tests or CI in the user's working tree. The only file you
  write is the page; the break probe below runs in a throwaway git worktree. Filling the gaps
  is separate work the user decides on afterwards.
- **The baseline is the spec.** The user doesn't need to know file names: the argument is
  optional and may be plain words ("ten od eksportu CSV"), a path, an artifact link, or `all`.
  - No argument: the spec of the work in this conversation or on this branch (matched by the
    branch name, the conversation, or the spec the plan links to).
  - Plain words: the spec in `docs/visual/spec/` whose title or file name matches them.
  - `all`: every spec in `docs/visual/spec/`, on one page with one section of the matrix per
    spec (slug `all-specs`).
  - Nothing matches, or several do: list the specs found by their titles (the `<h1>`) and
    dates and let the user pick one, or all of them, with the ask-the-user tool. Never ask the
    user to type a slug.

  Create the page with the **same slug** as the spec, so it sits next to it.
- **No spec: stop.** Say in one line that there is nothing to measure coverage against, and
  suggest `/suwagent:visual-spec`. Never reconstruct criteria from the code and then find
  them covered by the same code.
- **What counts as a criterion.** Every item of the spec's `acceptance` list. Also the rows of
  the edge-case table in `behaviour` and the main scenario in `scenarios`, as their own rows
  under the criterion they belong to, because these are what breaks quietly.

## Find the gate, once

The gate is what must pass before code is merged or released. Find it from the project, not
from habit:

- CI config: `.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`,
  `bitbucket-pipelines.yml`, `.circleci/`; which jobs run on merge requests and on the main
  branch, and which are required or allowed to fail.
- The commands those jobs call: `package.json` scripts, `Makefile`, `justfile`, `tox.ini`,
  `noxfile.py`, `pyproject.toml`, `build.gradle`, `*.csproj` test projects, `pre-commit` and
  `husky` hooks. Follow them down to the test runner and its config (include and exclude
  paths, tags, projects), the linter config and the type checker.
- The project's CLAUDE.md / AGENTS.md / CONTRIBUTING, which may name the gate.

No CI at all: the gate is the project's local check script if there is one; say so in a
`callout risk`, because nothing enforces it.

## Map criteria to guardrails, once

For each criterion, look for what asserts its observable result: first by its id
(`AC-<feature>-<n>`; tests and lint rules name it, and a project may have a check that lists
them), then by the nouns of the criterion (the endpoint, screen, field, message, error code),
by the spec's slug, and by the code paths the criterion runs
through. Then give it one status:

| status | meaning | `data-status` |
|---|---|---|
| **guarded** | a guardrail on the gate asserts the criterion's observable result | `pass` |
| **weak** | a guardrail exists but doesn't really hold: it only touches the path (smoke, no assertion on the result), mocks away the part the criterion is about, covers the happy path but not the stated limit, or is skipped / quarantined / allowed to fail | `partial` |
| **off the gate** | a check exists, but the gate doesn't run it (excluded path, tag not selected, job only on schedule or manual) | `partial` |
| **none** | nothing automated checks it | `fail` |
| **manual only** | it can't reasonably be automated (a visual judgement, an external party) and needs a human step; say which one | `skipped` |

**Evidence, not names.** A test called `exports csv` is not evidence: read its assertions.
Each status other than `none` carries the guardrail's kind, its `file:line` and test name,
and the gate job that runs it. Run the guardrails you mapped (only those, with the project's
runner) and record whether they pass now; a red guardrail is a finding of its own. If a run
is too expensive or needs services that aren't there, say it wasn't run.

## Does it really guard? Two questions, never one

A guardrail that addresses a criterion and a guardrail that is good are different findings.
`guarded` needs both. For every mapped guardrail, check that:

- it asserts the criterion's **observable result** (the value, message, status, screen state
  or limit the criterion names), not only that the code ran without throwing;
- it exercises the real part the criterion is about; a mock of that very part, or a snapshot
  accepted without reading, doesn't count;
- it covers the criterion's stated limits and edge cases (the `behaviour` rows), not only the
  happy path;
- it is deterministic: no sleeps, order dependence or data that changes run to run.

When reading leaves doubt, and always for criteria whose failure would hurt users or data,
**break it and watch**: in a temporary `git worktree` of the current commit, make the
smallest change to the code that violates the criterion (drop the check, change the limit,
return the wrong status), run only that guardrail, and record whether it went red. Remove
the worktree afterwards. A guardrail that stays green is `weak`, with the probe as the
evidence. Say on the page which guardrails were probed and which were judged by reading only.

For each gap (`weak`, `off the gate`, `none`), propose a guardrail: its kind (pick the
cheapest one that would actually fail: a type or lint rule before a unit test, a unit test
before an e2e test), where it would live (the existing test file or suite it belongs to),
what it asserts in one sentence, and the cost (S / M / L). For `off the gate`, the fix is
often a line in the gate rather than a new test.

## Sections, in order

Keep it to 3-5 minutes of reading. Leave out a section that has nothing to say.

1. **Header**, `doc-kind` "Guardrails", status `done`, the branch and commit in the meta
   line, and the nav links `vdoc.py links` prints (the spec, and the plan and recap if they
   exist).
2. `tldr`: 2-3 sentences with 🟢 (every criterion guarded), 🟡 (gaps, but none on a criterion
   whose failure would hurt users or data) or 🔴 (a key criterion unguarded, or a guardrail
   red now) at the start. `stats`: criteria guarded (e.g. 7/11), weak or off the gate, none,
   manual only.
3. `gate`: what the gate is, in one small Mermaid `flowchart` (trigger → jobs → commands →
   runners), with required jobs marked, and a `callout risk` for anything that weakens it
   (jobs allowed to fail, tests excluded by config, no CI).
4. `coverage`: the matrix as a `table`, worst first: criterion (as the spec words it, short)
   · status `tag` · guardrail kind · where (`file:line`, test name) · gate job · passes now ·
   fails when broken (probed / read only).
   Edge cases and scenarios as indented rows under their criterion. With `all`, one `<h3>`
   per spec.
5. `gaps`: per gap, an `<h3>` with the criterion, what could break unnoticed (a concrete
   change someone could make that no check would catch), and the proposed guardrail as a
   `callout decision` (kind, place, what it asserts, cost).
6. `manual`: the `manual only` criteria as a `checks` list with `data-status="skipped"`,
   each saying who checks it and when (a QA scenario, a release checklist).
7. `questions`: one fieldset with a checkbox per proposed guardrail, the recommended ones
   marked `data-recommended`, so the user picks which gaps to fill.

No code and no diffs: `file:line` as a reference only, as in a recap.

## After the user decides

The chosen guardrails are implementation work: suggest writing them, each in the place the
page proposed, and run the gate once at the end over all of them. When a criterion turns out
to be untestable as worded, the spec's wording is what changes: propose the rewritten
criterion. This page is a working page and stays out of git, like the plan and recap.

## Hand-off

Follow the hand-off step in authoring.md. Start the chat summary with the same 🟢/🟡/🔴 as
the TL;DR and the count (e.g. "7/11 criteria guarded"), and say what's needed from the user
(which gaps to fill, or nothing).
