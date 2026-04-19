#!/usr/bin/env python3
"""
feature-pointer/annotate.py
Annotate a screenshot with a green arrow + callout pointing to a new UI feature.

Usage:
  python annotate.py --input ss.png --x 400 --y 200 --label "Posts/Videos toggle" --output annotated.png
  python annotate.py --input ss.png --region 380 185 620 215 --label "Posts/Videos toggle" --output annotated.png
"""
import argparse
import math
from PIL import Image, ImageDraw, ImageFont


def draw_arrow(draw, x1, y1, x2, y2, color, width=3, head_size=14):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    for delta in (0.45, -0.45):
        hx = x2 - head_size * math.cos(angle - delta)
        hy = y2 - head_size * math.sin(angle - delta)
        draw.line([(x2, y2), (hx, hy)], fill=color, width=width)


def annotate(input_path, output_path, label, cx=None, cy=None, region=None):
    img = Image.open(input_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    GREEN = (0, 230, 118, 255)
    DARK_BG = (18, 18, 46, 230)
    WHITE = (255, 255, 255, 255)
    RING = (0, 230, 118, 180)

    if region:
        rx1, ry1, rx2, ry2 = region
        cx = (rx1 + rx2) // 2
        cy = (ry1 + ry2) // 2
        # Draw highlight rectangle
        for offset in range(3):
            draw.rectangle(
                [rx1 - offset, ry1 - offset, rx2 + offset, ry2 + offset],
                outline=(*GREEN[:3], max(80, 200 - offset * 60)),
                width=2,
            )
        # Pulsing ring effect (3 concentric rectangles)
        for i in range(1, 4):
            draw.rectangle(
                [rx1 - i * 4, ry1 - i * 4, rx2 + i * 4, ry2 + i * 4],
                outline=(*GREEN[:3], 80 - i * 20),
                width=1,
            )
    else:
        radius = 22
        for i in range(3, 0, -1):
            draw.ellipse(
                [cx - radius - i * 5, cy - radius - i * 5,
                 cx + radius + i * 5, cy + radius + i * 5],
                outline=(*GREEN[:3], 60 - i * 15),
                width=1,
            )
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=GREEN, width=3,
        )

    # Callout box position: below-right, or above if near bottom
    box_w, box_h = 260, 42
    pad = 12
    margin = 60
    box_x = min(cx + margin, img.width - box_w - 8)
    box_y = cy + margin if cy + margin + box_h < img.height - 8 else cy - margin - box_h

    # Arrow from feature to callout
    arrow_sx = cx + (22 if region is None else (region[2] - region[0]) // 2)
    arrow_sy = cy
    arrow_ex = box_x + pad
    arrow_ey = box_y + box_h // 2
    draw_arrow(draw, arrow_sx, arrow_sy, arrow_ex, arrow_ey, GREEN, width=3, head_size=12)

    # Callout background
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=8, fill=DARK_BG, outline=GREEN, width=2,
    )

    # Label text
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    draw.text((box_x + pad, box_y + pad), label, fill=WHITE, font=font)

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path)
    print(f"Saved: {output_path}")


def main():
    p = argparse.ArgumentParser(description="Annotate a screenshot with an arrow pointing to a feature")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--x", type=int)
    p.add_argument("--y", type=int)
    p.add_argument("--region", type=int, nargs=4, metavar=("X1", "Y1", "X2", "Y2"))
    args = p.parse_args()

    if args.region:
        annotate(args.input, args.output, args.label, region=args.region)
    elif args.x is not None and args.y is not None:
        annotate(args.input, args.output, args.label, cx=args.x, cy=args.y)
    else:
        p.error("Provide either --x --y or --region x1 y1 x2 y2")


if __name__ == "__main__":
    main()
