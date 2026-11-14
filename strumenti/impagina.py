"""Mezzo Minuto overlay for debate clips: header band, context box, end card."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts") + "/"
def font(n, s): return ImageFont.truetype(F + n, s)
from PIL import ImageFont

NAVY = (13, 18, 33)
NAVY2 = (21, 32, 53)
CREAM = (240, 236, 226)
GOLD = (208, 192, 150)      # same tone as the existing end card wordmark
AMBER = (255, 196, 61)
GREY = (170, 178, 200)
STING = os.path.join(HERE, "sting.wav")
LOGO = Image.open(os.path.join(HERE, "logo_mark.png")).convert("RGBA")

def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

def paste_logo(im, cx, cy, h):
    w = int(LOGO.width * h / LOGO.height)
    lg = LOGO.resize((w, int(h)), Image.LANCZOS)
    im.alpha_composite(lg, (int(cx - w / 2), int(cy - h / 2)))
    return w

TOP = 500          # height of the title area; video sits below it

FULL = False       # full-screen mode: video fills the frame, title sits on a dark gradient

def band_base():
    im = Image.new("RGBA", (W, TOP + (120 if FULL else 0)), (0, 0, 0, 0))
    if FULL:   # top gradient so the title reads over the video
        d = ImageDraw.Draw(im)
        for y in range(im.height):
            a = 225 if y < TOP - 40 else int(225 * (1 - (y - (TOP - 40)) / (im.height - (TOP - 40))))
            d.line([(0, y), (W, y)], fill=NAVY + (a,))
    return im

def header(cfg, path):
    """Hook title in the safe zone (y>=230, clear of TikTok/Instagram top UI)."""
    im = band_base(); d = ImageDraw.Draw(im)
    paste_logo(im, 82, 262, 56)
    d.text((122, 264), "MEZZO MINUTO", font=font("InterDisplay-Black.otf", 30), fill=GOLD, anchor="lm")
    if cfg.get("fonte"):
        d.text((W - 50, 266), "Fonte: " + cfg["fonte"], font=font("Inter-Medium.otf", 28), fill=GREY, anchor="rm")
    compact = cfg.get("compact", False)    # hook version: only a big title, no subtitle line
    ts = cfg.get("title_size", 72 if compact else 60)
    f1 = font("InterDisplay-Black.otf", ts)
    y = 306
    for line in wrap(d, cfg["title"], f1, W - 100):
        d.text((50, y), line, font=f1, fill=AMBER, anchor="la"); y += ts + 4
    if cfg.get("subtitle") and not compact:
        f2 = font("Inter-SemiBold.otf", 32)
        for line in wrap(d, cfg["subtitle"], f2, W - 100):
            d.text((50, y + 4), line, font=f2, fill=CREAM, anchor="la"); y += 40
    assert y <= TOP - 6, f"titolo troppo lungo ({y})"
    im.save(path)

def context_box(cfg, path):
    """Context card over the video, above the subtitles, clear of the right-side app buttons."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, x1 = 60, 930
    fb = font("Inter-SemiBold.otf", 34)
    blocks = [wrap(d, p, fb, x1 - x0 - 70) for p in cfg["context"]]
    n = sum(len(b) for b in blocks)
    box_h = 66 + n * 44 + (len(blocks) - 1) * 12 + 24
    y0 = cfg.get("context_y", cfg.get("context_bottom", 1325) - box_h)        # bottom edge just above the subtitles
    d.rounded_rectangle([x0, y0, x1, y0 + box_h], radius=26, fill=NAVY + (235,))
    d.rounded_rectangle([x0, y0, x0 + 12, y0 + box_h], radius=6, fill=AMBER + (255,))
    d.text((x0 + 36, y0 + 20), "IL CONTESTO", font=font("Inter-ExtraBold.otf", 30), fill=AMBER, anchor="la")
    y = y0 + 66
    for b in blocks:
        for l in b:
            d.text((x0 + 36, y), l, font=fb, fill=CREAM, anchor="la"); y += 44
        y += 12
    im.save(path)

def end_card(cfg, path):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = abs(y - H / 2) / (H / 2)
        c = tuple(int(NAVY2[i] * (1 - t) + (7, 15, 27)[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    im = im.convert("RGBA")
    paste_logo(im, W // 2, 520, 300)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 770), "MEZZO MINUTO", font=font("Inter-SemiBold.otf", 78), fill=GOLD, anchor="mm")
    # question
    fq = font("InterDisplay-Black.otf", 64)
    y = 940
    for line in wrap(d, cfg["question"], fq, W - 160):
        d.text((W // 2, y), line, font=fq, fill=CREAM, anchor="mm"); y += 78
    d.text((W // 2, y + 30), "Scrivilo nei commenti", font=font("Inter-SemiBold.otf", 42), fill=AMBER, anchor="mm")
    d.text((W // 2, 1400), "— Iscriviti! —", font=font("Inter-Bold.otf", 36), fill=CREAM, anchor="mm")
    d.text((W // 2, 1452), "Segui per informarti sulla politica", font=font("Inter-Medium.otf", 34), fill=GREY, anchor="mm")
    im.convert("RGB").save(path)

def background(path):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] * (1 - k) + NAVY2[i] * k) for i in range(3)))
    im.save(path)

def build(cfg, src, out, workdir):
    os.makedirs(workdir, exist_ok=True)
    h, c, e, b = (os.path.join(workdir, n) for n in ("header.png", "context.png", "end.png", "bg.png"))
    cut, end_len, c0 = cfg["content_end"], cfg["end_len"], cfg["context_start"]
    ct = cfg.get("crop_top", 0)            # source rows to drop at the top (TV ticker...)
    cb = cfg.get("crop_bottom", H)         # last source row kept (drop bars at the bottom)
    sub_y = cfg.get("sub_y", 1300)         # where the burned-in subtitles sit in the source
    global FULL
    FULL = cfg.get("full", False)
    FY = cfg.get("full_y") if FULL else None
    if FY is not None:   # full width from y=FY down, blurred copy of the video above (faces clear of the title)
        s = cfg["full_s"]; bt = cfg["band_top"]
        bh = int(round((H - FY) / s))
        vw, vh = int(W * s) // 2 * 2, H - FY
        top_y = FY
        cfg.setdefault("context_bottom", int(FY + (sub_y - 65 - bt) * s - 20))
    elif FULL:   # cover the whole 1080x1920 frame with the kept source rows
        s = H / (cb - ct)
        vw, vh = int(W * s) // 2 * 2, H
        top_y = 0
        cfg.setdefault("context_bottom", int((sub_y - 65 - ct) * s - 20))
    else:
        s = min((H - TOP) / (cb - ct), (1440 - TOP) / (sub_y - ct), 1.0)   # keep subtitles above ~1440 (app UI below)
        vw, vh = int(W * s) // 2 * 2, int((cb - ct) * s) // 2 * 2
        top_y = TOP
        cfg.setdefault("context_bottom", int(TOP + (sub_y - 65 - ct) * s - 20))
    header(cfg, h); context_box(cfg, c); end_card(cfg, e); background(b)
    if FY is not None:
        VPART = (f"split[s1][s2];[s2]crop={W}:{bh}:0:{bt},scale={vw}:{vh},crop={W}:{vh}:'{cfg.get('full_x','(in_w-out_w)/2')}':0[clip];"
                 f"[s1]crop={W}:{bh}:0:{bt},scale=-2:{H},crop={W}:{H},boxblur=40:3,eq=brightness=-0.15,format=rgba[bg];")
    else:
        VPART = (f"crop={W}:{cb - ct}:0:{ct},scale={vw}:{vh}" + (f",crop={W}:{H}:'{cfg.get('full_x','(in_w-out_w)/2')}':0" if FULL else "") + "[clip];"
                 f"[1:v]format=rgba[bg];")
    fc = (
        f"[0:v]trim=0:{cut},setpts=PTS-STARTPTS,scale={W}:{H},fps=30,"
        + VPART +
        f"[bg][clip]overlay=(W-w)/2:{top_y}[v0];"
        f"[2:v]format=rgba[hd];"
        f"[3:v]format=rgba,fade=t=in:st={c0}:d=0.35:alpha=1[cx];"
        f"[v0][hd]overlay=0:0[v1];[v1][cx]overlay=0:0[main];"
        f"[4:v]format=yuv420p,trim=0:{end_len},setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.25,setsar=1[endv];"
        f"[main]format=yuv420p,setsar=1[mainv];[mainv][endv]concat=n=2:v=1:a=0[v];"
        f"[0:a]atrim=0:{cut},asetpts=PTS-STARTPTS,afade=t=out:st={cut - 0.25}:d=0.25,aformat=sample_rates=44100:channel_layouts=stereo[a0];"
        f"[5:a]apad=whole_dur={end_len},atrim=0:{end_len},aformat=sample_rates=44100:channel_layouts=stereo[a1];"
        f"[a0][a1]concat=n=2:v=0:a=1[a]"
    )
    tmp = out + ".tmp.mp4"
    L = lambda p, t: ["-loop", "1", "-framerate", "30", "-t", str(t), "-i", p]
    cmd = (["ffmpeg", "-y", "-loglevel", "error", "-i", src] + L(b, cut) + L(h, cut) + L(c, cut) + L(e, end_len) +
           ["-i", STING, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(cut + end_len),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp])
    subprocess.run(cmd, check=True)
    os.replace(tmp, out)

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    build(cfg, sys.argv[2], sys.argv[3], sys.argv[4])
