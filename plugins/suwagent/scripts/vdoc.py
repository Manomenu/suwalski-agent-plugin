#!/usr/bin/env python3
"""Helper for suwagent visual documents (visual-spec, visual-plan, visual-recap).

    vdoc.py new KIND PATH --title T [--lang pl]   copy the template to PATH
    vdoc.py fill-diffs PATH [--refresh]           put `git diff` output into x-diff blocks that carry data-git
    vdoc.py check PATH                            report problems that would break the page
    vdoc.py open PATH                             open the page in the default browser

Standard library only, so it runs wherever python3 does.
"""

import argparse
import html
import json
import os
import re
import shlex
import subprocess
import sys
import webbrowser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "shared" / "template.html"
KINDS = ("spec", "plan", "recap")
CONTENT_RE = re.compile(r"(<!-- CONTENT START -->)(.*?)(<!-- CONTENT END -->)", re.S)
RAW_RE = re.compile(r'<script type="text/x-(code|diff|mermaid)"([^>]*)>(.*?)</script>', re.S)
ATTR_RE = re.compile(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')')

# Sections each kind is expected to have, matched against <section data-role="...">.
EXPECTED = {
    "spec": ["tldr", "problem", "goals", "behaviour", "acceptance", "questions"],
    "plan": ["tldr", "approach", "files", "steps", "verification", "questions"],
    "recap": ["tldr", "acceptance", "files", "changes", "verification", "review"],
}


def attrs(raw):
    return {m[1]: html.unescape(m[2] if m[2] is not None else m[3]) for m in ATTR_RE.finditer(raw)}


def cmd_new(a):
    dest = Path(a.path)
    if dest.exists() and not a.force:
        sys.exit(f"{dest} already exists; edit it, or pass --force to start over")
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("<title>TITLE</title>", f"<title>{html.escape(a.title)}</title>", 1)
    text = text.replace('<html lang="en" data-kind="plan">', f'<html lang="{a.lang}" data-kind="{a.kind}">', 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(f"created {dest.resolve()}")
    print("next: replace the empty line between <!-- CONTENT START --> and <!-- CONTENT END --> with the document body")


def cmd_fill_diffs(a):
    path = Path(a.path)
    text = path.read_text(encoding="utf-8")
    filled, problems = 0, []

    def repl(m):
        nonlocal filled
        kind, raw_attrs, body = m[1], m[2], m[3]
        at = attrs(raw_attrs)
        if kind != "diff" or "data-git" not in at or (body.strip() and not a.refresh):
            return m[0]
        args = shlex.split(at["data-git"])
        res = subprocess.run(["git", "--no-pager", "diff", "--no-color", "--no-ext-diff", *args],
                             capture_output=True, text=True, cwd=a.repo)
        if res.returncode != 0:
            problems.append(f"git diff {at['data-git']}: {res.stderr.strip()}")
            return m[0]
        out = res.stdout.rstrip("\n")
        if not out:
            problems.append(f"git diff {at['data-git']}: empty diff")
        lines = out.count("\n") + 1
        if lines > 250:
            problems.append(f"git diff {at['data-git']}: {lines} lines; narrow it (a path, -U2) to keep the tab readable")
        filled += 1
        out = re.sub(r"</script", r"<\\/script", out, flags=re.I)
        return f'<script type="text/x-{kind}"{raw_attrs}>\n{out}\n</script>'

    text = RAW_RE.sub(repl, text)
    path.write_text(text, encoding="utf-8")
    print(f"filled {filled} diff block(s) in {path}")
    for p in problems:
        print("WARN", p)


def cmd_check(a):
    path = Path(a.path)
    text = path.read_text(encoding="utf-8")
    errors, warns = [], []
    if "<title>TITLE</title>" in text:
        errors.append("the <title> is still TITLE")
    m = CONTENT_RE.search(text)
    if not m:
        errors.append("CONTENT START/END markers are missing: was the template's frame edited?")
        body = text
    else:
        body = m[2]
        if not body.strip():
            errors.append("the content area is empty")
    if '<script type="module">' not in text or "parseDiff" not in text:
        errors.append("the template's script block is missing or damaged; recreate the page with `vdoc.py new`")
    kind = (re.search(r'data-kind="(\w+)"', text) or [None, None])[1]
    for raw in RAW_RE.finditer(body):
        at = attrs(raw[2])
        label = f"x-{raw[1]} {at.get('data-file') or at.get('data-git') or ''}".strip()
        if "data-notes" in at:
            try:
                notes = json.loads(at["data-notes"])
                if not isinstance(notes, list):
                    raise ValueError("not a list")
                for n in notes:
                    if not isinstance(n, dict) or not ({"line", "lines", "old"} & n.keys()):
                        errors.append(f"{label}: each note needs line, lines or old: {n}")
            except ValueError as e:
                errors.append(f"{label}: data-notes is not valid JSON ({e}); use single quotes around the attribute")
        if not raw[3].strip():
            errors.append(f"{label}: empty block" + (" (run `vdoc.py fill-diffs`)" if "data-git" in at else ""))
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
    if re.search(r"<html|<head|<body|<style", body, re.I):
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("kind", choices=KINDS)
    n.add_argument("path")
    n.add_argument("--title", required=True)
    n.add_argument("--lang", default="en", help="page language for the built-in labels: en or pl")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)
    f = sub.add_parser("fill-diffs")
    f.add_argument("path")
    f.add_argument("--refresh", action="store_true", help="refill blocks that already have content")
    f.add_argument("--repo", default=os.getcwd(), help="git repository to diff (default: current directory)")
    f.set_defaults(fn=cmd_fill_diffs)
    c = sub.add_parser("check")
    c.add_argument("path")
    c.set_defaults(fn=cmd_check)
    o = sub.add_parser("open")
    o.add_argument("path")
    o.set_defaults(fn=cmd_open)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
