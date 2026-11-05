#!/usr/bin/env python3
"""Helper for suwagent visual documents (visual-spec, visual-plan, visual-recap, visual-deviation, visual-qa,
visual-guardrails, visual-review-spec, agent-review) and boards.

    vdoc.py new KIND SLUG --title T [--lang pl]   create docs/visual/KIND/<date>-SLUG.html from the template
                                                  (KIND board: docs/visual/board/SLUG.html, a page of picture panels)
    vdoc.py check PATH                            report problems that would break the page
    vdoc.py open PATH                             open the local page in the default browser
    vdoc.py links PATH                            the page's published artifact URL and its sibling documents
    vdoc.py register PATH URL                     record the published artifact in KIND/claude-artifacts.md
    vdoc.py refresh PATH                          give an older page the current template's CSS and JS, content kept
    vdoc.py ids SPEC [--feature F]                give each acceptance criterion of a spec its id AC-F-<n>, never reused
    vdoc.py criteria --config criteria.json [ID]  trace each criterion of a project's specs to the guardrails naming its id
    vdoc.py spec-delta [--base REF] [--into PAGE]  what this task changed in the living specs, from the merge-base;
                                                  --into fills a review-spec page with it
    vdoc.py shot URL|PATH OUT.png [--size WxH]    screenshot a page with an installed headless browser
         [--only ID] [--theme T] [--scale N] [--crop]   one section of a suwagent page, themed, sharp, trimmed
    vdoc.py render PATH [OUTDIR] [--picture]      every <section id> of a page as <id>-light.png and <id>-dark.png

Standard library only, so it runs wherever python3 does.
"""

import argparse
import datetime
import hashlib
import html
import json
import re
import shutil
import struct
import subprocess
import tempfile
import sys
import webbrowser
import zlib
from array import array
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "shared" / "template.html"
KINDS = ("spec", "plan", "recap", "deviation", "qa", "guardrails", "review", "review-spec")
LABELS = {"qa": "QA", "review-spec": "Review spec"}  # nav link text where capitalize() would read wrong
BOARD = "board"
REGISTRY = "claude-artifacts.md"
CONTENT_RE = re.compile(r"(<!-- CONTENT START -->)(.*?)(<!-- CONTENT END -->)", re.S)
RAW_RE = re.compile(r'<script type="text/x-(code|mermaid)"([^>]*)>(.*?)</script>', re.S)
ATTR_RE = re.compile(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')')
ROW_RE = re.compile(r"^\| (?P<title>.*?) \| \[(?P<file>[^\]]+)\]\([^)]*\) \| <?(?P<url>https://[^ >|]+)>? \| (?P<date>[^|]*?) \|$")
ARTIFACT_URL_RE = re.compile(r"^https://claude\.ai/(?:code/)?artifact/[\w-]+$")
IMG_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"')
# A criterion's id, AC-<feature>-<n>: guardrails (tests, lint rules) name it, so code and spec stay traceable.
AC_RE = re.compile(r"\bAC-[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*-\d+\b")
ACCEPTANCE_RE = re.compile(r'(<section\b[^>]*data-role="acceptance"[^>]*>)(.*?)(</section>)', re.S)
LI_RE = re.compile(r"(<li\b[^>]*>)(.*?)(</li>)", re.S)
SECTION_RE = re.compile(r"<section\b([^>]*)>(.*?)</section>", re.S)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>")
# A part of a review-spec page the author still has to write; `check` fails while one is left.
WRITE_MARK = "<!-- WRITE"
BASE_REFS = ("origin/HEAD", "origin/main", "origin/master", "main", "master")
DELTA_TEXT = {
    "en": {
        "kind": "Review spec", "base": "Base", "head": "Head", "branch": "Branch", "uncommitted": "uncommitted changes",
        "tldr": "TL;DR", "write_tldr": "2-4 sentences: what this task does to the specs and what the reviewer must judge",
        "new": "🆕 New spec: {}", "new_note": "The whole spec as it stands on this branch. It did not exist before this task.",
        "changed": "✏️ Changed spec: {}", "changed_note": "Only what this task changes; the rest of the spec stays as committed at the base.",
        "removed": "🗑️ Removed spec: {}", "removed_note": "This task removes the whole spec.",
        "what": "What changed and why: {}", "write_what": "in plain words: which behaviour changes, why, and what stays as it was",
        "write_removed": "why the spec goes, and where its behaviour went",
        "criteria": "Criteria: {}", "id": "Criterion", "change": "Change", "was": "Was", "now": "Now",
        "added": "added", "reworded": "changed", "dropped": "dropped",
        "pictures": "New diagrams and images: {}",
    },
    "pl": {
        "kind": "Review spec", "base": "Baza", "head": "Stan", "branch": "Branch", "uncommitted": "niezacommitowane zmiany",
        "tldr": "TL;DR", "write_tldr": "2-4 zdania: co ten task zmienia w speckach i co recenzent ma ocenić",
        "new": "🆕 Nowa specyfikacja: {}", "new_note": "Cała specyfikacja w stanie z tego brancha. Przed tym taskiem jej nie było.",
        "changed": "✏️ Zmieniona specyfikacja: {}", "changed_note": "Tylko to, co zmienia ten task; reszta specyfikacji jest taka, jak w zacommitowanej bazie.",
        "removed": "🗑️ Usunięta specyfikacja: {}", "removed_note": "Ten task usuwa całą specyfikację.",
        "what": "Co się zmieniło i dlaczego: {}", "write_what": "prostymi słowami: które zachowanie się zmienia, dlaczego i co zostaje bez zmian",
        "write_removed": "dlaczego specyfikacja znika i dokąd przeszło jej zachowanie",
        "criteria": "Kryteria: {}", "id": "Kryterium", "change": "Zmiana", "was": "Było", "now": "Jest",
        "added": "nowe", "reworded": "zmienione", "dropped": "usunięte",
        "pictures": "Nowe schematy i obrazy: {}",
    },
}
CHROMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge", "msedge",
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
           r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
FIREFOXES = ("firefox", "/Applications/Firefox.app/Contents/MacOS/firefox", r"C:\Program Files\Mozilla Firefox\firefox.exe")

# Sections each kind is expected to have, matched against <section data-role="...">.
EXPECTED = {
    "spec": ["tldr", "problem", "goals", "behaviour", "acceptance", "questions"],
    "plan": ["tldr", "approach", "files", "steps", "verification", "questions"],
    "recap": ["tldr", "how", "acceptance", "review"],
    "deviation": ["tldr", "deviations"],
    "qa": ["tldr", "environment", "scenarios", "results"],
    "guardrails": ["tldr", "gate", "coverage"],
    "review": ["tldr", "findings"],
    "review-spec": ["tldr"],
}


def attrs(raw):
    return {m[1]: html.unescape(m[2] if m[2] is not None else m[3]) for m in ATTR_RE.finditer(raw)}


def kind_of(path):
    """The document kind is the name of the folder it sits in: docs/visual/<kind>/<file>.html."""
    kind = path.resolve().parent.name
    if kind not in KINDS:
        sys.exit(f"{path} is not in a docs/visual/<{'|'.join(KINDS)}>/ folder")
    return kind


def read_registry(folder):
    """Rows of folder/claude-artifacts.md as {file: {title, url, date}}, in file order."""
    reg = folder / REGISTRY
    rows = {}
    if reg.exists():
        for line in reg.read_text(encoding="utf-8").splitlines():
            m = ROW_RE.match(line.strip())
            if m:
                rows[m["file"]] = {"title": m["title"], "url": m["url"], "date": m["date"].strip()}
    return rows


def write_registry(folder, rows):
    kind = folder.name
    lines = [
        f"# Claude artifacts: {kind}",
        "",
        f"Published claude.ai artifact of each {kind} document in this folder. The local `.html` file is the",
        "source; the artifact is its published copy. Maintained by `vdoc.py register`, so edit with care.",
        "",
        "| Document | File | Artifact | Updated |",
        "| :- | :- | :- | :- |",
    ]
    for file, r in sorted(rows.items()):
        title = r["title"].replace("|", "\\|")
        lines.append(f"| {title} | [{file}]({file}) | <{r['url']}> | {r['date']} |")
    (folder / REGISTRY).write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_new(a):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", a.slug):
        sys.exit("SLUG must be kebab-case, such as export-csv")
    root = Path(a.root)
    # A document of another kind for the same work keeps its date, so siblings share one file name.
    existing = [] if a.kind == BOARD else sorted(root.glob(f"*/????-??-??-{a.slug}.html"))
    date = existing[0].name[:10] if existing else (a.date or datetime.date.today().isoformat())
    # A board is a living source that is rendered again whenever it changes, so it has no date.
    dest = root / a.kind / (f"{a.slug}.html" if a.kind == BOARD else f"{date}-{a.slug}.html")
    if dest.exists() and not a.force:
        sys.exit(f"{dest} already exists; edit it, or pass --force to start over")
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("<title>TITLE</title>", f"<title>{html.escape(a.title)}</title>", 1)
    source = html.escape(dest.as_posix())
    text = text.replace('<html lang="en" data-lang="en" data-kind="plan" data-source="">',
                        f'<html lang="{a.lang}" data-lang="{a.lang}" data-kind="{a.kind}" data-source="{source}">', 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(f"created {dest}")
    if a.kind == BOARD:
        print("next: put one <section id=\"…\"> per picture between <!-- CONTENT START --> and <!-- CONTENT END -->,"
              " then `vdoc.py render` it")
        return
    if a.kind == "review-spec":
        print(f"next: `vdoc.py spec-delta --into {dest.as_posix()}` writes the body")
        return
    print("next: replace the empty line between <!-- CONTENT START --> and <!-- CONTENT END --> with the document body")
    if existing:
        print("siblings for the header nav: run `vdoc.py links` on the new file")


def cmd_refresh(a):
    """Swap the page's frame (CSS, JS) for the current template's, keeping its <html> tag, title and content."""
    path = Path(a.path)
    old = path.read_text(encoding="utf-8")
    content = CONTENT_RE.search(old)
    if not content:
        sys.exit(f"{path}: CONTENT START/END markers are missing, so the content can't be told from the frame")
    text = TEMPLATE.read_text(encoding="utf-8")
    for pattern in (r"<html\b[^>]*>", r"<title>.*?</title>"):
        text = re.sub(pattern, lambda m: re.search(pattern, old, re.S)[0], text, count=1, flags=re.S)
    text = CONTENT_RE.sub(lambda m: content[0], text, count=1)
    path.write_text(text, encoding="utf-8")
    print(f"refreshed {path} from {TEMPLATE.name}" + ("" if text != old else " (already current)"))


def criteria(text):
    """The <li> items of a spec's acceptance section, as (opening tag, inner HTML) pairs; None without the section."""
    m = ACCEPTANCE_RE.search(text)
    return None if not m else [(li[1], li[2]) for li in LI_RE.finditer(m[2])]


def plain(inner, limit=60):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()[:limit]


def used_ids(folder, feature):
    """Every number of AC-<feature>-<n> in the specs of the folder, and in their git history: a dropped criterion keeps its id."""
    pattern = re.compile(rf"\bAC-{re.escape(feature)}-(\d+)\b")
    found = set()
    for spec in folder.glob("*.html"):
        found |= {int(n) for n in pattern.findall(spec.read_text(encoding="utf-8"))}
    try:
        log = subprocess.run(["git", "log", "--all", "-p", "--", "."], cwd=folder, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", check=False).stdout
        found |= {int(n) for n in pattern.findall(log)}
    except OSError:
        pass
    return found


def cmd_ids(a):
    path = Path(a.path)
    text = path.read_text(encoding="utf-8")
    feature = a.feature or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*", feature):
        sys.exit(f'"{feature}" cannot be the feature of an id: pass --feature with kebab-case words starting with a letter')
    if criteria(text) is None:
        sys.exit('no <section data-role="acceptance">: write the criteria as <li> items of it first')
    taken = used_ids(path.parent, feature)
    assigned = []

    def number(li):
        if AC_RE.search(li[2]):
            return li[0]
        n = max(taken, default=0) + 1
        taken.add(n)
        assigned.append(f"AC-{feature}-{n}  {plain(li[2])}")
        return f"{li[1]}<code>AC-{feature}-{n}</code> {li[2].lstrip()}{li[3]}"

    section = ACCEPTANCE_RE.search(text)
    text = text[:section.start(2)] + LI_RE.sub(number, section[2]) + text[section.end(2):]
    path.write_text(text, encoding="utf-8")
    print("\n".join(assigned) if assigned else "every criterion already has its id")


def spec_problems(path, text):
    """Errors in a spec's criteria: each has exactly one id, and no other spec of the folder defines it."""
    items = criteria(text)
    if items is None:
        return []
    errors, mine = [], []
    for _, inner in items:
        ids = list(dict.fromkeys(AC_RE.findall(inner)))
        if not ids:
            errors.append(f'criterion without an id: "{plain(inner)}"; run `vdoc.py ids {path.as_posix()}`')
        elif len(ids) > 1:
            errors.append(f'one criterion has several ids ({" ".join(ids)}): "{plain(inner)}"; split it, one criterion per id')
        else:
            mine.append(ids[0])
    for dup in sorted({i for i in mine if mine.count(i) > 1}):
        errors.append(f"{dup} is defined twice in this spec; an id names one criterion: run `vdoc.py ids` after removing one")
    for other in sorted(path.parent.glob("*.html")):
        if other.resolve() == path.resolve():
            continue
        theirs = {AC_RE.search(inner)[0] for _, inner in (criteria(other.read_text(encoding="utf-8")) or []) if AC_RE.search(inner)}
        for dup in sorted(set(mine) & theirs):
            errors.append(f"{dup} is also defined in {other.name}; give this criterion a new id: remove it and run `vdoc.py ids`")
    return errors


def glob_re(pattern):
    """A path glob as a regex: ** spans folders, * and ? stay inside one (PurePath.full_match needs Python 3.13)."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        else:
            out += {"*": "[^/]*", "?": "[^/]"}.get(pattern[i], re.escape(pattern[i]))
            i += 1
    return re.compile(out + r"\Z")


def cmd_criteria(a):
    """Every criterion of the specs is named by a guardrail of a kind the project's config lists, and nothing else names an id."""
    root = Path(a.root).resolve()
    config = json.loads((root / a.config).read_text(encoding="utf-8"))
    specs = config["specs"].rstrip("/") + "/"
    prose = [glob_re(g) for g in config.get("prose", [])]
    kinds = [(k["kind"], [glob_re(g) for g in k["paths"]]) for k in config["kinds"]]
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root,
                            capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    paths = sorted(p for p in listed if p and (root / p).is_file())

    def read(path):
        data = (root / path).read_bytes()
        return None if b"\0" in data else data.decode("utf-8", errors="replace")

    problems, definitions, seen = [], {}, set()
    spec_paths = [p for p in paths if p.startswith(specs) and p.endswith(".html")]
    for path in spec_paths:
        items = criteria(read(path) or "")
        if items is None:
            problems.append(f'{path}: no acceptance section — add <section data-role="acceptance"> with one <li> per criterion,'
                            " each starting with its id AC-<feature>-<n>.")
            continue
        if not items:
            problems.append(f"{path}: the acceptance section has no criteria — add one <li> per criterion, each starting with its id.")
        for _, inner in items:
            ids = list(dict.fromkeys(AC_RE.findall(inner)))
            if not ids:
                problems.append(f'{path}: a criterion without an id: "{plain(inner)}" — start it with the next free'
                                " AC-<feature>-<n> (vdoc.py ids).")
            elif len(ids) > 1:
                problems.append(f'{path}: one criterion has several ids ({" ".join(ids)}): "{plain(inner)}" — split it,'
                                " one criterion per id.")
                seen |= set(ids)
            else:
                definitions.setdefault(ids[0], []).append(path)
    for cid, where in sorted(definitions.items()):
        if len(where) > 1:
            problems.append(f"{cid} is defined twice ({','.join(sorted(set(where)))}) — an id names one criterion for good:"
                            " give the newer one the next free number.")
    for path in spec_paths:
        for number, line in enumerate((read(path) or "").splitlines(), 1):
            for cid in dict.fromkeys(AC_RE.findall(line)):
                if cid not in definitions and cid not in seen:
                    problems.append(f"{path}:{number}: mentions {cid}, which no acceptance section defines — define it there"
                                    " or remove the mention.")

    trace = []
    for path in paths:
        if path.startswith(specs) or any(g.match(path) for g in prose):
            continue
        text = read(path)
        if text is None or not AC_RE.search(text):
            continue
        kind = next((name for name, globs in kinds if any(g.match(path) for g in globs)), None)
        for number, line in enumerate(text.splitlines(), 1):
            for cid in dict.fromkeys(AC_RE.findall(line)):
                if kind is None:
                    problems.append(f"{cid} at {path}:{number}: not a guardrail — nothing the gate runs reads this file. Move"
                                    f" the id to the test, lint rule or config that proves the criterion (kinds: {a.config}).")
                elif cid not in definitions:
                    problems.append(f"{cid} at {path}:{number}: no spec defines this criterion — restore it in the spec, or"
                                    " delete or rename the guardrail's id.")
                else:
                    trace.append((cid, kind, path, number))
    guarded = {t[0] for t in trace}
    for cid in sorted(definitions):
        if cid not in guarded:
            problems.append(f"{cid}: no guardrail — name the id in a test, lint rule or config that fails when the criterion"
                            " breaks. If no automated check can prove it, ask the owner whether it becomes plain description"
                            " in the spec or leaves the spec.")
    if a.id:
        trace = [t for t in trace if t[0] == a.id]
        problems = [p for p in problems if p.startswith((f"{a.id} ", f"{a.id}:"))]
    for cid, kind, path, number in sorted(trace):
        print(f"{cid:<16} {kind:<28} {path}:{number}")
    for problem in problems:
        print(problem, file=sys.stderr)
    sys.exit(1 if problems else 0)


def git_out(cwd, *args):
    """A git command's stdout, or None when it fails or git is missing."""
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def fork_point(cwd, ref=None):
    """(ref, merge-base with HEAD): where this branch left its base. A remote ref comes first because a local master
    can lag behind what the branch already merged, and the other tasks' changes would then look like this task's."""
    for candidate in [ref] if ref else BASE_REFS:
        commit = git_out(cwd, "merge-base", "HEAD", candidate)
        if commit:
            return candidate, commit.strip()
    return None, None


def spec_body(text):
    return (CONTENT_RE.search(text) or [None, None, text])[2]


def spec_sections(text):
    """A spec's sections by role, as {key: (attributes, inner HTML)}. The page frame and header don't count as its content."""
    found = {}
    for i, m in enumerate(SECTION_RE.finditer(spec_body(text))):
        at = attrs(m[1])
        key = at.get("data-role") or at.get("id") or f"section-{i + 1}"
        found[key if key not in found else f"{key}-{i + 1}"] = (m[1], m[2])
    return found


def spec_criteria(text):
    found = {}
    for _, inner in criteria(text) or []:
        cid = AC_RE.search(inner)
        if cid:
            found[cid[0]] = plain(inner, None).replace(cid[0], "", 1).strip()
    return found


def squeezed(inner):
    return re.sub(r"\s+", " ", inner).strip()


def page_title(text, fallback):
    return (re.search(r"<title>(.*?)</title>", text, re.S) or [None, fallback])[1].strip()


def spec_delta(folder, base):
    """What separates the specs in `folder` (as they are on disk) from the same folder at the commit `base`."""
    top = git_out(folder.parent, "rev-parse", "--show-toplevel")
    if top is None:
        sys.exit(f"{folder} is not in a git repository")
    rel = folder.resolve().relative_to(Path(top.strip()).resolve()).as_posix()
    listed = git_out(top.strip(), "ls-tree", "-r", "--name-only", base, "--", f"{rel}/") or ""
    at_base = {Path(p).name for p in listed.splitlines() if Path(p).parent.as_posix() == rel and p.endswith(".html")}
    on_disk = {p.name for p in folder.glob("*.html")}
    delta = []
    for name in sorted(on_disk | at_base):
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", Path(name).stem)
        now = (folder / name).read_text(encoding="utf-8") if name in on_disk else ""
        was = git_out(top.strip(), "show", f"{base}:{rel}/{name}") if name in at_base else ""
        entry = {"name": name, "path": f"{rel}/{name}", "slug": slug, "title": page_title(now or was, slug), "text": now}
        if name not in at_base:
            delta.append({**entry, "status": "new"})
            continue
        was_crit = spec_criteria(was)
        if name not in on_disk:
            delta.append({**entry, "status": "removed", "dropped": sorted(was_crit.items())})
            continue
        was_sec, now_sec = spec_sections(was), spec_sections(now)
        changed = [k for k in now_sec if k in was_sec and squeezed(now_sec[k][1]) != squeezed(was_sec[k][1])]
        if not (changed or now_sec.keys() ^ was_sec.keys()):
            continue
        now_crit = spec_criteria(now)
        old_raw = {squeezed(r[3]) for r in RAW_RE.finditer(spec_body(was)) if r[1] == "mermaid"}
        old_src = set(IMG_RE.findall(spec_body(was)))
        delta.append({
            **entry, "status": "changed",
            "sections": {"added": [k for k in now_sec if k not in was_sec], "changed": changed,
                         "removed": [k for k in was_sec if k not in now_sec]},
            "added": [(c, t) for c, t in now_crit.items() if c not in was_crit],
            "reworded": [(c, was_crit[c], t) for c, t in now_crit.items() if c in was_crit and t != was_crit[c]],
            "dropped": [(c, t) for c, t in was_crit.items() if c not in now_crit],
            "diagrams": [r[0] for r in RAW_RE.finditer(spec_body(now)) if r[1] == "mermaid" and squeezed(r[3]) not in old_raw],
            "images": [t for t in IMG_TAG_RE.findall(spec_body(now)) if IMG_RE.search(t) and IMG_RE.search(t)[1] not in old_src],
        })
    order = {"new": 0, "changed": 1, "removed": 2}
    return sorted(delta, key=lambda e: order[e["status"]])


def delta_fingerprint(delta):
    """Changes when a spec's reviewed content changes, so `check` can tell that a review-spec page went stale."""
    parts = []
    for e in delta:
        sections = spec_sections(e["text"])
        parts.append(f"{e['status']} {e['path']} " + " ".join(f"{k}={squeezed(v[1])}" for k, v in sections.items()))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def delta_lines(e):
    yield f"{e['status'].upper():<8} {e['path']}  {html.unescape(e['title'])}"
    if e["status"] == "changed":
        for c, t in e["added"]:
            yield f"  + {c}  {html.unescape(t)}"
        for c, was, now in e["reworded"]:
            yield f"  ~ {c}\n      was: {html.unescape(was)}\n      now: {html.unescape(now)}"
        for c, t in e["dropped"]:
            yield f"  - {c}  {html.unescape(t)}"
        for label, keys in e["sections"].items():
            if keys:
                yield f"  sections {label}: {', '.join(keys)}"
        if e["diagrams"]:
            yield f"  new diagrams: {len(e['diagrams'])}"
        if e["images"]:
            yield f"  new images: {', '.join(IMG_RE.search(t)[1] for t in e['images'])}"


def part_band(e, t):
    status = e["status"]
    return (f'<section class="part" data-part="{status}" data-role="part" id="{e["slug"]}-part">\n'
            f'  <h2>{t[status].format(e["title"])}</h2>\n  <p><code>{e["path"]}</code>: {t[status + "_note"]}</p>\n</section>')


def criteria_table(e, t):
    rows = [f'<tr><td><code>{c}</code></td><td><span class="tag ok">{t["added"]}</span></td><td></td><td>{x}</td></tr>' for c, x in e.get("added", [])]
    rows += [f'<tr><td><code>{c}</code></td><td><span class="tag warn">{t["reworded"]}</span></td><td>{was}</td><td>{now}</td></tr>' for c, was, now in e.get("reworded", [])]
    rows += [f'<tr><td><code>{c}</code></td><td><span class="tag bad">{t["dropped"]}</span></td><td>{x}</td><td></td></tr>' for c, x in e.get("dropped", [])]
    if not rows:
        return ""
    head = f'<tr><th>{t["id"]}</th><th>{t["change"]}</th><th>{t["was"]}</th><th>{t["now"]}</th></tr>'
    return (f'<section data-role="criteria-delta" id="{e["slug"]}-criteria">\n  <h2>{t["criteria"].format(e["title"])}</h2>\n'
            f"  <table><thead>{head}</thead><tbody>\n  " + "\n  ".join(rows) + "\n  </tbody></table>\n</section>")


def copied_sections(e):
    """A new spec's sections word for word. Only the ids change, so the sections of several specs can't collide on one page."""
    out = []
    for key, (raw, inner) in spec_sections(e["text"]).items():
        rest = re.sub(r'\s*(?<![\w-])id="[^"]*"', "", raw)
        out.append(f'<section id="{e["slug"]}-{key}"{rest}>{inner}</section>')
    return out


def copy_images(sources, page):
    """The images a page takes from a spec have to sit next to the page, under the same relative path."""
    spec_folder = page.parent.parent / "spec"
    for src in sources:
        source, target = spec_folder / src, page.parent / src
        if "://" not in src and not src.startswith("data:") and source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def review_spec_body(delta, t, ref, commit, head, dirty, branch, fingerprint, kept):
    def written(section_id, mark):
        return kept.get(section_id) or f"\n  <h2>{mark[0]}</h2>\n  <!-- WRITE: {mark[1]} -->\n"

    meta = ['<span><b>Status:</b> <span class="status draft">draft</span></span>',
            f'<span><b>{t["base"]}:</b> <code>{ref}</code> @ <code>{commit[:8]}</code></span>',
            f'<span><b>{t["head"]}:</b> <code>{head[:8]}</code>{" + " + t["uncommitted"] if dirty else ""}</span>']
    if branch:
        meta.append(f'<span><b>{t["branch"]}:</b> <code>{branch}</code></span>')
    out = [f'<header class="doc-head" data-base="{ref}" data-spec-fingerprint="{fingerprint}">\n'
           f'  <span class="doc-kind">{t["kind"]}</span>\n  <h1>TITLE_OF_PAGE</h1>\n'
           '  <div class="doc-meta">\n    ' + "\n    ".join(meta) + "\n  </div>\n</header>",
           f'<section data-role="tldr" id="tldr">{written("tldr", (t["tldr"], t["write_tldr"]))}</section>']
    for e in delta:
        out.append(part_band(e, t))
        if e["status"] == "new":
            out += copied_sections(e)
            continue
        what = f'{e["slug"]}-what'
        mark = (t["what"].format(e["title"]), t["write_removed"] if e["status"] == "removed" else t["write_what"])
        out.append(f'<section data-role="what-changed" id="{what}">{written(what, mark)}</section>')
        table = criteria_table(e, t)
        if table:
            out.append(table)
        pictures = e.get("diagrams", []) + [f'<figure class="shot"><div class="shot-img">{i}</div></figure>' for i in e.get("images", [])]
        if pictures:
            out.append(f'<section data-role="pictures" id="{e["slug"]}-pictures">\n  <h2>{t["pictures"].format(e["title"])}</h2>\n  '
                       + "\n  ".join(pictures) + "\n</section>")
    return "\n\n".join(out)


def cmd_spec_delta(a):
    page = Path(a.into) if a.into else None
    if page and kind_of(page) != "review-spec":
        sys.exit(f"{page} is not a review-spec page; create one with `vdoc.py new review-spec <task-slug>`")
    folder = page.parent.parent / "spec" if page else Path(a.root) / "spec"
    git_dir = folder.parent
    if not git_dir.is_dir():
        sys.exit(f"{git_dir} does not exist: run this from the repository root, or pass --root")
    ref, commit = fork_point(git_dir, a.base)
    if not commit:
        sys.exit(f"no merge-base with {a.base or ' or '.join(BASE_REFS)}: pass the branch this one started from as --base")
    delta = spec_delta(folder, commit)
    if not delta:
        message = f"no spec changed since {ref} @ {commit[:8]}: there is nothing for a review-spec page to show"
        if page:
            sys.exit(message)
        print(message)
        return
    print(f"base: {ref} @ {commit[:8]} (merge-base)")
    for e in delta:
        print("\n".join(delta_lines(e)))
    if not page:
        return
    text = page.read_text(encoding="utf-8")
    current = CONTENT_RE.search(text)
    if not current:
        sys.exit(f"{page}: CONTENT START/END markers are missing; recreate it with `vdoc.py new`")
    old = {attrs(m[1]).get("id"): m[2] for m in SECTION_RE.finditer(current[2])}
    kept = {k: v for k, v in old.items() if (k == "tldr" or (k or "").endswith("-what")) and WRITE_MARK not in v}
    lang = (re.search(r'data-lang="(\w+)"', text) or [None, "en"])[1]
    head = (git_out(git_dir, "rev-parse", "HEAD") or "").strip()
    dirty = bool((git_out(git_dir, "status", "--porcelain", "--", "spec") or "").strip())
    branch = (git_out(git_dir, "branch", "--show-current") or "").strip()
    body = review_spec_body(delta, DELTA_TEXT.get(lang, DELTA_TEXT["en"]), ref, commit, head, dirty, branch, delta_fingerprint(delta), kept)
    body = body.replace("TITLE_OF_PAGE", page_title(text, page.stem), 1)
    for e in delta:
        if e["status"] == "new":
            copy_images(IMG_RE.findall(spec_body(e["text"])), page)
        elif e["status"] == "changed":
            copy_images([IMG_RE.search(t)[1] for t in e["images"]], page)
    page.write_text(CONTENT_RE.sub(lambda m: f"{m[1]}\n{body}\n{m[3]}", text, count=1), encoding="utf-8")
    print(f"filled {page}" + (f"; kept the text you wrote in: {', '.join(sorted(kept))}. Check that it still holds" if kept else ""))
    if WRITE_MARK in body:
        print(f"next: replace every {WRITE_MARK} …--> with your own text, then `vdoc.py check {page.as_posix()}`")


def review_spec_problems(path, body):
    """(errors, warnings) of a review-spec page: parts left unwritten, and specs changed since the page was generated."""
    errors = [f"{body.count(WRITE_MARK)} part(s) still to write: replace each {WRITE_MARK} …--> with your text"] if WRITE_MARK in body else []
    head = re.search(r'data-base="([^"]+)" data-spec-fingerprint="([^"]+)"', body)
    if not head:
        return errors + ["the page was not generated: run `vdoc.py spec-delta --into` on it"], []
    folder = path.resolve().parent.parent / "spec"
    _, commit = fork_point(folder.parent, head[1])
    if commit and delta_fingerprint(spec_delta(folder, commit)) != head[2]:
        return errors, [f"a spec changed since this page was generated, so the reviewer would read an old state: run `vdoc.py spec-delta --base {head[1]} --into {path.as_posix()}` and publish again"]
    return errors, []


def cmd_check(a):
    path = Path(a.path)
    text = path.read_text(encoding="utf-8")
    errors, warns = [], []
    if "<title>TITLE</title>" in text:
        errors.append("the <title> is still TITLE")
    title = (re.search(r"<title>(.*?)</title>", text, re.S) or [None, ""])[1].strip()
    if ":" in title or " - " in title or len(title.split()) > 6:
        warns.append(f'title "{title}" reads like a caption; make it a short name of 2-5 words')
    m = CONTENT_RE.search(text)
    if not m:
        errors.append("CONTENT START/END markers are missing: was the template's frame edited?")
        body = text
    else:
        body = m[2]
        if not body.strip():
            errors.append("the content area is empty")
    if '<script type="module">' not in text or "feedbackText" not in text:
        errors.append("the template's script block is missing or damaged; recreate the page with `vdoc.py new`")
    kind = (re.search(r'data-kind="([\w-]+)"', text) or [None, None])[1]
    for raw in RAW_RE.finditer(body):
        at = attrs(raw[2])
        label = f"x-{raw[1]} {at.get('data-file') or ''}".strip()
        if "data-notes" in at:
            try:
                notes = json.loads(at["data-notes"])
                if not isinstance(notes, list):
                    raise ValueError("not a list")
                for n in notes:
                    if not isinstance(n, dict) or not ({"line", "lines"} & n.keys()):
                        errors.append(f"{label}: each note needs line or lines: {n}")
            except ValueError as e:
                errors.append(f"{label}: data-notes is not valid JSON ({e}); use single quotes around the attribute")
        if not raw[3].strip():
            errors.append(f"{label}: empty block")
    sections = re.findall(r"<section\b([^>]*)>", body)
    if not sections:
        errors.append("no <section> elements: every part of the document is a <section> with an <h2>")
    roles = {attrs(s).get("data-role") for s in sections}
    if kind == BOARD:
        for s in sections:
            if not attrs(s).get("id"):
                errors.append("a board <section> has no id: `render` names each picture after it")
    for role in EXPECTED.get(kind, []):
        if role not in roles:
            warns.append(f'no <section data-role="{role}">; fine only when the {kind} truly has nothing for it')
    if body.count("<section") != body.count("</section>"):
        errors.append("unbalanced <section> tags")
    for q in re.findall(r"<fieldset\b.*?</fieldset>", body, re.S):
        if "<legend" not in q:
            errors.append("a question <fieldset> has no <legend>")
    images = []
    for src in IMG_RE.findall(body):
        if src.startswith(("data:", "http://", "https://")):
            continue
        if not (path.parent / src).is_file():
            errors.append(f"image {src} does not exist next to the page")
        else:
            images.append(src)
    if kind == "spec":
        errors += spec_problems(path, body)
    if kind == "review-spec":
        found, stale = review_spec_problems(path, body)
        errors, warns = errors + found, warns + stale
    if re.search(r"<(?:html|head|body|style)[\s>]", body, re.I):
        errors.append("the content area contains <html>, <head>, <body> or <style>; use the template's classes")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    if images:
        files = {src: str(path.parent / src) for src in images}
        print("IMAGES publish them with the page, as the Artifact tool's files:", json.dumps(files, ensure_ascii=False))
    print("OK" if not errors else f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)


def cmd_open(a):
    path = Path(a.path).resolve()
    url = path.as_uri()
    opener = {"darwin": ["open"], "win32": ["cmd", "/c", "start", ""]}.get(sys.platform, ["xdg-open"])
    try:
        subprocess.Popen([*opener, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except OSError:
        webbrowser.open(url)
    print(url)


def find_browser(choice):
    """An installed headless-capable browser as (kind, executable); kind is chrome or firefox."""
    names = {"chrome": [("chrome", n) for n in CHROMES], "firefox": [("firefox", n) for n in FIREFOXES]}
    for kind, name in names.get(choice) or names["chrome"] + names["firefox"]:
        exe = shutil.which(name) or (name if Path(name).is_file() else None)
        if exe:
            return kind, exe
    sys.exit("no Chrome, Chromium, Edge or Firefox found; install one, or take the screenshot with a browser tool")


def png_read(path):
    """An 8-bit, non-interlaced RGB or RGBA PNG (what browsers write) as (width, height, RGBA rows)."""
    data = Path(path).read_bytes()
    w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", data[16:29])
    if depth != 8 or color not in (2, 6) or interlace:
        sys.exit(f"{path}: only 8-bit RGB/RGBA PNGs can be cropped")
    idat, pos = bytearray(), 8
    while pos < len(data):
        size, typ = struct.unpack(">I4s", data[pos:pos + 8])
        if typ == b"IDAT":
            idat += data[pos + 8:pos + 8 + size]
        pos += size + 12
    raw, bpp = zlib.decompress(bytes(idat)), 4 if color == 6 else 3
    stride, prev, rows = w * bpp, bytearray(w * bpp), []
    for y in range(h):
        f, cur = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                cur[i] = (cur[i] + cur[i - bpp]) & 255
        elif f == 2:
            cur = bytearray((c + p) & 255 for c, p in zip(cur, prev))
        elif f == 3:
            for i in range(stride):
                cur[i] = (cur[i] + ((cur[i - bpp] if i >= bpp else 0) + prev[i]) // 2) & 255
        elif f == 4:
            for i in range(stride):
                a, b, c = (cur[i - bpp], prev[i], prev[i - bpp]) if i >= bpp else (0, prev[i], 0)
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(cur)
        prev = cur
    if bpp == 3:
        rows = [bytearray(b"".join(bytes(r[i:i + 3]) + b"\xff" for i in range(0, stride, 3))) for r in rows]
    return w, h, rows


def png_write(path, w, rows):
    def chunk(typ, body):
        return struct.pack(">I", len(body)) + typ + body + struct.pack(">I", zlib.crc32(typ + body))
    prev, raw = bytes(w * 4), bytearray()
    for r in rows:  # filter Up: flat UI areas compress well
        raw += b"\x02" + bytes((c - p) & 255 for c, p in zip(r, prev))
        prev = r
    head = struct.pack(">IIBBBBB", w, len(rows), 8, 6, 0, 0, 0)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                           + chunk(b"IEND", b""))


def png_crop(path, pad):
    """Trim the page background (the top-left pixel's color) around the content, keep `pad` px of it,
    and make it transparent, so the picture sits on any background. False when the content reached the
    bottom edge, meaning the window was too short for it."""
    w, h, rows = png_read(path)
    r0, g0, b0 = rows[0][:3]
    # Within 3 levels of the corner color counts as background: browsers shade the window edges a little.
    near = {array("I", bytes((r, g, b, 255)))[0] for r in range(r0 - 3, r0 + 4) for g in range(g0 - 3, g0 + 4)
            for b in range(b0 - 3, b0 + 4) if max(r, g, b) < 256 and min(r, g, b) >= 0}
    px = [array("I", bytes(r)) for r in rows]
    used = [y for y, r in enumerate(px) if not near.issuperset(r)]
    if not used:
        return True
    left = min(next(x for x, v in enumerate(px[y]) if v not in near) for y in used)
    right = max(w - next(x for x, v in enumerate(reversed(px[y])) if v not in near) for y in used)
    top, bottom = max(used[0] - pad, 0), min(used[-1] + 1 + pad, h)
    left, right = max(left - pad, 0), min(right + pad, w)
    out = []
    for r in px[top:bottom]:
        r = array("I", (0 if v in near else v for v in r[left:right]))
        out.append(r.tobytes())
    png_write(path, right - left, out)
    return used[-1] < h - 1


def page_url(target, only=None, theme=None, scale=1):
    """The target as a URL. suwagent pages read these hash parameters (see template.html)."""
    url = target if "://" in target else Path(target).resolve().as_uri()
    params = [f"{k}={v}" for k, v in (("only", only), ("theme", theme), ("zoom", scale if scale != 1 else None)) if v]
    return url + ("#" + "&".join(params) if params else "")


def shoot(url, out, w, h, browser=None, wait=3):
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    kind, exe = find_browser(browser)
    with tempfile.TemporaryDirectory() as tmp:
        if kind == "chrome":
            # --screenshot writes screenshot.png into the working directory (Chrome Headless CLI reference).
            cmd = [exe, "--headless", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/profile",
                   f"--window-size={w},{h}", f"--virtual-time-budget={wait * 1000}", "--screenshot", url]
            made = Path(tmp) / "screenshot.png"
        else:
            # A fresh profile, so it runs next to the user's open Firefox.
            cmd = [exe, "--headless", "--profile", f"{tmp}/profile", f"--window-size={w},{h}", "--screenshot", str(out), url]
            (Path(tmp) / "profile").mkdir()
            made = out
        try:
            subprocess.run(cmd, cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        except subprocess.TimeoutExpired:
            sys.exit(f"{Path(exe).name} did not finish in 120 s")
        if not made.is_file():
            sys.exit(f"{Path(exe).name} made no screenshot of {url}")
        if made != out:
            shutil.move(made, out)
    return Path(exe).name


def shot_one(a, target, out, only=None, theme=None):
    w, h = (int(x) for x in a.size.lower().split("x"))
    name = shoot(page_url(target, only, theme, a.scale), out, w * a.scale, h * a.scale, a.browser, a.wait)
    fits = png_crop(out, 8 * a.scale) if a.crop else True
    print(f"{out} ({w}x{h} at {a.scale}x, {name})")
    if not fits:
        print(f"WARN  {out}: the content runs past the bottom of the window; pass a taller --size")


def cmd_shot(a):
    if (a.only or a.theme or a.scale != 1) and "://" in a.target and not a.target.startswith("file:"):
        print("note: --only, --theme and --scale work only on suwagent pages (vdoc.py new); other sites ignore them")
    for theme in ("light", "dark") if a.theme == "both" else (a.theme,):
        out = a.out if a.theme != "both" else f"{a.out.removesuffix('.png')}-{theme}.png"
        shot_one(a, a.target, out, a.only, theme)


def cmd_render(a):
    path = Path(a.path)
    body = (CONTENT_RE.search(path.read_text(encoding="utf-8")) or [None, None, ""])[2]
    ids = [attrs(s).get("id") for s in re.findall(r"<section\b([^>]*)>", body)]
    ids = [i for i in ids if i and (not a.only or i in a.only)]
    if not ids:
        sys.exit(f"{path} has no <section id=…> to render")
    outdir = Path(a.outdir or path.parent / "img" / path.stem)
    for i in ids:
        for theme in ("light", "dark"):
            shot_one(a, str(path), str(outdir / f"{i}-{theme}.png"), i, theme)
    if a.picture:
        print("\n<!-- <picture> for each panel; write the full text of the panel into alt -->")
        for i in ids:
            light, dark = (outdir / f"{i}-{t}.png" for t in ("light", "dark"))
            print(f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{dark.as_posix()}">\n'
                  f'  <img alt="" src="{light.as_posix()}" width="100%">\n</picture>\n')


def cmd_links(a):
    path = Path(a.path)
    kind = kind_of(path)
    own = read_registry(path.parent).get(path.name)
    print(f"this {kind}: " + (f"published at {own['url']} (update that artifact)" if own else "not published yet"))
    for other in KINDS:
        if other == kind:
            continue
        sib = path.parent.parent / other / path.name
        if not sib.exists():
            continue
        reg = read_registry(sib.parent).get(sib.name)
        target = reg["url"] if reg else f"../{other}/{sib.name}"
        print(f'nav {other}: <a href="{target}">{LABELS.get(other, other.capitalize())}</a>' + ("" if reg else "  (local only)"))


def cmd_register(a):
    path = Path(a.path)
    kind_of(path)
    if not path.exists():
        sys.exit(f"{path} does not exist")
    url = a.url.strip().rstrip("/")
    if not ARTIFACT_URL_RE.match(url):
        sys.exit(f"{url} is not a claude.ai artifact URL (https://claude.ai/artifact/<id>)")
    text = path.read_text(encoding="utf-8")
    title = html.unescape((re.search(r"<title>(.*?)</title>", text, re.S) or [None, path.stem])[1].strip())
    rows = read_registry(path.parent)
    old = rows.get(path.name)
    rows[path.name] = {"title": title, "url": url, "date": datetime.date.today().isoformat()}
    write_registry(path.parent, rows)
    note = "" if not old or old["url"] == url else f" (replaced {old['url']})"
    print(f"registered {path.name} → {url} in {path.parent / REGISTRY}{note}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("kind", choices=(*KINDS, BOARD))
    n.add_argument("slug", help="2-5 kebab-case words naming the work, such as export-csv")
    n.add_argument("--title", required=True, help="a short name of 2-5 words; it also names the artifact")
    n.add_argument("--lang", default="en", help="page language for the built-in labels: en or pl")
    n.add_argument("--root", default="docs/visual")
    n.add_argument("--date", help="YYYY-MM-DD; defaults to today, or to the date of a sibling document")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)
    for name, fn in (("check", cmd_check), ("open", cmd_open), ("links", cmd_links), ("refresh", cmd_refresh)):
        s = sub.add_parser(name)
        s.add_argument("path")
        s.set_defaults(fn=fn)
    i = sub.add_parser("ids")
    i.add_argument("path")
    i.add_argument("--feature", help="the feature part of AC-<feature>-<n>; defaults to the spec's slug")
    i.set_defaults(fn=cmd_ids)
    c = sub.add_parser("criteria")
    c.add_argument("id", nargs="?", help="show only this criterion, AC-<feature>-<n>")
    c.add_argument("--config", default="criteria.json", help="the project's kinds of guardrail, relative to --root")
    c.add_argument("--root", default=".", help="the repository to check")
    c.set_defaults(fn=cmd_criteria)
    d = sub.add_parser("spec-delta")
    d.add_argument("--base", help="the branch this one started from; default: origin/HEAD, origin/main, origin/master, main, master")
    d.add_argument("--root", default="docs/visual", help="the folder that holds spec/; ignored with --into, which uses the page's own")
    d.add_argument("--into", metavar="PAGE", help="fill this review-spec page; text already written in it is kept")
    d.set_defaults(fn=cmd_spec_delta)
    r = sub.add_parser("register")
    r.add_argument("path")
    r.add_argument("url")
    r.set_defaults(fn=cmd_register)
    sh = sub.add_parser("shot")
    sh.add_argument("target", help="a URL (http://localhost:5173/reports) or a local .html file")
    sh.add_argument("out", help="the PNG to write, such as docs/visual/recap/img/2026-10-25-export-csv-1.png")
    sh.add_argument("--size", default="1280x800", help="viewport WxH in CSS px; 1280x800 for desktop, 390x844 for a phone")
    sh.add_argument("--only", help="suwagent pages: show only the element with this id, or the section with this data-role (tldr, how…)")
    sh.add_argument("--theme", choices=("light", "dark", "both"), help="suwagent pages: force a theme; both writes OUT-light.png and OUT-dark.png")
    sh.add_argument("--crop", action="store_true", help="trim the page background around the content and make it transparent")
    rd = sub.add_parser("render")
    rd.add_argument("path", help="a board (vdoc.py new board) or any suwagent page whose sections have ids")
    rd.add_argument("outdir", nargs="?", help="default: img/<page name>/ next to the page")
    rd.add_argument("--only", nargs="+", help="render only these section ids")
    rd.add_argument("--size", default="1008x2400", help="viewport WxH in CSS px; the height only has to fit the tallest section")
    rd.add_argument("--picture", action="store_true", help="print a light/dark <picture> snippet for each section, for a README")
    rd.set_defaults(fn=cmd_render, crop=True)
    for s in (sh, rd):
        s.add_argument("--scale", type=int, default=1 if s is sh else 2, help="pixel density; 2 for sharp pictures")
        s.add_argument("--browser", choices=("chrome", "firefox"), help="default: the first one found, Chrome-family first")
        s.add_argument("--wait", type=int, default=3, help="seconds of page time for scripts to render (Chrome)")
    sh.set_defaults(fn=cmd_shot)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
