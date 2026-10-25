#!/usr/bin/env python3
"""Helper for suwagent visual documents (visual-spec, visual-plan, visual-recap).

    vdoc.py new KIND SLUG --title T [--lang pl]   create docs/visual/KIND/<date>-SLUG.html from the template
    vdoc.py check PATH                            report problems that would break the page
    vdoc.py open PATH                             open the local page in the default browser
    vdoc.py links PATH                            the page's published artifact URL and its sibling documents
    vdoc.py register PATH URL                     record the published artifact in KIND/claude-artifacts.md
    vdoc.py shot URL|PATH OUT.png [--size WxH]    screenshot a page with an installed headless browser

Standard library only, so it runs wherever python3 does.
"""

import argparse
import datetime
import html
import json
import re
import shutil
import subprocess
import tempfile
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
IMG_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"')
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
    source = html.escape(dest.as_posix())
    text = text.replace('<html lang="en" data-lang="en" data-kind="plan" data-source="">',
                        f'<html lang="{a.lang}" data-lang="{a.lang}" data-kind="{a.kind}" data-source="{source}">', 1)
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
    images = []
    for src in IMG_RE.findall(body):
        if src.startswith(("data:", "http://", "https://")):
            continue
        if not (path.parent / src).is_file():
            errors.append(f"image {src} does not exist next to the page")
        else:
            images.append(src)
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


def cmd_shot(a):
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    url = a.target if "://" in a.target else Path(a.target).resolve().as_uri()
    w, h = (int(x) for x in a.size.lower().split("x"))
    kind, exe = find_browser(a.browser)
    with tempfile.TemporaryDirectory() as tmp:
        if kind == "chrome":
            # --screenshot writes screenshot.png into the working directory (Chrome Headless CLI reference).
            cmd = [exe, "--headless", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/profile",
                   f"--window-size={w},{h}", f"--virtual-time-budget={a.wait * 1000}", "--screenshot", url]
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
    print(f"{out} ({w}x{h}, {Path(exe).name})")


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
    sh = sub.add_parser("shot")
    sh.add_argument("target", help="a URL (http://localhost:5173/reports) or a local .html file")
    sh.add_argument("out", help="the PNG to write, such as docs/visual/recap/img/2026-10-25-export-csv-1.png")
    sh.add_argument("--size", default="1280x800", help="viewport WxH; 1280x800 for desktop, 390x844 for a phone")
    sh.add_argument("--browser", choices=("chrome", "firefox"), help="default: the first one found, Chrome-family first")
    sh.add_argument("--wait", type=int, default=3, help="seconds of page time for scripts to render (Chrome)")
    sh.set_defaults(fn=cmd_shot)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
