#!/usr/bin/env python3
"""Build signed .shortcut files and regenerate the catalog.

Shortcuts are defined in shortcuts.py as small Python programs -- a JSON
DSL would have to model control flow, which is worse than just writing it.
Everything a shortcut needs to appear in the catalog lives in its spec.

    python3 forge/build.py

Writes dist/<Name>.shortcut and rewrites the CATALOG blocks in README.md
and index.html so the two never drift apart.
"""
import os, plistlib, subprocess, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "forge", ".build")

# Read from a genuine Apple-signed shortcut. Inventing these silently gates
# off any action newer than the declared version -- it cost four debugging
# rounds once already.
CLIENT_VERSION = "5037.0.17"
MIN_VERSION = 1113

sys.path.insert(0, os.path.join(ROOT, "forge"))
from shortcuts import SHORTCUTS  # noqa: E402


def make_plist(spec):
    return {
        "WFWorkflowClientVersion": CLIENT_VERSION,
        "WFWorkflowMinimumClientVersion": MIN_VERSION,
        "WFWorkflowMinimumClientVersionString": str(MIN_VERSION),
        "WFQuickActionSurfaces": [],
        "WFWorkflowIcon": {"WFWorkflowIconStartColor": spec["color"],
                           "WFWorkflowIconGlyphNumber": spec["glyph"]},
        "WFWorkflowTypes": ["ActionExtension"],
        "WFWorkflowInputContentItemClasses": list(spec["input_types"]),
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": True,
        "WFWorkflowImportQuestions": [],
        "WFWorkflowNoInputBehavior": {
            "Name": "WFWorkflowNoInputBehaviorGetClipboard", "Parameters": {}},
        "WFWorkflowActions": spec["actions"](),
    }


def build_one(name, spec):
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    src = os.path.join(BUILD, f"{name}.shortcut")
    with open(src, "wb") as fh:
        plistlib.dump(make_plist(spec), fh)
    # The filename becomes the shortcut's name on import -- a .shortcut file
    # carries no name field of its own.
    dst = os.path.join(DIST, f"{name}.shortcut")
    subprocess.run(["shortcuts", "sign", "--mode", "anyone", "-i", src, "-o", dst],
                   check=True)
    os.chmod(dst, 0o644)
    return dst


def replace_block(path, body):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    start, end = "<!-- CATALOG:START -->", "<!-- CATALOG:END -->"
    a, b = text.find(start), text.find(end)
    if a == -1 or b == -1:
        raise SystemExit(f"{path}: missing CATALOG markers")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text[:a + len(start)] + "\n" + body + text[b:])


def href(name):
    return "dist/" + urllib.parse.quote(f"{name}.shortcut")


def main():
    built = []
    for name, spec in SHORTCUTS.items():
        path = build_one(name, spec)
        built.append(name)
        print(f"  {os.path.relpath(path, ROOT)}  ({os.path.getsize(path)} bytes)")

    rows = "\n".join(
        f"| [{n}](#{n.lower().replace(' ', '-')}) | {SHORTCUTS[n]['description']} "
        f"| [Install]({href(n)}) |" for n in built)
    replace_block(os.path.join(ROOT, "README.md"),
                  "| Shortcut | What it does | Install |\n|---|---|---|\n" + rows + "\n")

    cards = "\n".join(
        f'  <a class="row" href="{href(n)}">\n'
        f'    <img src="icon-1024.png" alt="">\n'
        f'    <div class="meta">\n'
        f'      <strong>{n}</strong>\n'
        f'      <span>{SHORTCUTS[n]["description"]}</span>\n'
        f'    </div>\n'
        f'    <span class="get">Get</span>\n'
        f'  </a>' for n in built)
    replace_block(os.path.join(ROOT, "index.html"), cards + "\n  ")
    print(f"\nRegenerated catalog in README.md and index.html ({len(built)} shortcuts)")


if __name__ == "__main__":
    main()
