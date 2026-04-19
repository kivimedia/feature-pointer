---
name: feature-pointer
version: 1.0.0
description: "After shipping a new UI feature, capture a browser screenshot and annotate it with a green arrow pointing to the new element. Use this skill proactively after any UI change so the user can instantly see what changed and where. Trigger phrases: 'show me where', 'point to the feature', 'annotate the screenshot', or automatically after any deploy."
metadata:
  category: ui-verification
  requires: [python, pillow]
---

# Feature Pointer

Captures the current browser state via Orellius and draws a green annotated arrow pointing to a newly deployed UI element. Eliminates "where is the new button?" questions.

## When to Use

Use this **proactively after every UI deploy** — do not wait for the user to ask. As soon as a feature is live and the page is open in Orellius, run this skill and show the annotated screenshot.

## How to Use

```
/feature-pointer
```

Or Claude invokes it automatically after shipping a UI change.

## What Claude Does

### Step 1 — Take a screenshot
Use the Orellius browser bridge to capture the current page:
```
mcp__orellius-browser-bridge__computer action=screenshot
```
Save the result bytes to `C:\Users\raviv\Downloads\fp-raw.png`.

If Orellius is not connected, ask the user to share a screenshot instead and skip to Step 3.

### Step 2 — Find the feature coordinates
Use one of:
- `mcp__orellius-browser-bridge__find` with the element's text or CSS selector to get bounding box
- Context from the conversation (e.g. "toggle at top of controls section")
- `mcp__orellius-browser-bridge__javascript_tool` to query `element.getBoundingClientRect()`

Get either:
- A **point** `(x, y)` — center of the element
- A **region** `(x1, y1, x2, y2)` — bounding box of the element (preferred when available)

### Step 3 — Annotate
```bash
python "C:\Users\raviv\.claude\skills\feature-pointer\annotate.py" \
  --input "C:\Users\raviv\Downloads\fp-raw.png" \
  --x 400 --y 285 \
  --label "New: Posts / Videos toggle" \
  --output "C:\Users\raviv\Downloads\fp-annotated.png"
```

Or with a region (more precise):
```bash
python "C:\Users\raviv\.claude\skills\feature-pointer\annotate.py" \
  --input "C:\Users\raviv\Downloads\fp-raw.png" \
  --region 466 272 620 300 \
  --label "New: Posts / Videos toggle" \
  --output "C:\Users\raviv\Downloads\fp-annotated.png"
```

### Step 4 — Show the result
```
Read C:\Users\raviv\Downloads\fp-annotated.png
```

Display the image inline. Do NOT just say "saved to X" — show it.

## annotate.py Reference

| Flag | Description |
|------|-------------|
| `--input` | Source screenshot path |
| `--output` | Output path for annotated image |
| `--label` | Text shown in the green callout box |
| `--x --y` | Center point of element (integer pixels) |
| `--region x1 y1 x2 y2` | Bounding box (preferred over point) |

## Requirements

```bash
pip install Pillow
```

Python 3.8+. No other dependencies.

## Project Location

- Local: `E:\FromC\projects\feature-pointer`
- GitHub: https://github.com/kivimedia/feature-pointer
- Skill symlink: `C:\Users\raviv\.claude\skills\feature-pointer\`
