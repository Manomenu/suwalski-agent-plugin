#!/usr/bin/env python3
"""Helper for suwagent visual documents (visual-spec, visual-plan, visual-recap).

    vdoc.py new KIND SLUG --title T [--lang pl]   create docs/visual/KIND/<date>-SLUG.html from the template
    vdoc.py check PATH                            report problems that would break the page
    vdoc.py open PATH                             open the local page in the default browser
    vdoc.py links PATH                            the page's published artifact URL and its sibling documents
    vdoc.py register PATH URL                     record the published artifact in KIND/claude-artifacts.md

Standard library only, so it runs wherever python3 does.
"""

import argparse
import datetime
import html
import json
import re
import subprocess
import sys
import webbrowser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "shared" / "template.html"
KINDS = ("spec", "plan", "recap")
REGISTRY = "claude-artifacts.md"
CONTENT_RE = re.compile(r"(<!-- CONTENT START -->)(.*?)(<!-- CONTENT END -->)", re.S)
RAW_RE = re.compile(r'<script type="text/x-(code|mermaid)"([^>]*)>(.*?)</script>', re.S)
ATTR_RE = re.compile(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')')
ROW_RE = re.compile(r"^\| (?P<title>.*?) \| \[(?P<file>[^\]]+)\]\([^)]*\) \| <?(?P<url>https://[^ >|]+)>? \| (?P<date>[^|]*?) \|$")
ARTIFACT_URL_RE = re.compile(r"^https://claude\.ai/(?:code/)?artifact/[\w-]+$")

# Sections each kind is expected to have, matched against <section data-role="...">.
EXPECTED = {
    "spec": ["tldr", "problem", "goals", "behaviour", "acceptance", "questions"],
    "plan": ["tldr", "approach", "files", "steps", "verification", "questions"],
    "recap": ["tldr", "acceptance", "how", "files", "verification", "review"],
}


def attrs(raw):
    return {m[1]: html.unescape(m[2] if m[2] is not None else m[3]) for m in ATTR_RE.finditer(raw)}


def kind_of(path):
    """The document kind is the name of the folder it sits in: docs/visual/<kind>/<file>.html."""
    kind = path.resolve().parent.name
    if kind not in KINDS:
        sys.exit(f"{path} is not in a docs/visual/<spec|plan|recap>/ folder")
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
    existing = sorted(root.glob(f"*/????-??-??-{a.slug}.html"))
    date = existing[0].name[:10] if existing else (a.date or datetime.date.today().isoformat())
    dest = root / a.kind / f"{date}-{a.slug}.html"
    if dest.exists() and not a.force:
        sys.exit(f"{dest} already exists; edit it, or pass --force to start over")
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("<title>TITLE</title>", f"<title>{html.escape(a.title)}</title>", 1)
    text = text.replace('<html lang="en" data-lang="en" data-kind="plan">',
                        f'<html lang="{a.lang}" data-lang="{a.lang}" data-kind="{a.kind}">', 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(f"created {dest}")
    print("next: replace the empty line between <!-- CONTENT START --> and <!-- CONTENT END --> with the document body")
    if existing:
        print("siblings for the header nav: run `vdoc.py links` on the new file")


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
    kind = (re.search(r'data-kind="(\w+)"', text) or [None, None])[1]
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
    for role in EXPECTED.get(kind, []):
        if role not in roles:
            warns.append(f'no <section data-role="{role}">; fine only when the {kind} truly has nothing for it')
    if body.count("<section") != body.count("</section>"):
        errors.append("unbalanced <section> tags")
    for q in re.findall(r"<fieldset\b.*?</fieldset>", body, re.S):
        if "<legend" not in q:
            errors.append("a question <fieldset> has no <legend>")
    if re.search(r"<(?:html|head|body|style)[\s>]", body, re.I):
        errors.append("the content area contains <html>, <head>, <body> or <style>; use the template's classes")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
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
        print(f'nav {other}: <a href="{target}">{other.capitalize()}</a>' + ("" if reg else "  (local only)"))


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
    n.add_argument("kind", choices=KINDS)
    n.add_argument("slug", help="2-5 kebab-case words naming the work, such as export-csv")
    n.add_argument("--title", required=True, help="a short name of 2-5 words; it also names the artifact")
    n.add_argument("--lang", default="en", help="page language for the built-in labels: en or pl")
    n.add_argument("--root", default="docs/visual")
    n.add_argument("--date", help="YYYY-MM-DD; defaults to today, or to the date of a sibling document")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)
    for name, fn in (("check", cmd_check), ("open", cmd_open), ("links", cmd_links)):
        s = sub.add_parser(name)
        s.add_argument("path")
        s.set_defaults(fn=fn)
    r = sub.add_parser("register")
    r.add_argument("path")
    r.add_argument("url")
    r.set_defaults(fn=cmd_register)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
