# Authoring a suwagent visual document

Shared rules for `visual-spec`, `visual-plan`, `visual-recap`, `visual-deviation`, `visual-qa` and the boards of `visual-readme`. The block catalog is in
`components.md` next to this file.

## Why the document exists

The user judges the agent's work from this page instead of from walls of chat text. Every
choice below serves one reader: a busy developer who opens the page cold, wants the shape of
the thing in 30 seconds, and then wants to drill into only the parts that worry them. Write
for scanning: the conclusion before the reasoning, a picture where a relationship is
spatial, real names (files, functions, fields) instead of vague nouns, and nothing padded.

## Where the files go

One folder per kind. The spec, plan, recap, deviation and QA page of the same piece of work
share one file name, so they find and link to each other:

```
docs/visual/spec/2026-10-25-export-csv.html
docs/visual/plan/2026-10-25-export-csv.html
docs/visual/recap/2026-10-25-export-csv.html
docs/visual/deviation/2026-10-25-export-csv.html
docs/visual/qa/2026-10-25-export-csv.html
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
   **Screenshots** for the "Screenshot with numbered marks" block: start the app (the
   project's dev server, or the `run` skill), then shoot each screen into the page's `img/`
   folder and open the PNG to place the marks:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" shot http://localhost:5173/reports docs/visual/recap/img/2026-10-25-export-csv-1.png --size 1280x800
   ```
   It uses a headless Chrome, Chromium, Edge or Firefox that is installed (`--browser` picks
   one) and also takes a local `.html` path, which is how you check the marks on your own
   page. A screen that needs a login, a click or a filled form first: take it with this
   session's browser tool (Claude in Chrome, the built-in browser, Playwright) and save the
   PNG to the same place. Never shoot screens with real customer data or secrets for a page
   that gets published; use test data, or keep the page `local`.
3. **Check it**, and fix every ERROR:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" check docs/visual/plan/2026-10-25-export-csv.html
   ```
4. **Publish** (`artifact` mode). Do all three steps, every time the file changes:
   1. Run `vdoc.py links <file>`. It says whether this file already has an artifact.
   2. Publish the local file with the Artifact tool, using `file_path` = the local `.html`:
      - **Not published yet**: give an `icon` (`list` for a spec, `map` for a plan, `report`
        for a recap, `compare` for a deviation page, `checklist` for a QA page) and a one-sentence `description`.
      - **Already published**: update **that** artifact by passing its URL as `url`, so the
        link stays the same. If the tool requires a read of the artifact first, read it, then
        publish the local file.
      - **The page has screenshots**: `check` lists them. Pass each one in `files`, keyed by
        the path the page uses: `{"img/2026-10-25-export-csv-1.png": "docs/visual/recap/img/2026-10-25-export-csv-1.png"}`.
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
  and architecture, and for UI a screenshot with numbered marks when the app runs (a
  wireframe when it doesn't or doesn't exist yet). Don't draw a diagram that a sentence explains
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

## Boards: pages that become pictures

A **board** is a page of picture panels, made to be turned into PNGs for a place that can't
show HTML: a README, a pull request, slides, a chat. Each `<section id="…">` on it is one
picture. It uses the same styles as the documents, so the pictures look like the pages.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" new board readme --title "reportgen README"   # docs/visual/board/readme.html
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" check docs/visual/board/readme.html
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" render docs/visual/board/readme.html --picture
```

- A board has no table of contents, no feedback bar and no date in its name: it is the
  source of the pictures, edited and rendered again whenever they need to change.
- Write one `<section id="hero">` per picture, built from the picture blocks in
  components.md (and any other block). A section is about one screen at most.
- `render` writes `img/<board>/<id>-light.png` and `<id>-dark.png` next to the board, at 2x,
  trimmed to the card with a transparent margin. `--only ID…` renders some of them,
  `--picture` prints a `<picture>` snippet for each that switches with the reader's theme.
- **Look at every picture** after rendering (open the PNG): a cut-off bottom (`render`
  warns), a card alone in a row (`--cols`), text that wraps badly.
- Pictures are rendered with Firefox or Chrome. Mermaid diagrams load from a CDN after the
  page; Chrome waits for them (`--wait`), Firefox may shoot before they appear, so draw
  pictures with the picture blocks rather than Mermaid.

`vdoc.py shot` takes the same options for any suwagent page: `--only <id or data-role>`
shoots one section of a spec, plan or recap (`--only tldr`, `--only how`), `--theme light|dark|both`, `--scale 2`, `--crop`.

## Older pages

A page carries its own copy of the template's CSS and JS, so it keeps working on its own and
doesn't change when the plugin does. To give an older page the current blocks and fixes,
run `vdoc.py refresh <page>`: it swaps the frame for the current template's and keeps the
`<html>` tag, the title and the content.

## Header (same for all three)

```html
<header class="doc-head">
  <span class="doc-kind">Plan</span>  <!-- Spec / Plan / Recap / Deviation / QA, in the document's language -->
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
