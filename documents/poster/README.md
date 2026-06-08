# ASRA posters

Print-ready and shareable ad materials derived from project white papers.

| File | Description |
|------|-------------|
| `asra-scientific-intelligence-poster.html` | Source layout (edit this) |
| `asra-scientific-intelligence-poster.pdf` | Export — print / share |
| `asra-scientific-intelligence-poster.png` | Export — social / slides (2× retina) |

## View / export

Open in a browser:

```bash
open documents/poster/asra-scientific-intelligence-poster.html
```

**Print to PDF:** Browser → Print → Save as PDF, or regenerate exports:

```bash
python3 - <<'PY'
from pathlib import Path
from playwright.sync_api import sync_playwright
html = Path("documents/poster/asra-scientific-intelligence-poster.html").resolve()
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(viewport={"width":1000,"height":1414}, device_scale_factor=2)
    page.goto(html.as_uri(), wait_until="networkidle"); page.wait_for_timeout(1500)
    h = page.evaluate("() => Math.ceil(document.querySelector('.poster').getBoundingClientRect().height)")
    page.set_viewport_size({"width":1000,"height":max(h,1414)})
    page.pdf(path=str(html.with_suffix('.pdf')), width="1000px", height=f"{max(h,1414)}px", print_background=True, margin={"top":"0","right":"0","bottom":"0","left":"0"})
    page.locator('.poster').screenshot(path=str(html.with_suffix('.png')), type='png'); b.close()
PY
```

**Source:** `documents/from_databricks_meets_pytorch_to_keras_whitepaper.md` (Section 8 — ASRA case study).
