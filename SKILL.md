---
name: feature-pointer
version: 2.1.0
description: "Point to a UI feature on the current browser page. Takes a screenshot, draws a green arrow + callout on the element, and shows the result inline. Invoke with /feature-pointer or /feature-pointer 'element description'. Trigger automatically after any UI deploy."
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

## Step 2 — Pick the annotation method

Two paths. Default to A unless you've got multiple targets across multiple pages.

### A. Live DOM injection (preferred for single-page targets)

Inject absolutely-positioned `<div>` elements over the live page via Orellius, then take an Orellius screenshot of the now-decorated page. Sharper than rasterizing arrows in PIL, no disk dance, no auth-cookie copy gymnastics, and the screenshot is taken at the page's actual viewport so coordinates from `getBoundingClientRect` line up perfectly.

The DOM nodes are local-to-tab only. Anyone else loading the page sees nothing — they're just live runtime nodes, never persisted, never committed. **Always clean up at the end** with `document.querySelectorAll('[data-fp-anno]').forEach(n=>n.remove())` so the user's own browser session doesn't get left with green boxes if they later reload.

Inject snippet (adjust label/side per target):

```javascript
// via mcp__orellius-browser-bridge__javascript_tool
(()=>{
  document.querySelectorAll('[data-fp-anno]').forEach(n=>n.remove());

  function annotate(target, label, side='right'){
    const r = target.getBoundingClientRect();
    const box = document.createElement('div');
    box.dataset.fpAnno='1';
    box.style.cssText=`position:fixed;left:${r.left-8}px;top:${r.top-8}px;width:${r.width+16}px;height:${r.height+16}px;border:4px solid #00d96c;border-radius:8px;z-index:99999;pointer-events:none;box-shadow:0 0 0 6px rgba(0,217,108,.30), 0 0 24px rgba(0,217,108,.6);`;
    document.body.appendChild(box);

    const callout = document.createElement('div');
    callout.dataset.fpAnno='1';
    callout.textContent = label; // plain text only — keep it XSS-safe
    callout.style.cssText=`position:fixed;background:#00d96c;color:#0a1428;padding:10px 14px;border-radius:8px;font:400 13px/1.4 system-ui;z-index:99999;pointer-events:none;box-shadow:0 6px 22px rgba(0,0,0,.4);max-width:380px;white-space:pre-wrap;`;
    if (side==='right') { callout.style.left=`${r.right+50}px`; callout.style.top=`${r.top+r.height/2-14}px`; }
    else if (side==='below') { callout.style.left=`${r.left}px`; callout.style.top=`${r.bottom+12}px`; }
    else { callout.style.right=`${window.innerWidth - r.left + 50}px`; callout.style.top=`${r.top+r.height/2-14}px`; }
    document.body.appendChild(callout);

    // Connector arrow line
    const arrow = document.createElement('div');
    arrow.dataset.fpAnno='1';
    const startX = side==='left' ? r.left-2 : r.right+2;
    const ax = side==='left' ? r.left-46 : r.right+46;
    arrow.style.cssText=`position:fixed;left:${Math.min(startX,ax)}px;top:${r.top+r.height/2-1.5}px;width:${Math.abs(ax-startX)}px;height:3px;background:#00d96c;z-index:99998;pointer-events:none;`;
    document.body.appendChild(arrow);
  }

  const target = document.querySelector('#element-id'); // ← put your selector here
  annotate(target, 'Short label, plain text\nNewlines are fine', 'right');
  return 'ok';
})()
```

For multi-line emphasis, use `\n` in the label string — `white-space:pre-wrap` honors line breaks. To highlight several elements at once (e.g. show the row of valid score badges around a primary one), call `annotate(...)` multiple times with thinner styles for the secondary ones.

Then take a screenshot of the live page:

```
mcp__orellius-browser-bridge__computer action=screenshot
```

The screenshot is rendered inline by the tool — that's the deliverable. After it's captured, immediately clean up:

```javascript
document.querySelectorAll('[data-fp-anno]').forEach(n=>n.remove())
```

Use this path 90% of the time. It is faster, sharper, and avoids the disk-and-auth path entirely.

### B. Disk-saved annotated PNG (use only when you need a portable artifact)

Use this when you need the annotation as a standalone image file — e.g. proving 5 features across 5 different pages in one PR description, embedding in a doc, sending to someone who isn't in this conversation. The image lives on disk, can be uploaded, attached, archived. It does NOT depend on Orellius after capture.

Sequence:

1. Take an Orellius screenshot AND save a parallel copy with playwright so you have bytes on disk:

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

If Orellius isn't connected and the page is auth-gated (so playwright lands on /login), ask the user to paste a screenshot saved as `C:\Users\raviv\Downloads\fp-raw.png` and continue.

2. Run annotate.py:

```bash
python "C:\Users\raviv\.claude\skills\feature-pointer\annotate.py" \
  --input "C:\Users\raviv\Downloads\fp-raw.png" \
  --region <x1> <y1> <x2> <y2> \
  --label "<short description>" \
  --output "C:\Users\raviv\Downloads\fp-annotated.png"
```

3. `Read C:\Users\raviv\Downloads\fp-annotated.png` to display inline.

---

## Step 3 — Find the element's bounding box

Either path needs coordinates. Try these in order:

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

For Path A (DOM injection), feed the element directly into the inject snippet — no need to round-trip the bounding box back to your code. For Path B, pass `--region x1 y1 x2 y2` to annotate.py.

---

## annotate.py flags (Path B only)

| Flag | Description |
|------|-------------|
| `--input` | Source screenshot path |
| `--output` | Output path for annotated image |
| `--label` | Text shown in the green callout box |
| `--x --y` | Center point (integer pixels) |
| `--region x1 y1 x2 y2` | Bounding box (preferred) |

---

## Notes

- The skill canonical source is at `E:\FromC\projects\feature-pointer`. The `.claude/skills/feature-pointer/` copy is loaded by Claude Code; keep both in sync after edits.
- Always use the absolute `C:\Users\raviv\.claude\skills\feature-pointer\annotate.py` path so it works from any working directory.
- Label text should be short and descriptive: "New: Posts / Videos toggle" not "This is the new toggle that was added"
- For Path A, the live page must support adding `<div>` to `document.body` (true for any normal web app). For Path B, annotate.py auto-repositions the callout if it would overlap the element.

## Requirements

Path A: Orellius connected, the page open in a tab.
Path B: Python 3.8+, `pip install Pillow`, playwright (`pip install playwright && playwright install chromium`).
