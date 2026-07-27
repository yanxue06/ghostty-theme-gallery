#!/usr/bin/env python3
"""Re-extract theme palettes from a local Ghostty install and rewrite index.html.

Ghostty syncs its built-in themes from mbadolato/iTerm2-Color-Schemes weekly, so
the committed data goes stale. Run this after a Ghostty (or cmux) update.

    python3 scripts/extract.py                    # auto-detect the themes dir
    python3 scripts/extract.py /path/to/themes    # or point at one

Writes the palette array back into the `const RAW = [...]` line of index.html.
No dependencies.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")

CANDIDATES = [
    "/Applications/Ghostty.app/Contents/Resources/ghostty/themes",
    "/Applications/cmux.app/Contents/Resources/ghostty/themes",
    os.path.expanduser("~/.config/ghostty/themes"),
    "/usr/share/ghostty/themes",
    "/usr/local/share/ghostty/themes",
]

# Order matters: index.html reads each row positionally.
FIELDS = ["background", "foreground", "cursor-color", "cursor-text",
          "selection-background", "selection-foreground"]


def find_themes_dir(argv):
    if len(argv) > 1:
        d = os.path.expanduser(argv[1])
        if not os.path.isdir(d):
            sys.exit("not a directory: " + d)
        return d
    for d in CANDIDATES:
        if os.path.isdir(d):
            return d
    sys.exit("no themes directory found; pass one explicitly.\nTried:\n  " +
             "\n  ".join(CANDIDATES))


def parse(path):
    """Parse one Ghostty theme file into {key: value, 'palette': {int: hex}}."""
    out = {"palette": {}}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = (p.strip() for p in line.split("=", 1))
            if key == "palette":
                if "=" in val:
                    idx, colour = val.split("=", 1)
                    try:
                        out["palette"][int(idx.strip())] = colour.strip()
                    except ValueError:
                        pass
            else:
                out[key] = val
    return out


def main():
    themes_dir = find_themes_dir(sys.argv)
    rows, skipped = [], []

    for name in sorted(os.listdir(themes_dir)):
        path = os.path.join(themes_dir, name)
        if not os.path.isfile(path):
            continue
        t = parse(path)
        # A usable theme needs a background, a foreground, and all 16 ANSI slots.
        if "background" not in t or "foreground" not in t:
            skipped.append((name, "no background/foreground"))
            continue
        if not all(i in t["palette"] for i in range(16)):
            skipped.append((name, "incomplete 16-colour palette"))
            continue
        # cursor/selection are optional upstream; fall back to fg/bg.
        vals = [
            name,
            t["background"],
            t["foreground"],
            t.get("cursor-color", t["foreground"]),
            t.get("cursor-text", t["background"]),
            t.get("selection-background", t["foreground"]),
            t.get("selection-foreground", t["background"]),
            [t["palette"][i] for i in range(16)],
        ]
        rows.append(vals)

    if not rows:
        sys.exit("parsed 0 themes from " + themes_dir)

    data = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
    if "</script" in data.lower():
        sys.exit("refusing to write: theme name contains a script close tag")

    html = open(INDEX, encoding="utf-8").read()
    new, n = re.subn(r"^const RAW = .*;$", "const RAW = " + data + ";",
                     html, count=1, flags=re.M)
    if n != 1:
        sys.exit("could not find the 'const RAW = ...;' line in index.html")
    open(INDEX, "w", encoding="utf-8").write(new)

    print("themes dir : " + themes_dir)
    print("embedded   : %d themes" % len(rows))
    print("index.html : %.1f KB" % (len(new) / 1024))
    if skipped:
        print("skipped    : %d" % len(skipped))
        for name, why in skipped[:10]:
            print("    %-34s %s" % (name, why))
        if len(skipped) > 10:
            print("    ... and %d more" % (len(skipped) - 10))


if __name__ == "__main__":
    main()
