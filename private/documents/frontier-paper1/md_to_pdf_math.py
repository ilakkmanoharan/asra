#!/usr/bin/env python3
"""Convert markdown with LaTeX math to PDF via PyMdown MathJax + Playwright."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright
from pymdownx.arithmatex import ArithmatexExtension

ROOT = Path(__file__).resolve().parent
MD = ROOT / "asra_frontiers_hypothesis_theory_paper.md"
HTML = ROOT / "_asra_frontiers_paper.html"
PDF = ROOT / "asra_frontiers_hypothesis_theory_paper.pdf"

CSS = """
@page { size: Letter; margin: 0.75in; }
body {
  font-family: "Times New Roman", Times, serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #111;
  max-width: 7.5in;
  margin: 0 auto;
}
h1 { font-size: 18pt; margin-top: 1.2em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; margin-top: 1em; color: #1e3a5f; }
h3 { font-size: 12pt; margin-top: 0.8em; }
p, li { text-align: justify; }
code, pre { font-family: "Courier New", monospace; font-size: 9pt; }
pre { background: #f8fafc; padding: 0.5em; border: 1px solid #e2e8f0; white-space: pre-wrap; }
blockquote { border-left: 3px solid #4fd1c5; margin-left: 0; padding-left: 1em; color: #334155; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10pt; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; vertical-align: top; }
.arithmatex { overflow-x: auto; }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ASRA Frontiers Hypothesis and Theory Paper</title>
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$']],
        displayMath: [['$$', '$$']],
        processEscapes: true
      }},
      options: {{ skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }}
    }};
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
  <style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def preprocess(md: str) -> str:
    md = re.sub(r"```\w+[^\n]*\n", "```\n", md)
    return md


def md_to_html(md_path: Path, html_path: Path) -> None:
    text = preprocess(md_path.read_text(encoding="utf-8"))
    extensions = [
        "extra",
        "tables",
        "sane_lists",
        "smarty",
        ArithmatexExtension(
            generic=True,
            smart_dollar=True,
            block_tag="div",
            inline_tag="span",
        ),
    ]
    body = markdown.markdown(text, extensions=extensions)
    html_path.write_text(HTML_TEMPLATE.format(css=CSS, body=body), encoding="utf-8")


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    url = html_path.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_function(
            "() => window.MathJax && MathJax.startup && MathJax.startup.promise"
        )
        page.evaluate("() => MathJax.typesetPromise()")
        page.wait_for_timeout(2500)
        page.pdf(
            path=str(pdf_path),
            format="Letter",
            margin={"top": "0.75in", "bottom": "0.75in", "left": "0.75in", "right": "0.75in"},
            print_background=True,
        )
        browser.close()


def main() -> None:
    if not MD.is_file():
        print(f"Missing {MD}", file=sys.stderr)
        sys.exit(1)
    print("Converting markdown to HTML (MathJax)...")
    md_to_html(MD, HTML)
    print("Rendering PDF (Chromium)...")
    html_to_pdf(HTML, PDF)
    print(f"Wrote {PDF} ({PDF.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
