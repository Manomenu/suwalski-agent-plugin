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

With four items, use `class="cols two"`: two per row, so none is left alone in a row.

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
component, file or table name. Keep a diagram to about 10 nodes. For a long chain, use
`flowchart TB` with `subgraph … direction LR … end` rows, so the diagram stays readable on
one screen instead of becoming a thin, tiny strip.

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

## Screenshot with numbered marks

A real screenshot of the UI with numbered frames on the elements that matter and a legend
under it. Use it in a recap whenever rendered UI changed (and in a spec or plan to show the
current state). It shows the reader exactly where on the screen to look, which a wireframe
can't. Take the image with `vdoc.py shot` (see authoring.md) and save it next to the page in
`img/`, named after the page: `docs/visual/recap/img/2026-10-25-export-csv-1.png`.

```html
<figure class="shot">
  <div class="shot-img">
    <img src="img/2026-10-25-export-csv-1.png" alt="Lista raportów z nowym przyciskiem eksportu">
    <span class="mark new" data-n="1" style="left:71%; top:18%; width:14%; height:7%"></span>
    <span class="mark" data-n="2" style="left:4%; top:30%; width:92%; height:9%"></span>
  </div>
  <ol class="shot-legend">
    <li class="new" data-n="1"><div><b>Eksportuj CSV</b>: nowy przycisk; pobiera bieżący raport z filtrami</div></li>
    <li data-n="2"><div><b>Wiersz raportu</b>: liczba wierszy liczy się teraz po filtrach</div></li>
  </ol>
  <figcaption>Raporty po zmianie</figcaption>
</figure>
```

- A `mark` is placed in **percent of the image** (`left`, `top`, `width`, `height`), so it
  stays on its element at any page width. Read the box off the screenshot (open the PNG and
  look), or from the browser's element bounds divided by the viewport size when a browser
  tool gives them. Then shoot the rendered page itself and check that every frame sits on
  its element.
- `new` (green) marks what was added, `gone` (red, dashed) what was removed, and a plain mark
  (orange) what changed. Each `li` of the legend has the same `data-n` and class as its mark.
- Number the marks in reading order (top-left to bottom-right, or the order of the
  interaction), at most ~6 per image. Frame the element itself with a little margin, not a
  whole region.
- Before/after: two figures in a `<div class="shot-pair">`, the before state with `gone`
  and changed marks, the after state with `new` and changed marks, numbered the same where
  they show the same element.
- A flow of several screens: one figure per step, in order, each with its own legend.

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

Raw code: no escaping, except that a literal `</script>` is written `<\/script>` and `<!--` is written `<\!--`. The
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
(one line under the header). Use code sparingly. The user doesn't want to read code, so show
only a contract the reader has to agree on (a new signature, type, schema or config shape),
at most ~15 lines, and never a full implementation. Recaps show no code and no diffs.

## Elements and their roles (recaps, plans)

Explain each moving part in plain words: what it is responsible for, what it takes in and
gives out, and what it talks to. This replaces reading the code.

```html
<div class="cols">
  <div><h4>ExportController</h4><p>Przyjmuje żądanie eksportu, sprawdza uprawnienia i otwiera strumień.</p>
    <p class="wf-muted">wejście: id raportu · wyjście: plik CSV · rozmawia z: ReportRepository</p></div>
  <div><h4>CsvWriter</h4><p>Zamienia wiersze na linie CSV i pilnuje, żeby nie trzymać całego pliku w pamięci.</p></div>
</div>
```

## Walkthrough (recaps)

A numbered "what happens when…" story of one real scenario through the new code. Reuses
the `steps` list. Each step is one sentence of behaviour with the responsible element in
`<code>`, and no code.

```html
<h3>Co się dzieje, gdy analityk klika „Eksportuj CSV”</h3>
<ol class="steps">
  <li><p><code>ReportsList</code> wysyła żądanie z id raportu i aktualnymi filtrami.</p></li>
  <li><p><code>ExportController</code> sprawdza rolę; brak uprawnień kończy się komunikatem, a nie pustym plikiem.</p></li>
  <li><p><code>CsvWriter</code> wysyła plik partiami; przeglądarka zaczyna pobieranie od razu.</p></li>
</ol>
```

## Tabs

```html
<div class="tabs">
  <div data-tab="Przed">…</div>
  <div data-tab="Po">…</div>
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

## Tags

Small labels for a state or a kind, such as how something is invoked or a risk level:

```html
<span class="tag accent">ręcznie</span> <span class="tag ok">automatycznie</span> <span class="tag note">zawsze</span>
<span class="tag warn">wymaga konfiguracji</span> <span class="tag bad">ryzykowne</span>
```

## Terminal

What the user sees in the terminal or chat, such as a command and its output or an agent's
reply. It is always dark, like a real terminal, so it reads the same in both themes:

```html
<div class="term"><span class="dim">$</span> python3 limits.py status
OK 5h 34% (resets 16:00) · 7d 52% (resets Thu 09:00)</div>
```

## Collapsible detail

```html
<details><summary>Pełna lista przypadków brzegowych (14)</summary> … </details>
```

## Picture blocks

Blocks drawn for a reader who looks rather than reads. They work in any page, and they are
what a **board** is made of (see "Boards" in authoring.md): a hero card, a pipeline, a grid
of cards, a before/after, a "which one when", a settings panel. Every text in them is short:
a label, a phrase, at most one line per item.

### Hero

The title card of a project: what it is in one line, a few tags, an optional sketch on the
right (a `wire`), and the numbers that tell its size.

```html
<div class="hero">
  <div>
    <span class="doc-kind">CLI tool</span>
    <h1>reportgen</h1>
    <p class="lead">Turns a SQL query into a <b>shareable report</b> in one command.</p>
    <span class="tag accent">📄 PDF · CSV</span> <span class="tag ok">⏱ scheduled runs</span>
  </div>
  <div class="side"><div class="wire after"><span class="wf-label">Report</span><div class="wf-body">…</div></div></div>
  <div class="stats"><div><b>3</b><span>output formats</span></div><div><b>0</b><span>servers to run</span></div></div>
</div>
```

### Flow

Stages of a process, left to right, with arrows drawn between them (top to bottom on
phones). Each stage is a card; `alt` colors one differently, such as the step a person does.

```html
<div class="flow">
  <div><span class="tag accent">import</span><h4>Read</h4><p class="when">CSV, Excel, SQL</p><ul><li>types detected</li></ul></div>
  <div class="alt"><span class="tag note">you</span><h4>Review</h4><p class="when">in the browser</p><div class="foot"><span class="btn ok">✅ Approve</span></div></div>
  <div><span class="tag accent">export</span><h4>Publish</h4><p class="when">PDF and a link</p></div>
</div>
```

### Cards

A grid of features, commands or components, one card each: an `ico` (an emoji), a name, a
`when` line, one line of what it gives, and a `foot` with a tag. `group` is a heading with a
rule that separates two grids. Set `style="--cols:N"` to the number of cards (or half of it)
so no card is left alone in a row; without it the grid fills as many columns as fit.

```html
<div class="group">📄 Commands</div>
<div class="cards" style="--cols:3">
  <div><span class="ico">🚀</span><h4><code>run</code></h4><p class="when">once, now</p><p>runs the query and writes the report</p><div class="foot"><span class="tag accent">manual</span></div></div>
  …
</div>
```

### Before / after

```html
<div class="versus">
  <div class="before"><h4><span class="tag bad">Without</span></h4><ul><li>reports pasted into email by hand</li></ul></div>
  <div class="after"><h4><span class="tag ok">With reportgen</span></h4><ul><li>one command, the same link every week</li></ul></div>
</div>
```

The items get ✗ and ✓ by themselves. Pair them: the n-th "after" answers the n-th "before".

### Which one, when

A situation on the left, the answer on the right. `then` is accent by default; `note`, `ok`
and `muted` give the other colors, such as "you start it", "automatic", "nothing to do".

```html
<div class="pick">
  <div class="if">A one-off report for today</div><div class="then">run <small>manual</small></div>
  <div class="if">The same report every Monday</div><div class="then ok">schedule <small>automatic</small></div>
</div>
```

### Settings

Options as they look in a settings screen: a `toggle` (add `off` for a switch that is off),
a `seg` with the `on` choice, or a `tag` such as "always on". `fixed` marks one that can't be
changed. `--cols` works as in Cards.

```html
<div class="settings" style="--cols:2">
  <div class="setting"><h4>Email the link</h4><p>after every scheduled run</p><span class="toggle"></span></div>
  <div class="setting"><h4>Format</h4><p>the default output</p><span class="seg"><span class="on">PDF</span><span>CSV</span></span></div>
</div>
```

### Buttons and a strip

`btn` draws a button as it looks in the product (`ok`, `warn`, `primary`), for showing what
a person clicks. `strip` is a one-line band with a `lbl`, for a loop or a rule that applies
to everything above it.

```html
<div class="strip"><span class="lbl">On every page</span> comment · <span class="btn ok">✅ Approve</span> → <span class="btn primary">Copy feedback</span></div>
```
