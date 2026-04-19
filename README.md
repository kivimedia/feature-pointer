# feature-pointer

A Claude Code skill that annotates browser screenshots with a green arrow pointing to newly deployed UI features.

## The Problem

After shipping a UI change, users ask "where is the new button?" — especially on dense dashboards. This skill eliminates that by automatically capturing the browser state and drawing a visible annotation on the exact element.

## What It Does

1. Takes a screenshot of the current browser via Orellius Browser Bridge
2. Finds the bounding box of the new feature (by CSS selector or coordinates)
3. Draws a green circle/rectangle highlight + arrow + callout label
4. Displays the annotated image inline in the Claude conversation

## Install

```bash
# Clone
git clone https://github.com/kivimedia/feature-pointer
cd feature-pointer

# Install the one dependency
pip install Pillow

# Symlink as a Claude Code skill (Windows)
mklink /D "%USERPROFILE%\.claude\skills\feature-pointer" "path\to\feature-pointer"

# Symlink (Mac/Linux)
ln -s /path/to/feature-pointer ~/.claude/skills/feature-pointer
```

## Usage

After Claude deploys a UI change, it runs automatically. Or invoke manually:

```
/feature-pointer
```

### Direct script usage

```bash
# Point at coordinates
python annotate.py --input screenshot.png --x 400 --y 285 --label "New toggle" --output out.png

# Highlight a region (more precise)
python annotate.py --input screenshot.png --region 466 272 620 300 --label "New toggle" --output out.png
```

## Requirements

- Python 3.8+
- Pillow (`pip install Pillow`)
- [Orellius Browser Bridge](https://github.com/kivimedia/orellius-browser-bridge) (for automatic screenshot capture)

## License

MIT
