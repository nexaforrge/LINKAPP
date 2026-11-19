#!/usr/bin/env python3
"""
LinkApp generator
-----------------
App naam + icon + link daalo, aur ek ready-to-build Android project ban jata hai
(WebView wrapper + protection kit). Phir usko Android Studio me kholke APK banao.

Example:
    python3 generate.py \
        --name "My App" \
        --url "https://example.com" \
        --icon my_logo.png \
        --package com.myname.myapp \
        --out ./MyApp

Zaroori: --icon ek PNG/JPG image honi chahiye (square best).
"""

import argparse
import os
import shutil
import sys

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webview-app-template")

# Android mipmap densities aur unke pixel size
DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def replace_in_file(path, pairs):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in pairs:
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_icons(out_dir, icon_path):
    try:
        from PIL import Image
    except ImportError:
        fail("Pillow chahiye: pip install Pillow")
    img = Image.open(icon_path).convert("RGBA")
    # square crop (center)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    res_dir = os.path.join(out_dir, "app", "src", "main", "res")
    for folder, size in DENSITIES.items():
        d = os.path.join(res_dir, folder)
        os.makedirs(d, exist_ok=True)
        img.resize((size, size), Image.LANCZOS).save(os.path.join(d, "ic_launcher.png"))
    print(f"  icon -> {len(DENSITIES)} densities me laga diya")


def main():
    ap = argparse.ArgumentParser(description="Link se protected app banao")
    ap.add_argument("--name", required=True, help="App ka naam (dikhega phone pe)")
    ap.add_argument("--url", required=True, help="Link jo app me khulega (https://...)")
    ap.add_argument("--icon", required=True, help="Icon image ka path (png/jpg)")
    ap.add_argument("--package", required=True,
                    help="Unique applicationId, jaise com.myname.myapp")
    ap.add_argument("--out", required=True, help="Output project folder")
    args = ap.parse_args()

    if not os.path.isdir(TEMPLATE_DIR):
        fail(f"template nahi mila: {TEMPLATE_DIR}")
    if not os.path.isfile(args.icon):
        fail(f"icon file nahi mili: {args.icon}")
    if not args.url.startswith(("http://", "https://")):
        fail("url https:// ya http:// se shuru hona chahiye")
    if "." not in args.package or " " in args.package:
        fail("package aisa ho: com.myname.myapp (space mat daalo)")
    if os.path.exists(args.out):
        fail(f"out folder pehle se hai, dusra naam do: {args.out}")

    # 1. template copy
    shutil.copytree(TEMPLATE_DIR, args.out)
    print(f"[1/3] project copy -> {args.out}")

    # 2. tokens replace
    pairs_all = [("__APP_NAME__", args.name),
                 ("__APP_URL__", args.url),
                 ("__APPLICATION_ID__", args.package)]
    replace_in_file(os.path.join(args.out, "app", "src", "main", "res",
                                 "values", "strings.xml"), pairs_all)
    replace_in_file(os.path.join(args.out, "app", "build.gradle"), pairs_all)
    print("[2/3] naam / link / package set")

    # 3. icon
    write_icons(args.out, args.icon)
    print("[3/3] icon done")

    print("\nDONE ✅  Ab project ready hai:", args.out)
    print("Agle steps:")
    print("  1. Android Studio me 'Open' -> ye folder select karo")
    print("  2. Release keystore banao aur env vars set karo (README dekho)")
    print("  3. TamperCheck me signature hash daalo (README step)")
    print("  4. Build > Generate Signed Bundle/APK > APK > release")


if __name__ == "__main__":
    main()
