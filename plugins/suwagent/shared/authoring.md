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

One folder per piece of work, so the spec, the plan and the recap of the same feature sit side
by side and link to each other:

```
docs/visual/<YYYY-MM-DD>-<slug>/spec.html
docs/visual/<YYYY-MM-DD>-<slug>/plan.html
docs/visual/<YYYY-MM-DD>-<slug>/recap.html
```

- `<YYYY-MM-DD>` is the day the folder was created; `<slug>` is 2-5 kebab-case words.
- If a folder for this piece of work already exists (a spec made earlier), reuse it.
- If the project's CLAUDE.md / AGENTS.md names another location, use that.
- Don't commit these files on your own initiative; they go in when the user commits.

## Steps

The helper is `${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py` (Python 3, standard library only).

1. **Create the page from the template**, never by writing the whole HTML yourself:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" new plan docs/visual/2026-10-25-export-csv/plan.html --title "Eksport CSV raportów" --lang pl
   ```
   `--lang` is `pl` or `en` and sets the page's built-in labels; use the language the user
   writes in, and write the document itself in that language too.
2. **Write the body.** With the Edit tool, replace the empty line between
   `<!-- CONTENT START -->` and `<!-- CONTENT END -->` with the document. Touch nothing else
   in the file: the CSS and JS above and below render every block in `components.md`.
3. **Check it**, and fix every ERROR:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" check docs/visual/.../plan.html
   ```
4. **Open it** in the user's browser. The command prints the `file://` URL:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" open docs/visual/.../plan.html
   ```
5. **Hand over in chat in at most 5 lines**: the path/URL, one sentence on what the document
   proposes or reports, the number of open questions, and what you need from the user
   (approval, answers). Never repeat the document's content in chat; the page is the
   deliverable.

## The review loop

The page has a feedback bar: the user answers the open questions, leaves a comment on any
section, marks **Approve** or **Request changes**, and presses **Copy feedback for the agent**.
They paste a block that starts with `Feedback on <kind>:` / `Feedback do <kind>:` followed
by the page's path.

When that block arrives:

1. Treat it as a review of that file. Answers to open questions become decisions: move each
   one out of the Open questions section and into the body as settled prose or a
   `callout decision`.
2. Edit the same file (the document is the source of truth, not the chat). Keep it standalone:
   no "as discussed", "changed after feedback", "in the previous version".
3. Update the header `status`: `draft` → `approved` when the user approved; leave `draft`
   while changes are pending.
4. Run `check`, then `open` again, and reply with a short list of what changed.

If the user replies in plain chat instead, apply it the same way.

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
    <a href="spec.html">Spec</a>
    <a href="plan.html" aria-current="page">Plan</a>
    <a href="recap.html">Recap</a>   <!-- link only the documents that exist -->
  </nav>
</header>
```

Status values: `draft`, `approved`, `done` (recap of finished work).
