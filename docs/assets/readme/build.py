#!/usr/bin/env python3
"""Render the README pictures: every .panel in panels.html, light and dark, at 2x, cropped to the card.

    python3 docs/assets/readme/build.py [panel ...]

Needs Firefox (or Chrome/Chromium) and Pillow. Writes docs/assets/readme/<panel>-<light|dark>.png.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[2] / "plugins/suwagent/shared/template.html"
ZOOM = 2
WIDTH = 960 + 2 * 24
PAD = 4 * ZOOM


def page(tmp):
    style = re.search(r"<style>\s*:root.*?</style>", TEMPLATE.read_text(encoding="utf-8"), re.S)[0]
    out = Path(tmp) / "panels.html"
    out.write_text((HERE / "panels.html").read_text(encoding="utf-8").replace("<!-- TEMPLATE STYLE -->", style), encoding="utf-8")
    return out


def shoot(url, png, tmp):
    for name in ("firefox", "google-chrome", "chromium", "chromium-browser"):
        exe = shutil.which(name)
        if not exe:
            continue
        size = f"{WIDTH * ZOOM},{1400 * ZOOM}"
        if name == "firefox":
            profile = Path(tmp) / "profile"
            profile.mkdir(exist_ok=True)
            cmd = [exe, "--headless", "--profile", str(profile), f"--window-size={size}", "--screenshot", str(png), url]
        else:
            cmd = [exe, "--headless", "--hide-scrollbars", f"--user-data-dir={tmp}/chrome", f"--window-size={size}",
                   f"--screenshot={png}", url]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        return
    sys.exit("no Firefox or Chrome found")


def crop(png):
    """Cut the page background away around the card and make what is left of it transparent,
    so the card sits on GitHub's own background in either theme."""
    img = Image.open(png).convert("RGB")
    bg = Image.new("RGB", img.size, img.getpixel((1, 1)))
    mask = ImageChops.difference(img, bg).convert("L").point(lambda v: 255 if v > 2 else 0)
    l, t, r, b = mask.getbbox()
    img.putalpha(mask)
    img.crop((max(l - PAD, 0), max(t - PAD, 0), min(r + PAD, img.width), min(b + PAD, img.height))).save(png, optimize=True)


def main():
    src = (HERE / "panels.html").read_text(encoding="utf-8")
    panels = sys.argv[1:] or re.findall(r'<div class="panel" id="([\w-]+)"', src)
    with tempfile.TemporaryDirectory() as tmp:
        url = page(tmp).as_uri()
        for panel in panels:
            for theme in ("light", "dark"):
                png = HERE / f"{panel}-{theme}.png"
                shoot(f"{url}#only={panel}&theme={theme}&zoom={ZOOM}", png, tmp)
                crop(png)
                print(png.relative_to(HERE.parents[2]), Image.open(png).size)


if __name__ == "__main__":
    main()
