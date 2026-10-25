# Block catalog

Every block the template renders. Write plain HTML with these classes inside the content
area. Labels such as "Decision" or "Done when:" come from the page language (`--lang`).

## Section

Every part of the document is a section with an `<h2>` first. `data-role` names its purpose,
`vdoc.py check` uses it, and the page builds the table of contents and the per-section
comment button from it.

```html
<section data-role="approach">
  <h2>Podejście</h2>
  <p>…</p>
</section>
```

Roles: `tldr`, `problem`, `goals`, `scenarios`, `behaviour`, `ui`, `data`, `acceptance`,
`approach`, `architecture`, `files`, `code`, `steps`, `verification`, `risks`, `changes`,
`deviations`, `review`, `followups`, `questions`. Use any other role you need.

## TL;DR

```html
<section data-role="tldr">
  <h2>TL;DR</h2>
  <div class="tldr"><p>Dodajemy przycisk <b>Eksportuj CSV</b> na liście raportów…</p></div>
  <div class="stats">
    <div><b>6</b><span>plików</span></div>
    <div><b>4</b><span>kroki</span></div>
    <div><b>2</b><span>otwarte pytania</span></div>
  </div>
</section>
```

`stats` is optional: use it for counts that tell the size of the work (files, steps,
endpoints, tests, +/− lines).

## Callouts

```html
<div class="callout decision"><p>Streamujemy CSV zamiast budować go w pamięci, bo raporty mają do 2 mln wierszy.</p></div>
<div class="callout risk"><p>…</p></div>
<div class="callout warn"><p>…</p></div>
<div class="callout note"><p>…</p></div>
<div class="callout ok"><p>…</p></div>          <!-- verified fact, e.g. a test that passed -->
<div class="callout assumption"><p>…</p></div>  <!-- inferred, not read from the code -->
<div class="callout note" data-label="Poza zakresem"><p>…</p></div>  <!-- custom label -->
```

## Side-by-side comparison

Use it for options you weighed, before/after, or planned/done. Mark the chosen option.

```html
<div class="cols">
  <div class="chosen"><h4>A. Streaming</h4><p>…</p><p><b>+</b> stała pamięć <b>−</b> brak sumy kontrolnej</p></div>
  <div class="rejected"><h4>B. Plik w tle + mail</h4><p>…</p></div>
</div>
```

## Diagram (Mermaid)

Write the source raw: no HTML escaping is needed inside the script tag. Rendered from a CDN.
Offline, the source text is shown instead.

```html
<script type="text/x-mermaid" data-caption="Przepływ eksportu">
flowchart LR
  UI[ReportsList] -->|GET /reports/:id/export| API[ExportController]
  API --> Q[(reports_rows)]
  API -->|stream text/csv| UI
</script>
```

Pick the diagram type by the question it answers: `flowchart` (structure, data flow),
`sequenceDiagram` (who calls whom, in what order), `stateDiagram-v2` (states and
transitions), `erDiagram` (data model), `gantt` (only when timing matters). For before/after
architecture, put two diagrams in `cols`. Keep labels short, and give each node a real
component, file or table name.

## Wireframe

A low-fidelity sketch of a screen. Show real labels and real data, not lorem ipsum. Mark
what is new with `wf-new` and what goes away with `wf-gone`.

```html
<div class="wire-pair">
  <div class="wire"><span class="wf-label">Przed</span>
    <div class="wf-bar"><b>Raporty</b><span class="wf-grow"></span><span class="wf-input">Szukaj…</span></div>
    <div class="wf-body">
      <div class="wf-card wf-row"><span class="wf-grow">Sprzedaż Q3</span><span class="wf-muted">12 400 wierszy</span></div>
    </div>
  </div>
  <div class="wire after"><span class="wf-label">Po</span>
    <div class="wf-bar"><b>Raporty</b><span class="wf-grow"></span><span class="wf-input">Szukaj…</span></div>
    <div class="wf-body">
      <div class="wf-card wf-row"><span class="wf-grow">Sprzedaż Q3</span><span class="wf-muted">12 400 wierszy</span><span class="wf-btn wf-new">Eksportuj CSV</span></div>
    </div>
  </div>
</div>
```

Pieces: `wire` (frame; add `after` for the new state), `wf-label`, `wf-bar` (top bar or
toolbar), `wf-body`, `wf-row`, `wf-grow`, `wf-card`, `wf-btn` (`primary`), `wf-input`,
`wf-muted`, `wf-line` (a placeholder text line), `wf-new`, `wf-gone`. One `wire` on its own
is fine for an additive change. Use several for a flow, one per state (empty, loading,
error, success).

## File map

```html
<ul class="files">
  <li class="dir">src/reports/</li>
  <li data-change="added"><span class="path">src/reports/export.ts</span><span class="why">streaming CSV writer</span><span class="stat"><span class="p">+120</span></span></li>
  <li data-change="modified"><span class="path">src/reports/routes.ts</span><span class="why">new route GET /reports/:id/export</span><span class="stat"><span class="p">+8</span> <span class="m">−1</span></span></li>
  <li data-change="deleted"><span class="path">src/legacy/csv.js</span><span class="why">replaced by export.ts</span></li>
</ul>
```

`data-change`: `added`, `modified`, `deleted`, `renamed`, `unchanged` (shown for context).
In a plan, `why` says what will change; in a recap, it says what did change and `stat` gives
the line counts.

## Code with notes

Raw code: no escaping, except that a literal `</script>` is written `<\/script>`. The
`data-notes` value is a JSON array inside **single quotes**. `lines` is `"12"`, `"12-18"` or
`"3,7-9"`, counted from `data-start`.

```html
<script type="text/x-code" data-file="src/reports/export.ts" data-start="1"
  data-notes='[{"lines":"4-6","label":"Backpressure","note":"czekamy na drain, inaczej 2 mln wierszy w RAM"}]'>
export async function streamCsv(rows: AsyncIterable<Row>, out: Writable) {
  out.write(header());
  for await (const row of rows) {
    if (!out.write(toLine(row))) {
      await once(out, "drain");
    }
  }
}
</script>
```

Optional: `data-lang` when the file extension doesn't say it, `data-title`, and `data-summary`
(one line under the header). In a plan, show the planned shape (signatures, types, a stub with
TODO comments), not a full implementation.

## Diff with notes (recaps)

Leave the body empty and set `data-git` to the `git diff` arguments. `vdoc.py fill-diffs`
pastes the real output in. One block per key file keeps each tab focused.

```html
<script type="text/x-diff" data-git="main...HEAD -- src/reports/export.ts"
  data-summary="Nowy writer CSV ze streamingiem"
  data-notes='[{"line":14,"note":"backpressure: bez tego proces puchnie na dużych raportach"},{"old":30,"note":"usunięty bufor całego pliku"}]'></script>
```

- `line` / `lines` refer to line numbers in the **new** file, and `old` to a removed line in the
  old file. Read them from the hunk headers (`@@ -a,b +c,d @@`) after filling.
- With several files in one block, add `"file":"export.ts"` to each note, and the note goes to
  that file's card.
- `data-collapsed` starts the card folded. Use it for long, low-interest files.
- You can also paste a diff by hand instead of `data-git`. The block takes raw unified-diff
  text.

## Tabs

```html
<div class="tabs">
  <div data-tab="export.ts">…a diff or code block…</div>
  <div data-tab="routes.ts">…</div>
</div>
```

## Steps (plans)

```html
<ol class="steps">
  <li>
    <h4>Writer CSV ze streamingiem</h4>
    <p>Nowy moduł <code>src/reports/export.ts</code>, reużywa <code>formatCell()</code> z <code>src/format.ts</code>.</p>
    <div class="touches">src/reports/export.ts (nowy), src/format.ts</div>
    <div class="done-when"><code>npm test -- export</code> przechodzi; 1 mln wierszy &lt; 200 MB RSS</div>
  </li>
</ol>
```

Each step can be checked on its own (`done-when`), and the steps come in an order that
keeps the code working after each one.

## Checklist (acceptance criteria)

```html
<ul class="checks">
  <li>Przycisk eksportu widoczny tylko dla roli <code>analyst</code> i wyżej</li>
  <li data-status="pass">CSV otwiera się poprawnie w Excelu (BOM, średniki) <span class="evidence">test: export.spec.ts › excel-compat</span></li>
  <li data-status="fail">… <span class="evidence">why it fails</span></li>
  <li data-status="partial">…</li>
  <li data-status="skipped">…</li>
</ul>
```

In a spec, the items have no status: they are the contract. In a recap, give each one a
status and evidence (a test name, a command and its output, a file:line).

## Table

A plain `<table>` with `<th>`. It is styled and scrolls on phones. Use it for edge cases
(input → expected behaviour), API fields, and config options.

## Open questions

Exactly one form, at the end. Each question says why it matters. Mark the option you
recommend with `data-recommended`. The page adds a free-text box to each question by itself.

```html
<section data-role="questions">
  <h2>Otwarte pytania</h2>
  <form class="questions">
    <fieldset data-id="q1">
      <legend>Jaki separator w CSV?</legend>
      <p class="why">Polski Excel domyślnie oczekuje średnika; narzędzia BI przecinka.</p>
      <label data-recommended><input type="radio" value="semicolon"><span><b>Średnik</b><small>działa od razu w Excelu PL</small></span></label>
      <label><input type="radio" value="comma"><span><b>Przecinek</b><small>standard RFC 4180</small></span></label>
    </fieldset>
    <fieldset data-id="q2">
      <legend>Które kolumny eksportować?</legend>
      <label><input type="checkbox" value="all"><span><b>Wszystkie</b></span></label>
      <label data-recommended><input type="checkbox" value="visible"><span><b>Tylko widoczne w tabeli</b></span></label>
    </fieldset>
  </form>
</section>
```

Use `radio` for one choice and `checkbox` for several. A question with no options (just a
`<legend>` and `why`) becomes a free-text answer.

## Collapsible detail

```html
<details><summary>Pełna lista przypadków brzegowych (14)</summary> … </details>
```
