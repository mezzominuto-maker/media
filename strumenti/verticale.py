"""Make a 1080x1920 'source' from a 16:9 interview: per-shot crop + big custom subtitles.
usage: python3 vert.py spec.json out.mp4"""
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
def font(n, s):
    for d in (FONTS, "/home/claude/clips/fonts", "/usr/share/fonts"):
        p = os.path.join(d, n)
        if os.path.exists(p): return ImageFont.truetype(p, s)
    raise SystemExit("font missing " + n)

NAVY = "0x0D1221"
spec = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
src, t0, t1 = spec["src"], spec["start"], spec["end"]
work = os.path.abspath(out + "_w"); os.makedirs(work, exist_ok=True)
VH = 1920           # full-screen band
SUB_Y = 1250

# 1) video band: per-shot segments
parts = []
for i, (a, b, mode) in enumerate(spec["shots"]):
    p = os.path.join(work, f"seg{i}.mp4")
    if mode.startswith(("fw:", "fc:")):   # sharp 1080x1600 window placed low, blurred copy fills the top
        cx = int(mode[3:])
        y0, h_ = (20, 660) if mode.startswith("fw:") else (0, 820)
        w_ = int(h_ * 1080 / 1600) // 2 * 2
        x0 = max(0, min(1920 - w_, cx - w_ // 2))
        vf = (f"crop={w_}:{h_}:{x0}:{y0},split[a][b];"
              f"[a]scale=1080:1920,boxblur=40:3,eq=brightness=-0.12[bg];"
              f"[b]scale=1080:1600:flags=lanczos[fg];[bg][fg]overlay=0:320")
    elif mode.startswith("zoom:"):  # zoom:x:y:w -> 4:3 window (w x w*3/4) scaled to the band
        _, x, y, w = mode.split(":"); w = int(w)
        vf = f"crop={w}:{w*3//4}:{x}:{y},scale=1080:{VH}"
    elif mode == "wide":
        vf = f"crop=1920:820:0:0,scale=1080:-2,pad=1080:{VH}:0:(oh-ih)/2:color={NAVY}"
    else:  # close-up: crop 1080 wide window starting at x=mode
        x = int(mode); vf = f"crop=1080:{VH}:{x}:0"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-to", str(b), "-i", src,
                    "-filter_complex", "[0:v]" + vf + ",fps=30,format=yuv420p[o]", "-map", "[o]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", p], check=True)
    parts.append(p)
lst = os.path.join(work, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
band = os.path.join(work, "band.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", band], check=True)

# 2) subtitle PNGs
f = font("Inter-Bold.otf", 46)
def wrap(text, maxw=960):
    words, lines, cur = text.split(), [], ""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
subs = []
for j, (a, b, text) in enumerate(spec["subs"]):
    lines = wrap(text); assert len(lines) <= 3, text
    im = Image.new("RGBA", (1080, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, ln in enumerate(lines):
        d.text((540, 30 + k * 57), ln, font=f, fill=(255, 255, 255), anchor="mt", stroke_width=5, stroke_fill=(0, 0, 0))
    p = os.path.join(work, f"sub{j}.png"); im.save(p); subs.append((a - t0, b - t0, p))

# 3) compose 1080x1920
inputs = ["-i", band]; fc = f"[0:v]null[v0];"
for j, (a, b, p) in enumerate(subs):
    inputs += ["-i", p]
    fc += f"[v{j}][{j+1}:v]overlay=0:{SUB_Y}:enable='between(t,{a:.2f},{b:.2f})'[v{j+1}];"
fc = fc.rstrip(";")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", fc, "-map", f"[v{len(subs)}]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "copy", out], check=True)
print("ok", out)
