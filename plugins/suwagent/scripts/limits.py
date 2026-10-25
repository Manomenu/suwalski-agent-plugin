#!/usr/bin/env python3
"""Plan usage limits for suwagent's limit-guard.

    limits.py tap [--wrap CMD]               status line command: save rate_limits, then print CMD's output
    limits.py status [--max-5h N] [--max-7d N]   OK / PAUSE / UNKNOWN from the last saved snapshot
    limits.py setup                          install the tap at a stable path and print the statusLine setting

Claude Code passes rate_limits only to the status line script, so the tap is what makes the
numbers readable for the agent. Standard library only.
"""

import argparse
import datetime
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home() / ".claude" / "suwagent"
SNAPSHOT = HOME / "rate-limits.json"
STABLE = HOME / "limits.py"
SETTINGS = Path.home() / ".claude" / "settings.json"
MAX_AGE = 15 * 60
WINDOWS = (("five_hour", "5h"), ("seven_day", "7d"))


def cmd_tap(a):
    raw = sys.stdin.read()
    # The status line must never break, so every failure here is swallowed.
    try:
        limits = json.loads(raw).get("rate_limits")
        if limits:
            HOME.mkdir(parents=True, exist_ok=True)
            tmp = SNAPSHOT.with_suffix(".tmp")
            tmp.write_text(json.dumps({"saved_at": time.time(), "rate_limits": limits}))
            os.replace(tmp, SNAPSHOT)
    except Exception:
        limits = None
    if a.wrap:
        try:
            out = subprocess.run(a.wrap, shell=True, input=raw, capture_output=True, text=True, timeout=10).stdout
            sys.stdout.write(out)
        except Exception:
            pass
    elif limits:
        parts = [f"{label} {round(limits[k]['used_percentage'])}%" for k, label in WINDOWS
                 if isinstance(limits.get(k), dict) and "used_percentage" in limits[k]]
        print(" · ".join(parts))


def when(epoch):
    t = datetime.datetime.fromtimestamp(epoch)
    return t.strftime("%H:%M") if t.date() == datetime.date.today() else t.strftime("%a %H:%M")


def cmd_status(a):
    try:
        snap = json.loads(SNAPSHOT.read_text())
    except (OSError, ValueError):
        print("UNKNOWN no usage snapshot: the status line tap isn't set up (limits.py setup), "
              "or this plan has no 5h/7d limits")
        return
    age = time.time() - snap.get("saved_at", 0)
    if age > MAX_AGE:
        print(f"UNKNOWN the last snapshot is {int(age // 60)} min old; the status line refreshes it during activity")
        return
    limits, now = snap.get("rate_limits") or {}, time.time()
    caps = {"five_hour": a.max_5h, "seven_day": a.max_7d}
    parts, over = [], []
    for key, label in WINDOWS:
        w = limits.get(key)
        if not isinstance(w, dict) or "used_percentage" not in w:
            continue
        reset = w.get("resets_at")
        if reset and reset < now:
            continue  # the window has reset since the snapshot
        pct = w["used_percentage"]
        parts.append(f"{label} {pct:.0f}%" + (f" (resets {when(reset)})" if reset else ""))
        if pct >= caps[key]:
            over.append((label, pct, caps[key], reset))
    if not parts:
        print("UNKNOWN the snapshot has no 5h/7d windows")
    elif over:
        resume = max((r for *_, r in over if r), default=None)
        why = ", ".join(f"{label} {pct:.0f}% ≥ {cap}%" for label, pct, cap, _ in over)
        wait = f"; wait {int(resume - now)} s, until {when(resume)}" if resume else ""
        print(f"PAUSE {why}{wait} · " + " · ".join(parts))
    else:
        print("OK " + " · ".join(parts))


def cmd_setup(a):
    HOME.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), STABLE)
    try:
        current = (json.loads(SETTINGS.read_text()).get("statusLine") or {}) if SETTINGS.exists() else {}
    except ValueError:
        sys.exit(f"{SETTINGS} is not valid JSON; fix it before setting up the tap")
    tap = f"python3 {shlex.quote(str(STABLE))} tap"
    existing = current.get("command", "")
    if str(STABLE) in existing:
        print(f"the tap is already in {SETTINGS}; the helper at {STABLE} was refreshed")
        return
    command = f"{tap} --wrap {shlex.quote(existing)}" if existing else tap
    new = dict(current, type="command", command=command)
    print(f"installed {STABLE}")
    print(f"current statusLine: {json.dumps(current) if current else 'none'}")
    print(f'set "statusLine" in {SETTINGS} to:')
    print(json.dumps(new, indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tap")
    t.add_argument("--wrap", help="the user's own status line command, run with the same input")
    t.set_defaults(fn=cmd_tap)
    s = sub.add_parser("status")
    s.add_argument("--max-5h", type=float, default=90)
    s.add_argument("--max-7d", type=float, default=95)
    s.set_defaults(fn=cmd_status)
    sub.add_parser("setup").set_defaults(fn=cmd_setup)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
