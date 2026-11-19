#!/usr/bin/env python3
"""
protect_widget.py
-----------------
widget_src/ (editable) ko PROTECT karke app ke assets me daalta hai.

- JS: javascript-obfuscator (npm) se obfuscate — agar available ho.
      Nahi to basic minify (comments/whitespace strip) fallback.
- CSS/HTML: basic minify.

Chalane ka tareeka (project folder me):
    python3 protect_widget.py

Edit hamesha widget_src/ me karo. App assets/widgets/ ka use karta hai.
"""

import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "widget_src")
DST = os.path.join(HERE, "webview-app-template", "app", "src", "main", "assets", "widgets")


def minify_css(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)      # comments
    text = re.sub(r"\s+", " ", text)                        # whitespace
    text = re.sub(r"\s*([{}:;,])\s*", r"\1", text)
    return text.strip()


def minify_html(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)     # html comments
    text = re.sub(r">\s+<", "><", text)                    # between tags
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def basic_minify_js(text):
    # line comments (string-safe nahi — basic fallback)
    text = re.sub(r"(?<!:)//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def obfuscate_js(in_path, out_path):
    """javascript-obfuscator try karo; fail ho to basic minify."""
    try:
        subprocess.run(
            ["npx", "--yes", "javascript-obfuscator", in_path,
             "--output", out_path, "--compact", "true",
             "--self-defending", "true"],
            check=True, capture_output=True, timeout=180
        )
        return "obfuscated (javascript-obfuscator)"
    except Exception:
        with open(in_path, "r", encoding="utf-8") as f:
            js = f.read()
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(basic_minify_js(js))
        return "minified (fallback — node nahi mila; strong protection ke liye " \
               "`npm i -g javascript-obfuscator` karo)"


def process(name, fn):
    src = os.path.join(SRC, name)
    dst = os.path.join(DST, name)
    with open(src, "r", encoding="utf-8") as f:
        out = fn(f.read())
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)


def main():
    if not os.path.isdir(SRC):
        print("ERROR: widget_src/ nahi mila"); sys.exit(1)
    os.makedirs(DST, exist_ok=True)

    print("[*] widget protect kar raha hun...")
    process("widget.css", minify_css)
    print("    widget.css  -> minified")
    process("widget.html", minify_html)
    print("    widget.html -> minified")

    js_msg = obfuscate_js(os.path.join(SRC, "widget.js"),
                          os.path.join(DST, "widget.js"))
    print("    widget.js   -> " + js_msg)

    print("\nDONE ✅  Protected widget app ke assets/widgets/ me daal diya.")
    print("Ab normal build karo — widget bhi protected jayega.")


if __name__ == "__main__":
    main()
