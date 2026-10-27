#!/usr/bin/env python3
"""Helper for suwagent visual documents (visual-spec, visual-plan, visual-recap, visual-deviation) and boards.

    vdoc.py new KIND SLUG --title T [--lang pl]   create docs/visual/KIND/<date>-SLUG.html from the template
                                                  (KIND board: docs/visual/board/SLUG.html, a page of picture panels)
    vdoc.py check PATH                            report problems that would break the page
    vdoc.py open PATH                             open the local page in the default browser
    vdoc.py links PATH                            the page's published artifact URL and its sibling documents
    vdoc.py register PATH URL                     record the published artifact in KIND/claude-artifacts.md
    vdoc.py refresh PATH                          give an older page the current template's CSS and JS, content kept
    vdoc.py shot URL|PATH OUT.png [--size WxH]    screenshot a page with an installed headless browser
         [--only ID] [--theme T] [--scale N] [--crop]   one section of a suwagent page, themed, sharp, trimmed
    vdoc.py render PATH [OUTDIR] [--picture]      every <section id> of a page as <id>-light.png and <id>-dark.png

Standard library only, so it runs wherever python3 does.
"""

import argparse
import datetime
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
KINDS = ("spec", "plan", "recap", "deviation")
BOARD = "board"
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
    "deviation": ["tldr", "deviations"],
}


def attrs(raw):
    return {m[1]: html.unescape(m[2] if m[2] is not None else m[3]) for m in ATTR_RE.finditer(raw)}


def kind_of(path):
    """The document kind is the name of the folder it sits in: docs/visual/<kind>/<file>.html."""
    kind = path.resolve().parent.name
    if kind not in KINDS:
        sys.exit(f"{path} is not in a docs/visual/<spec|plan|recap|deviation>/ folder")
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
