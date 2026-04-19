---
name: feature-pointer
version: 2.0.0
description: "Point to a UI feature on the current browser page. Takes a screenshot, draws a green arrow + callout on the element, and shows the annotated image inline. Invoke with /feature-pointer or /feature-pointer 'element description'. Trigger automatically after any UI deploy."
metadata:
  category: ui-verification
  requires: [python, pillow]
---

# Feature Pointer

You are running the `/feature-pointer` skill. Your job: take a screenshot of the browser, find the target element, annotate it with a green arrow, and show the result inline. Be conversational — ask one question if needed, then execute.

---

## Step 1 — Figure out what to point to

Check the conversation for context. The user may have:
- Just deployed a feature ("I added a toggle", "the new button is live")
- Passed an argument after `/feature-pointer` ("show me the export button")
- Said nothing specific

**If it's clear** from context what element to highlight: proceed silently.

**If it's ambiguous**: ask ONE short question — "What element should I point to?" — then wait for the answer before continuing.

---

## Step 2 — Take a screenshot

Use Orellius to capture the current browser state:

```
mcp__orellius-browser-bridge__computer action=screenshot
```

Then save a clean copy using playwright so you have a file on disk:

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 516, 'height': 844})
    page.goto('<current page URL>')
    page.wait_for_timeout(2000)
    page.screenshot(path='C:/Users/raviv/Downloads/fp-raw.png')
    browser.close()
```

**If Orellius is not connected**: ask the user to paste a screenshot, save it as `C:\Users\raviv\Downloads\fp-raw.png`, then continue to Step 3.

---

## Step 3 — Find the element's bounding box

Try these in order, stop when you get coordinates:

**Option A** — JavaScript getBoundingClientRect (most reliable):
```javascript
// via mcp__orellius-browser-bridge__javascript_tool
const el = document.querySelector('#element-id') || document.querySelector('[data-label="..."]');
const r = el.getBoundingClientRect();
JSON.stringify({x1: Math.round(r.left), y1: Math.round(r.top), x2: Math.round(r.right), y2: Math.round(r.bottom)});
```

**Option B** — Orellius find by text:
```
mcp__orellius-browser-bridge__find text="button label or element text"
```

**Option C** — Visual estimate from the screenshot (use as fallback if DOM query fails).

---

## Step 4 — Annotate

Run annotate.py with the bounding box you found:

```bash
python "C:\Users\raviv\.claude\skills\feature-pointer\annotate.py" \
  --input "C:\Users\raviv\Downloads\fp-raw.png" \
  --region <x1> <y1> <x2> <y2> \
  --label "<short description of the feature>" \
  --output "C:\Users\raviv\Downloads\fp-annotated.png"
```

Or with a center point if you only have that:

```bash
python "C:\Users\raviv\.claude\skills\feature-pointer\annotate.py" \
  --input "C:\Users\raviv\Downloads\fp-raw.png" \
  --x <cx> --y <cy> \
  --label "<short description>" \
  --output "C:\Users\raviv\Downloads\fp-annotated.png"
```

---

## Step 5 — Show it

```
Read C:\Users\raviv\Downloads\fp-annotated.png
```

Display the image inline. **Do NOT** just say "saved to X path" — show the actual image.

After showing it, say one sentence about what you highlighted and how to interact with it.

---

## annotate.py flags

| Flag | Description |
|------|-------------|
| `--input` | Source screenshot path |
| `--output` | Output path for annotated image |
| `--label` | Text shown in the green callout box |
| `--x --y` | Center point (integer pixels) |
| `--region x1 y1 x2 y2` | Bounding box (preferred) |

---

## Notes

- The skill junction is at `C:\Users\raviv\.claude\skills\feature-pointer\` pointing to `E:\FromC\projects\feature-pointer`
- Always use the junction path when invoking annotate.py so it works from any working directory
- Label text should be short and descriptive: "New: Posts / Videos toggle" not "This is the new toggle that was added"
- If the callout box overlaps the element, annotate.py auto-repositions it above or below

## Requirements

```bash
pip install Pillow
```

Python 3.8+, playwright (`pip install playwright && playwright install chromium`).
