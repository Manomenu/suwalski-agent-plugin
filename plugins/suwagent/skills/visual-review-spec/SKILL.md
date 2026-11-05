---
name: visual-review-spec
description: Write the page a reviewer reads instead of the living spec, as one visual HTML page frozen for one task. A spec the task created appears whole, as a copy; a spec the task edited appears only as what changed (criteria added, changed and dropped, new diagrams and images, an explanation in plain words); several specs go on the same page, visibly split into parts. Living specs keep moving as other tasks land, so a link to one shows a reviewer things from outside their task. This page doesn't move. It is gitignored and valid until the merge request closes.
when_to_use: A change that added or edited a spec goes to a teammate for review, or a link for a merge request or ticket is needed; or the user says "visual review spec", "review spec", "spec do review", "co zmieniono w specyfikacji", "link do specki dla recenzenta".
argument-hint: "[task slug] [--base branch]"
---

# Visual review spec

A living spec is one document per feature, and every task edits it in place. That is right for
the agent and for whoever reads the spec next year, and wrong as a review link: once another
task edits the same spec, the page holds things from outside the reviewer's task, and a whole
spec never says which part this task touched. This page answers the reviewer's question: **what
is this task doing to our specs?** It is one page per task, however many specs the task touches,
so one link goes into the merge request.

Before writing, read these two files. They hold the rules shared by the visual skills and the
HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog

Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

What to cover: $ARGUMENTS (if empty, the current branch and the specs on disk, uncommitted edits
included).

## Rules

- **The living spec stays the source.** Review feedback on a criterion or a behaviour changes
  the living spec first; then generate this page again. Never fix only this page, or the
  committed spec and what the reviewer approved drift apart.
- **The final spec comes first.** Accepted deviations are already written into the spec
  (`/suwagent:visual-deviation`), so the reviewer judges what will be committed.
- **The task's slug, never the spec's.** Name the page after the branch or ticket
  (`sr-108-return-limits`). Two tasks can edit one spec: under the spec's slug the second would
  overwrite the first one's page and artifact, and the reviewer's link would move again, which
  is what this page exists to stop. Generate again on the same branch: same file, same artifact.
  `new` reports a file that already exists; if it belongs to another task, pick another slug.
- **No spec changed: no page.** Say so in one line; a task of size S has nothing to show here.
- **The tool computes, you explain.** `spec-delta` decides what changed and writes it on the page.
  Don't retype criteria or trim the copied spec by hand; only the explanations are yours.
- **Which base.** The comparison starts where the branch left its base (the merge-base), so what
  other tasks landed on the main branch never shows up, even after it is merged into this branch.
  Run `git fetch` first. On a stacked merge request pass the parent branch as `--base`.

## Steps

```bash
git fetch
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" spec-delta                 # what changed; stop here when nothing did
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" new review-spec sr-108-return-limits --title "SR-108 zwroty" --lang pl
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" spec-delta --into docs/visual/review-spec/<date>-sr-108-return-limits.html
```

`--into` writes the page body. Replace every `<!-- WRITE: … -->` with your text; `check` fails
while one is left. Generating again later keeps what you wrote and says so: read it again,
because the delta under it may have moved. When `check` warns that a spec changed since
generation, generate again and publish to the same artifact, before the reviewer reads a stale
page.

Add `--base <parent>` to the `spec-delta` calls on a stacked merge request.

## What the page holds

| Part | Written by | Holds |
| :- | :- | :- |
| Header | tool | base and head commits, the branch, so a reader knows the exact state shown |
| `tldr` | you | 2-4 sentences: what the task does to the specs, what the reviewer must judge. `stats` when counts help (new specs, changed specs, criteria) |
| 🆕 New spec | tool | the band, then the whole spec, word for word. A task with only this part is simply a copy of the spec |
| ✏️ Changed spec | tool and you | the band; `what-changed`, yours; a table of criteria added, changed (was and now) and dropped; new diagrams and images |
| 🗑️ Removed spec | tool and you | the band; why it goes and where its behaviour went, yours; the criteria that go |

In `what-changed`, write what a reviewer who knows the old behaviour needs: which behaviour
changes, why, what stays as it was, in the terms of the spec, not the code. Name every changed
section `spec-delta` listed that the criteria don't explain; quote or redraw only the points that
matter, not the whole section. A wireframe or table that changed and carries the point can be
copied from the spec into this section. Never restate the unchanged rest of the spec.

A renamed spec file shows as one removed and one new: move the explanation into one part and
say it is a rename.

## Hand-off

Follow the hand-off step in authoring.md, and end with one line ready to paste into the merge
request or ticket, in the user's language: the page's link and the counts ("Spec do review: <link>:
1 nowa, 2 zmienione"). Don't post it yourself: the user decides where it goes. A published artifact
starts private, so say the reviewer can open it only after the user shares it. In `local` mode
give the path and say the file can be attached to the merge request; copied images in `img/` go
with it.

This page is a working page of one merge request: it stays out of git (`docs/visual/review-spec/`
in `.gitignore`) and is not updated after the merge. Left unignored, its criterion ids also read
to `vdoc.py criteria` as ids in a file nothing runs, and the gate fails.
