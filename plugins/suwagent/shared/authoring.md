# Authoring a suwagent visual document

Shared rules for `visual-spec`, `visual-plan` and `visual-recap`. The block catalog is in
`components.md` next to this file.

## Why the document exists

The user judges the agent's work from this page instead of from walls of chat text. Every
choice below serves one reader: a busy developer who opens the page cold, wants the shape of
the thing in 30 seconds, and then wants to drill into only the parts that worry them. Write
for scanning: the conclusion before the reasoning, a picture where a relationship is
spatial, real names (files, functions, fields) instead of vague nouns, and nothing padded.

## Where the files go

One folder per kind. The spec, plan and recap of the same piece of work share one file name,
so they find and link to each other:

```
docs/visual/spec/2026-10-25-export-csv.html
docs/visual/plan/2026-10-25-export-csv.html
docs/visual/recap/2026-10-25-export-csv.html
docs/visual/recap/claude-artifacts.md      ← links to the published artifacts of this folder
```

- `vdoc.py new KIND SLUG` picks the path. The slug is 2-5 kebab-case words. Reuse the slug of
  an existing spec or plan for the same work, and `new` reuses its date too.
- If the project's CLAUDE.md / AGENTS.md names another location, pass it as `--root`.
- Don't commit these files on your own initiative; they go in when the user commits.

## Publishing mode

The SKILL.md that sent you here states the mode, which the user sets in `/plugin` →
suwagent → Configure:

- **`artifact`** (the default): the local `.html` is the source, and it is also published as a
  claude.ai artifact. The user reviews it from a link on any device and can comment on it.
- **`local`**: the file stays on this machine and opens in the browser. Use this mode for
  client or confidential repositories.

The project's CLAUDE.md / AGENTS.md, or the user in this conversation, can override the mode
("tylko lokalnie", "don't publish"). In `artifact` mode, if this session has no Artifact
tool (another agent, an API-key session), fall back to `local` and say so in one line.

## Steps

The helper is `${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py` (Python 3, standard library only).

1. **Create the page from the template**, never by writing the whole HTML yourself:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" new plan export-csv --title "Eksport CSV raportów" --lang pl
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" links docs/visual/plan/2026-10-25-export-csv.html
   ```
   `--lang` is `pl` or `en`. It sets the page's built-in labels, so use the language the user
   writes in, and write the document in it too. `--title` is a short **name** of 2-5 words,
   because it also names the artifact: "Eksport CSV raportów", never "Plan: eksport CSV —
   streaming…". The kind shows in the page's badge. `links` prints the `<a>` tags for the
   header nav: sibling documents, pointing at their artifacts when they're published.
2. **Write the body.** With the Edit tool, replace the empty line between
   `<!-- CONTENT START -->` and `<!-- CONTENT END -->` with the document. Touch nothing else
   in the file: the CSS and JS above and below render every block in `components.md`.
3. **Check it**, and fix every ERROR:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" check docs/visual/plan/2026-10-25-export-csv.html
   ```
4. **Publish** (`artifact` mode). Do all three steps, every time the file changes:
   1. Run `vdoc.py links <file>`. It says whether this file already has an artifact.
   2. Publish the local file with the Artifact tool, using `file_path` = the local `.html`:
      - **Not published yet**: give an `icon` (`list` for a spec, `map` for a plan, `report`
        for a recap) and a one-sentence `description`.
      - **Already published**: update **that** artifact by passing its URL as `url`, so the
        link stays the same. If the tool requires a read of the artifact first, read it, then
        publish the local file.
   3. **Register it. This is mandatory**: without the entry, the artifact is lost to the
      project and the next update would create a duplicate:
      ```bash
      python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" register docs/visual/plan/2026-10-25-export-csv.html https://claude.ai/artifact/<id>
      ```
      This adds or refreshes the row in `docs/visual/plan/claude-artifacts.md`.

   In **`local`** mode, open the page instead:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" open docs/visual/plan/2026-10-25-export-csv.html
   ```
5. **Hand over in chat in at most 5 lines**: the artifact link (or the local path), one
   sentence on what the document proposes or reports, the number of open questions, and what
   you need from the user (approval, answers). Never repeat the document's content in chat;
   the page is the deliverable.

## The review loop

Feedback arrives in one of three ways:

- **Comments on the artifact** (`artifact` mode). When the user comments on the page and sends
  the comment to Claude, it reaches this session. Read the comments with the artifact
  comments tool (load it through tool search if it's deferred).
- **Pasted feedback.** The page's feedback bar collects answers to the open questions,
  per-section comments and an Approve / Request changes verdict. **Copy feedback for the
  agent** puts it on the clipboard as a block that starts with `Feedback on <kind>:` /
  `Feedback do <kind>:`.
- **Plain chat.**

Whichever way it comes:

1. Answers to open questions become decisions: move each one out of the Open questions
   section and into the body as settled prose or a `callout decision`.
2. Edit the **local file**, which is the source of truth. Never edit only the artifact. Keep
   the document standalone: no "as discussed", "changed after feedback", "in the previous
   version".
3. Update the header `status`: `draft` → `approved` when the user approved; leave `draft`
   while changes are pending.
4. Run `check`, then publish again to the **same** artifact and `register` (or `open` in
   local mode). Reply with a short list of what changed.

## Quality bar (applies to all three)

- **Lead with a TL;DR** of 2-4 sentences: what, why, and the one thing the reader must decide or
  know. Someone who reads only the TL;DR should be able to say yes, no, or "wait".
- **Concrete before abstract.** Open with a real example (an actual request, a real screen,
  a real record) before architecture or tables.
- **Ground everything in the codebase.** Read the real files first. Name real paths, symbols,
  tables and endpoints. Mark anything inferred rather than read as a `callout assumption`.
- **One picture per real relationship.** Use a Mermaid diagram for flows, states, sequences
  and architecture, and a wireframe for UI. Don't draw a diagram that a sentence explains
  better, and don't draw a chain A→B→C that is just a list.
- **Decisions are explicit.** Every non-obvious choice gets a `callout decision` with its
  reason. When alternatives were weighed, show them side by side (`cols`) with the chosen one
  marked.
- **Open questions live in one place**: a single `questions` form at the end, each with a
  recommended option and why it matters. Ask only what changes the work; decide the rest
  yourself and say so. A document with no open questions is fine when nothing is open.
- **No padding.** No marketing tone, no restating the TL;DR at the end, no generic risks
  ("bugs may occur"), no sections that only say "N/A". Leave out a section that has nothing
  to say.
- **Size.** Aim for 5-10 minutes of reading. Put long detail in collapsed `<details>` or
  tabs, not in the main flow.
- **Abstract over code.** The user doesn't read code to judge the work: explain behaviour,
  roles and flows in words and pictures. Never show diffs. Show code only as a short contract
  (a signature, type or schema the reader must agree on), and only in a spec or plan.
- **Both themes.** Use only the template's classes and CSS variables (`var(--ok)` etc.), and
  never hard-coded colors, so the page reads in light and dark mode.

## Header (same for all three)

```html
<header class="doc-head">
  <span class="doc-kind">Plan</span>  <!-- Spec / Plan / Recap, in the document's language -->
  <h1>Eksport raportów do CSV</h1>
  <div class="doc-meta">
    <span><b>Status:</b> <span class="status draft">draft</span></span>
    <span><b>Data:</b> 2026-10-25</span>
    <span><b>Branch:</b> <code>feature/export-csv</code></span>
    <span><b>Zakres:</b> ~6 plików, 4 kroki</span>
  </div>
  <nav class="doc-nav">
    <a href="https://claude.ai/artifact/…">Spec</a>      <!-- the lines `vdoc.py links` prints -->
    <a aria-current="page">Plan</a>
  </nav>
</header>
```

Status values: `draft`, `approved`, `done` (recap of finished work).
