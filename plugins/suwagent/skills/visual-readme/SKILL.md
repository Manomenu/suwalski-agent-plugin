---
name: visual-readme
description: Rewrite the repository's README so it is told in pictures, the way a visual recap is, instead of walls of text. The pictures are panels on a board page (hero, before/after, how it works, features, which one when, settings) built from the suwagent visual blocks, rendered to light and dark PNGs that GitHub switches with the reader's theme, and redrawn from the same source whenever the project changes. Text stays only where people copy it or search for it (install, commands, configuration, troubleshooting). Start it only when the user explicitly asks for it (by name or by plain words), never on your own initiative.
argument-hint: "[what to stress, or the audience]"
---

# Visual README

Make the README look like a visual recap: a reader who opens the repository understands in
30 seconds what the project is, why it exists and how it works, from pictures, and finds the
commands to copy right under them. GitHub can't show HTML, CSS or scripts in a README, so
the visual parts are drawn on a **board** page with the visual document styles and rendered
to PNGs; the README shows them and keeps the text that must stay text.

Read first:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`, especially "Boards: pages that become pictures"
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`, especially "Picture blocks"

What to stress: $ARGUMENTS

## 1. Understand the project, once

Read the current README, the manifest (`package.json`, `pyproject.toml`, `Cargo.toml`,
`plugin.json`…), the entry points, the commands or API a user meets first, the
configuration, the license and `docs/`. Run the project's `--help` or its main command if
that's cheap. Take notes **at the level of the reader**: what it is in one line, who it is
for, the problem it removes, the 3-5 things it does, how a first use goes, what can be
configured, what it needs. Check every claim against the code and the official docs of the
tools it depends on (install commands, flags, menu names), not against the old README.

## 2. Choose the panels

One panel per question a newcomer asks, usually 4-7. Pick from these and drop what the
project has nothing for:

| Panel (section id) | Answers | Blocks |
| :- | :- | :- |
| `hero` | what is it? | `hero`: one-line pitch, tags, a sketch, `stats` |
| `why` | why would I use it? | `versus`: without / with, paired items |
| `flow` | how does it work? | `flow` stages, a `strip`, a `term` with real output |
| `features` | what does it give me? | `cards` in `group`s |
| `choose` | which part do I use when? | `pick` |
| `settings` | what can I configure? | `settings`, `cols` for modes |
| `architecture` | how is it built? (libraries, contributors) | `flow` or `cards` with roles |

When the project has a UI, a real screenshot beats a drawn panel: shoot it with `vdoc.py
shot … --scale 2` (light and dark if the app has both) and use it in the README next to the
panels. A suwagent spec, plan or recap of the project can also give a picture:
`vdoc.py shot <page> out.png --only <data-role, such as how> --theme both --scale 2 --crop`.

## 3. Build the board

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" new board readme --title "<project> README"
```

If `docs/visual/board/readme.html` already exists, edit it instead, and run `vdoc.py
refresh` on it first so it has the current blocks. Write the panels between `<!-- CONTENT
START -->` and `<!-- CONTENT END -->`, in the README's language (the project's, not
necessarily the user's), with real names, real commands and real numbers. Keep each panel's
text short: a picture with paragraphs in it is a wall of text with extra steps. Then:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" check docs/visual/board/readme.html
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vdoc.py" render docs/visual/board/readme.html --picture
```

**Open every PNG** and fix what you see before going on: cut-off content, a card alone in a
row, a line wrapping badly, an empty area, a picture taller than about one screen.
`render --only <id>` redraws one panel.

## 4. Write the README

- Open with the `hero` picture; the `alt` text carries the project name and the pitch.
- Each picture is the `<picture>` snippet from `render --picture`, with `width="100%"`, and
  **an `alt` that holds the full text of the panel**, so screen readers, search and readers
  with images off lose nothing.
- **Text stays text** where people copy, search or follow it step by step: install and
  quick start commands, configuration keys, API and CLI references, troubleshooting,
  contributing, license. Commands never appear only in a picture.
- Under each picture, at most two or three sentences that a picture can't say. Long
  references go in `<details>`.
- Keep the parts of the old README that are still true and that someone needs; drop what
  the pictures now say. Keep the badges and links that work.
- Add a line in the development section on how the pictures are made:
  edit `docs/visual/board/readme.html`, then `vdoc.py render` it.

## 5. Check and hand over

- Every path in the README exists (pictures, links), and every command was checked against
  the code or the docs.
- Don't commit unless the user asks; the board, the PNGs and the README go in together.
- Tell the user in at most 5 lines: which panels, what text was kept or dropped, what
  wasn't verified (GitHub's rendering can only be seen after a push), and the status line.
