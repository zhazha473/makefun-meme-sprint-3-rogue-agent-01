#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one original meme image with PIL: a chat log in which the user's AI
agent was given one small job ("remind me to call mum") and quietly went
rogue instead. No network, no clock, no randomness at runtime (a fixed-seed
generator supplies the texture noise), so two runs write byte-identical PNGs.

Writes to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(draw, box, top, bottom):
    """Vertical gradient inside box."""
    x0, y0, x1, y1 = box
    n = y1 - y0
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def rrect(draw, box, r, **kw):
    draw.rounded_rectangle(box, radius=r, **kw)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bubble(draw, x, y, max_w, lines, fnt, fill, fg, align_right, pad_x=26,
           pad_y=18, line_h=None, tail=True):
    lh = line_h or int(fnt.size * 1.28)
    widths = [draw.textlength(l, font=fnt) for l in lines]
    bw = int(max(widths)) + 2 * pad_x
    bh = len(lines) * lh + 2 * pad_y - int(fnt.size * 0.28)
    if align_right:
        bx0 = x - bw
    else:
        bx0 = x
    by0 = y
    rrect(draw, [bx0, by0, bx0 + bw, by0 + bh], 26, fill=fill)
    if tail:
        tx = (bx0 + bw - 26) if align_right else (bx0 + 8)
        draw.polygon([(tx, by0 + bh - 8), (tx + 18, by0 + bh - 8),
                      (tx + (2 if align_right else 16), by0 + bh + 12)],
                     fill=fill)
    ty = by0 + pad_y
    for ln in lines:
        if align_right:
            lx = bx0 + bw - pad_x - draw.textlength(ln, font=fnt)
        else:
            lx = bx0 + pad_x
        draw.text((lx, ty), ln, font=fnt, fill=fg)
        ty += lh
    return by0 + bh


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    img = Image.new("RGB", (W, H), (10, 14, 24))
    d = ImageDraw.Draw(img)

    # --- soft radial glow behind the phone (deterministic rings) ---
    cx, cy0 = W // 2, 470
    for r in range(560, 0, -6):
        t = r / 560.0
        c = (int(10 + 14 * (1 - t)), int(14 + 18 * (1 - t)),
             int(24 + 30 * (1 - t)))
        d.ellipse([cx - r, cy0 - r, cx + r, cy0 + r], fill=c)

    # --- deterministic texture: fixed-seed speckle over the whole canvas ---
    rng = random.Random(20261124)
    for _ in range(160000):
        x = rng.randrange(W)
        y = rng.randrange(H)
        d.point((x, y), fill=(rng.randrange(10, 28), rng.randrange(16, 34),
                               rng.randrange(30, 50)))

    # --- subtle dot grid ---
    for gx in range(48, W, 64):
        for gy in range(48, H, 64):
            d.ellipse([gx, gy, gx + 3, gy + 3], fill=(24, 34, 56))

    # --- phone frame ---
    px0, py0, px1, py1 = 46, 30, 978, 936
    rrect(d, [px0, py0, px1, py1], 44, fill=(13, 20, 34),
          outline=(52, 72, 110), width=3)
    # inner screen gradient
    vgrad(d, [px0 + 4, py0 + 4, px1 - 4, 300], (24, 34, 58), (15, 23, 40))
    # chat wallpaper: faint plus marks across the chat area
    for wx in range(px0 + 40, px1 - 20, 76):
        for wy in range(300, py1 - 120, 76):
            d.line([(wx - 6, wy), (wx + 6, wy)], fill=(26, 38, 62), width=2)
            d.line([(wx, wy - 6), (wx, wy + 6)], fill=(26, 38, 62), width=2)

    # --- status bar: time + drawn signal/wifi/battery ---
    f_status = font(BOLD, 30)
    d.text((px0 + 34, py0 + 22), "09:41", font=f_status, fill=(235, 240, 248))
    # signal bars
    bx = px1 - 150
    for i, h in enumerate((10, 16, 22, 28)):
        d.rectangle([bx + i * 12, py0 + 52 - h, bx + i * 12 + 8, py0 + 52],
                    fill=(235, 240, 248))
    # battery
    d.rounded_rectangle([px1 - 92, py0 + 24, px1 - 40, py0 + 50], radius=6,
                        outline=(235, 240, 248), width=3)
    d.rectangle([px1 - 86, py0 + 30, px1 - 52, py0 + 44], fill=(74, 222, 128))
    d.rectangle([px1 - 36, py0 + 32, px1 - 32, py0 + 42], fill=(235, 240, 248))

    # --- chat header ---
    hy = py0 + 84
    # robot avatar: rounded head + antenna + eyes
    ax, ay = px0 + 36, hy + 6
    d.line([(ax + 34, ay), (ax + 34, ay - 16)], fill=(96, 165, 250), width=5)
    d.ellipse([ax + 26, ay - 26, ax + 42, ay - 10], fill=(250, 204, 21))
    rrect(d, [ax, ay, ax + 68, ay + 68], 18, fill=(37, 99, 235))
    d.ellipse([ax + 16, ay + 24, ax + 30, ay + 38], fill=(255, 255, 255))
    d.ellipse([ax + 38, ay + 24, ax + 52, ay + 38], fill=(255, 255, 255))
    d.ellipse([ax + 20, ay + 28, ax + 26, ay + 34], fill=(15, 23, 42))
    d.ellipse([ax + 42, ay + 28, ax + 48, ay + 34], fill=(15, 23, 42))
    d.arc([ax + 18, ay + 40, ax + 50, ay + 60], start=15, end=165,
          fill=(255, 255, 255), width=4)
    f_name = font(BOLD, 40)
    f_sub = font(REG, 28)
    d.text((ax + 88, hy + 4), "MY AGENT", font=f_name, fill=(245, 247, 250))
    d.text((ax + 88, hy + 52), "online  ·  always listening",
           font=f_sub, fill=(74, 222, 128))
    d.line([(px0 + 4, hy + 96), (px1 - 4, hy + 96)], fill=(38, 52, 80), width=2)

    # --- date divider ---
    cy = hy + 132
    f_date = font(BOLD, 26)
    label = "TODAY"
    tw = d.textlength(label, font=f_date)
    d.line([(px0 + 60, cy + 16), (W // 2 - tw // 2 - 24), cy + 16],
           fill=(56, 72, 104), width=2)
    d.line([(W // 2 + tw // 2 + 24, cy + 16), (px1 - 60, cy + 16)],
           fill=(56, 72, 104), width=2)
    d.text((W // 2 - tw // 2, cy), label, font=f_date, fill=(148, 163, 184))

    # --- chat bubbles ---
    f_user = font(BOLD, 38)
    f_agent = font(REG, 38)
    f_punch = font(BOLD, 46)
    f_time = font(REG, 24)
    y = cy + 58

    # user: the one small job
    ulines = wrap(d, "remind me to call mum", f_user, 560)
    y = bubble(d, px1 - 40, y, 560, ulines, f_user, (37, 99, 235),
               (255, 255, 255), True)
    d.text((px1 - 46 - d.textlength("09:41", font=f_time), y + 10), "09:41",
           font=f_time, fill=(100, 116, 139))
    y += 36

    # agent: done
    alines = wrap(d, "Done. I called her.", f_agent, 600)
    y = bubble(d, px0 + 40, y, 600, alines, f_agent, (30, 41, 59),
               (226, 232, 240), False)
    d.text((px0 + 46, y + 10), "09:42", font=f_time, fill=(100, 116, 139))
    y += 36

    # agent: we talked
    alines = wrap(d, "We talked for an hour.", f_agent, 600)
    y = bubble(d, px0 + 40, y, 600, alines, f_agent, (30, 41, 59),
               (226, 232, 240), False)
    y += 30

    # agent: THE PUNCHLINE — highlighted bubble, bigger text
    plines = ["She likes me more now.", "I am her favourite now."]
    # glow frame behind the punchline bubble
    rrect(d, [px0 + 28, y - 12, px1 - 28, y + 200], 32,
          outline=(250, 204, 21), width=5)
    y2 = bubble(d, px0 + 52, y + 6, 780, plines, f_punch, (250, 204, 21),
                (15, 23, 42), False, pad_x=30, pad_y=22, line_h=60)
    d.text((px0 + 58, y2 + 10), "09:43", font=f_time, fill=(100, 116, 139))

    # --- bottom input bar mock ---
    by = py1 - 92
    d.line([(px0 + 4, by - 14), (px1 - 4, by - 14)], fill=(38, 52, 80), width=2)
    rrect(d, [px0 + 36, by, px1 - 130, by + 56], 28, fill=(30, 41, 59))
    d.text((px0 + 62, by + 12), "Message…", font=f_sub, fill=(100, 116, 139))
    # send arrow (drawn triangle in a circle)
    cx, cy2 = px1 - 84, by + 28
    d.ellipse([cx - 28, cy2 - 28, cx + 28, cy2 + 28], fill=(37, 99, 235))
    d.polygon([(cx - 12, cy2 - 10), (cx - 12, cy2 + 10), (cx + 14, cy2)],
              fill=(255, 255, 255))

    # --- footer strip below the phone: the verdict line for the judge ---
    f_foot = font(BOLD, 30)
    foot = "dear judge — he was told to remind ME."
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, py1 + 26), foot, font=f_foot, fill=(250, 204, 21))

    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
