"""Notiziario Mezzo Minuto, nuova grafica (bozza): clip e foto a tutto schermo, titoli animati, stacchi sulla musica.

uso: python3 notiziario_v2.py config.json still T1 T2 ...   (fotogrammi di prova in r/)
     python3 notiziario_v2.py config.json vid I0 I1 out.mp4  (fotogrammi I0..I1 a 30 fps)
config.json: date_label, news (come il kit: [CATEGORIA, TITOLO, TESTO, FONTE]), evidenza (parola/e gialle per titolo),
             cuts (inizio di ogni notizia e dell'uscita, in secondi), shots (per notizia: lista di [file, inizio, fx, fy]),
             clip_dir, sondaggio (opzionale, indice notizia e barre), durata.
"""
import json, math, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # cartella strumenti/
FD = os.path.join(ROOT, "fonts") + "/"
NAVY = (13, 18, 33); CREAM = (240, 236, 226); AMBER = (255, 196, 61); GOLD = (208, 192, 150); GREY = (165, 172, 195)
CAT = {"MONDO": (70, 130, 220), "ECONOMIA": (40, 170, 120), "USA": (210, 70, 80), "ITALIA": (60, 150, 90), "SONDAGGI": (150, 100, 210)}
BLK = "InterDisplay-Black.otf"; XB = "Inter-ExtraBold.otf"; BD = "Inter-Bold.otf"; SB = "Inter-SemiBold.otf"; MD = "Inter-Medium.otf"
cfg = json.load(open(sys.argv[1]))
# tempi fissi della musica del notiziario (136 BPM, accenti ogni battuta): 3 battute per notizia
cfg.setdefault("cuts", [0, 6.41, 11.75, 17.07, 22.41, 27.75]); cfg.setdefault("durata", 31.5)
CUTS = cfg["cuts"]; DUR = cfg["durata"]
CLIP = cfg.get("clip_dir") or os.path.dirname(os.path.abspath(sys.argv[1]))
_fc = {}
def F(n, s):
    if (n, s) not in _fc: _fc[(n, s)] = ImageFont.truetype(FD + n, s)
    return _fc[(n, s)]
def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eb(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def prog(t, t0, d): return cl((t - t0) / d)

# ---------- immagini ----------
def grade(a, k=0.8):
    g = a.mean(axis=2, keepdims=True); a = a * 0.8 + g * 0.2
    return np.clip(a * k + np.array(NAVY, np.float32) * 0.12, 0, 255).astype(np.uint8)
sh = np.zeros((H, W, 1), np.float32)
for i, yv in enumerate(np.linspace(0, 1, H)):
    sh[i] = 0.10 + 0.6 * max(0, 1 - yv / 0.16) ** 1.6 + 0.93 * max(0, (yv - 0.45) / 0.55) ** 1.25
shadeL = Image.fromarray(np.dstack([np.broadcast_to(np.array(NAVY, np.uint8), (H, W, 3)), (np.clip(sh, 0, 0.96) * 255).astype(np.uint8)]), "RGBA")
GZ = 1.12
_ph = {}
def photo(fn):
    if fn not in _ph:
        im = Image.open(fn).convert("RGB"); s = max(W * GZ * 1.12 / im.width, H * GZ * 1.12 / im.height)
        im = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
        _ph[fn] = Image.fromarray(grade(np.asarray(im).astype(np.float32), 0.85))
    return _ph[fn]
class Reader:
    def __init__(s): s.key = None; s.p = None; s.next = None; s.last = None
    def get(s, fn, start, fx, i):
        if s.key != (fn, start) or s.next != i:
            if s.p: s.p.kill()
            ow, oh = int(W * GZ) // 2 * 2, int(H * GZ) // 2 * 2
            vf = f"fps={FPS},scale={ow}:{oh}:force_original_aspect_ratio=increase,crop={ow}:{oh}:(iw-{ow})*{fx}:(ih-{oh})/2"
            s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start + i / FPS:.3f}", "-i", fn, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            s.key = (fn, start); s.dim = (ow, oh)
        ow, oh = s.dim; b = s.p.stdout.read(ow * oh * 3); s.next = i + 1
        if len(b) == ow * oh * 3: s.last = np.frombuffer(b, np.uint8).reshape(oh, ow, 3)
        return s.last
RD = Reader()
def shots_flat():
    out = []
    for k, lst in enumerate(cfg["shots"]):
        t0, t1 = CUTS[k], CUTS[k + 1]
        for j, s in enumerate(lst):
            a = (s[4] if len(s) > 4 else {}).get("da", t0 + (t1 - t0) * j / len(lst))
            out.append((a, s))
    res = []
    for i, (a, s) in enumerate(out):
        b = out[i + 1][0] if i + 1 < len(out) else CUTS[len(cfg["shots"])]
        res.append((a, b, s))
    return res
SHOTS = shots_flat()
def broll(t):
    for a, b, s in SHOTS:
        if a - 1e-3 <= t < b:
            fn, start, fx, fy = s[:4]; u = cl((t - a) / max(0.1, b - a)); path = fn if fn.startswith("/") else (os.path.join(ROOT, fn[5:]) if fn.startswith("repo:") else os.path.join(CLIP, fn))
            if fn.endswith(".mp4"):
                arr = RD.get(path, start, fx, int(round((t - a) * FPS)))
                im = Image.fromarray(grade(arr.astype(np.float32), 0.8 * (s[4] if len(s) > 4 else {}).get("luce", 1.0))); z = 1 + 0.06 * u; cw = im.width / z
                cx, cy = (im.width - cw) / 2, (im.height - cw * H / W) / 2
            else:
                im = photo(path); z = 1 + 0.12 * u; cw = W * GZ / z
                cx, cy = (im.width - cw) * fx, (im.height - cw * H / W) * fy
            ch = cw * H / W
            o = im.crop((int(cx), int(cy), int(cx + cw), int(cy + ch))).resize((W, H), Image.BILINEAR).convert("RGBA")
            o.alpha_composite(shadeL); return o, a
    return None, 0

# ---------- testo ----------
_tc = {}
def tl(s, font, size, color, sh=False):
    k = (s, font, size, color, sh)
    if k not in _tc:
        f = F(font, size); b = f.getbbox(s); im = Image.new("RGBA", (b[2] - b[0] + 30, b[3] - b[1] + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if sh: d.text((15 - b[0] + 3, 15 - b[1] + 5), s, font=f, fill=(0, 0, 0, 150))
        d.text((15 - b[0], 15 - b[1]), s, font=f, fill=color); _tc[k] = im
    return _tc[k]
_wc = {}
def word(s, size, color, sh):
    k = (s, size, color, sh)
    if k not in _wc:
        f = F(BLK, size); w = int(f.getlength(s)) + 20; im = Image.new("RGBA", (w, int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if sh: d.text((3, int(size * 1.0) + 5), s, font=f, fill=(0, 0, 0, 150), anchor="ls")
        d.text((0, int(size * 1.0)), s, font=f, fill=color, anchor="ls"); _wc[k] = im
    return _wc[k]
def put(c, L, x, y, sc=1.0, a=1.0, anchor="lm"):
    if a <= 0.01 or sc <= 0.01: return
    if abs(sc - 1) > 0.01: L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
    if a < 0.99: L = L.copy(); L.putalpha(L.split()[3].point(lambda v: int(v * a)))
    px = int(x) if anchor[0] == "l" else int(x - L.width / 2) if anchor[0] == "m" else int(x - L.width)
    c.alpha_composite(L, (max(0, px), max(0, int(y - L.height / 2))))
def wrap(words, font, size, maxw):
    f = F(font, size); lines = [[]]; sp = f.getlength(" ")
    for w in words:
        cur = lines[-1]; wd = sum(f.getlength(x) for x in cur) + sp * len(cur) + f.getlength(w)
        if cur and wd > maxw: lines.append([w])
        else: cur.append(w)
    return lines
def headline(c, title, hl, t, t0, y0, out):
    words = title.split(); size = 88
    while True:
        lines = wrap(words, BLK, size, W - 140)
        if len(lines) <= 3: break
        size -= 6
    f = F(BLK, size); sp = f.getlength(" "); lh = int(size * 1.12); hlw = set(x.lower().strip(",.") for x in hl.split()); pad = 14
    idx = 0
    for li, line in enumerate(lines):
        x = 70
        for w in line:
            gl = w.lower().strip(",.:’'") in hlw or w.lower() in hlw
            if gl: x += pad
            p = prog(t, t0 + idx * 0.07, 0.22)
            if p > 0:
                a = eo(p) * (1 - prog(t, out, 0.15)); dy = (1 - eo(p)) * 40
                top = y0 + li * lh + dy
                if gl:
                    tw = f.getlength(w); R = Image.new("RGBA", (int(tw) + 28, int(size * 1.22)), (0, 0, 0, 0))
                    ImageDraw.Draw(R).rounded_rectangle([0, 0, int(tw) + 27, int(size * 1.2)], 12, fill=AMBER + (int(235 * a),))
                    c.alpha_composite(R, (int(x - 14), int(top + size * 0.04)))
                Wd = word(w, size, NAVY if gl else CREAM, not gl)
                if a < 0.99: Wd = Wd.copy(); Wd.putalpha(Wd.split()[3].point(lambda v: int(v * a)))
                c.alpha_composite(Wd, (int(x), int(top)))
            x += f.getlength(w) + sp + (pad if gl else 0); idx += 1
    return y0 + len(lines) * lh + 20
def body(c, s, t, t0, y0, out):
    lines = wrap(s.split(), SB, 44, W - 140); a = eo(prog(t, t0, 0.35)) * (1 - prog(t, out, 0.15)); dy = (1 - eo(prog(t, t0, 0.35))) * 30
    for i, ln in enumerate(lines): put(c, tl(" ".join(ln), SB, 44, CREAM, True), 55, y0 + i * 56 + dy, 1, a)
    return y0 + len(lines) * 56
def chip(c, s, col, x, y, a):
    f = F(BLK, 34); tw = f.getlength(s); L = Image.new("RGBA", (int(tw) + 44, 62), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, int(tw) + 43, 61], 31, fill=col + (int(255 * a),)); d.text((22, 31), s, font=f, fill=(255, 255, 255, int(255 * a)), anchor="lm")
    c.alpha_composite(L, (int(x), int(y - 31))); return x + tw + 56

logo = Image.open(os.path.join(ROOT, "logo_mark.png")).convert("RGBA"); logo = logo.resize((int(logo.width * 58 / logo.height), 58))
def header(c, t, k):
    c.alpha_composite(logo, (60, 110))
    put(c, tl("MEZZO MINUTO", BLK, 34, GOLD), 120, 140)
    put(c, tl(cfg["date_label"].upper(), BD, 24, GREY), W - 60, 140, anchor="rm")
    d = ImageDraw.Draw(c); n = len(cfg["news"]); gw = (W - 120 - 12 * (n - 1)) / n
    for i in range(n):
        x0 = 60 + i * (gw + 12); d.rounded_rectangle([x0, 70, x0 + gw, 78], 4, fill=(255, 255, 255, 55))
        if i < k or (i == k and t >= CUTS[i]):
            fr = 1 if i < k else cl((t - CUTS[i]) / (CUTS[i + 1] - CUTS[i]))
            d.rounded_rectangle([x0, 70, x0 + gw * fr, 78], 4, fill=AMBER)

def poll(c, t, t0, out, bars, y=575, step=118):
    mx = max(b[1] for b in bars); pa = eo(prog(t, t0, 0.3)) * (1 - prog(t, out, .15))
    P = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(P).rounded_rectangle([40, y - 90, W - 40, y + len(bars) * step + 5], 28, fill=NAVY + (int(205 * pa),)); c.alpha_composite(P)
    put(c, tl(cfg["sondaggio"]["titolo"], BD, 30, GREY), 70, y - 50, 1, eo(prog(t, t0, 0.3)) * (1 - prog(t, out, .15)))
    for i, (lab, v) in enumerate(bars):
        tt = t0 + 0.25 + i * 0.32; p = eo(prog(t, tt, 0.55)); a = eo(prog(t, tt, 0.2)) * (1 - prog(t, out, .15))
        if a <= 0: continue
        yy = y + i * step; L = Image.new("RGBA", (W, 100), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
        dd.text((70, 22), lab, font=F(BD, 36), fill=CREAM + (int(255 * a),), anchor="lm")
        bw = (W - 330) * v / mx * p
        col = AMBER if i < 2 else (120, 135, 175)
        dd.rounded_rectangle([70, 48, 70 + max(8, bw), 86], 10, fill=col + (int(235 * a),))
        val = f"{v * p:.1f}%".replace(".", ",")
        dd.text((70 + max(8, bw) + 18, 67), val, font=F(BLK, 40), fill=CREAM + (int(255 * a),), anchor="lm")
        c.alpha_composite(L, (0, yy))

def frame(t):
    k = sum(1 for x in CUTS[1:] if x <= t); n = len(cfg["news"])
    br, sa = broll(t) if k < n else (None, 0)
    if br is None:
        y = np.linspace(0, 1, H)[:, None, None]
        base = (np.array((24, 36, 62), np.float32) * (1 - y) + np.array(NAVY, np.float32) * y)
        c = Image.fromarray(np.broadcast_to(base, (H, W, 3)).astype(np.uint8)).convert("RGBA")
    else:
        c = br
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if k < n:
        cat, title, text, src = cfg["news"][k]; t0 = CUTS[k]; out = CUTS[k + 1] - 0.12
        a = eo(prog(t, t0, 0.25)) * (1 - prog(t, out, 0.15))
        # numero grande e categoria
        put(L, tl(f"{k + 1:02d}", BLK, 150, AMBER + (230,)), 62, 330 + (1 - eo(prog(t, t0, .3))) * 60, 1, a)
        chip(L, cat, CAT.get(cat, (90, 90, 120)), 70, 450, a)
        if cfg.get("sondaggio") and cfg["sondaggio"]["notizia"] == k:
            poll(L, t, t0 + 0.3, out, cfg["sondaggio"]["barre"])
        yb = headline(L, title, cfg["evidenza"][k], t, t0 + 0.15, 1215 if (cfg.get("sondaggio") and cfg["sondaggio"]["notizia"] == k) else 1170, out)
        yb = body(L, text, t, t0 + 1.0, yb + 40, out)
        put(L, tl(src, MD, 28, GREY), 58, yb + 30, 1, eo(prog(t, t0 + 1.4, .3)) * (1 - prog(t, out, .15)))
    else:
        t0 = CUTS[n]; p = eo(prog(t, t0, 0.4))
        put(L, logo.resize((int(logo.width * 3), 174)), W / 2, 700, 0.8 + 0.2 * eb(prog(t, t0, .5)), p, "mm")
        put(L, tl("Questo era", SB, 50, GREY), W / 2, 860, 1, eo(prog(t, t0 + .2, .3)), "mm")
        put(L, tl("MEZZO MINUTO", BLK, 110, CREAM), W / 2, 960, 1, eo(prog(t, t0 + .35, .3)), "mm")
        q = prog(t, t0 + .7, .3)
        if q > 0:
            f = F(BLK, 46); s = "SEGUI PER LE NOTIZIE DI DOMANI"; tw = f.getlength(s)
            R = Image.new("RGBA", (int(tw) + 80, 96), (0, 0, 0, 0)); ImageDraw.Draw(R).rounded_rectangle([0, 0, int(tw) + 79, 95], 48, fill=AMBER)
            ImageDraw.Draw(R).text((40, 48), s, font=f, fill=NAVY, anchor="lm"); put(L, R, W / 2, 1120, 0.6 + 0.4 * eb(q), eo(q), "mm")
    # colpo sullo stacco: zoom e lampo
    b = max([0] + [x for x in CUTS if x <= t]); dt = t - b
    if 0 < b and dt < 0.25:
        z = 1 + 0.08 * (1 - eo(dt / 0.25)); nw, nh = int(W * z), int(H * z)
        L = L.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    c.alpha_composite(L)
    header(c, t, min(k, n))
    if b > 0 and dt < 0.08: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(110 * (1 - dt / 0.08)))))
    if t > DUR - 0.5: c = Image.blend(c, Image.new("RGBA", (W, H), NAVY + (255,)), cl((t - (DUR - 0.5)) / 0.5))
    return c.convert("RGB")

# ---------- slide del carosello (4:5) ----------
SH2 = 1350
sh2 = np.zeros((SH2, W, 1), np.float32)
for i, yv in enumerate(np.linspace(0, 1, SH2)):
    sh2[i] = 0.12 + 0.6 * max(0, 1 - yv / 0.2) ** 1.6 + 0.95 * max(0, (yv - 0.38) / 0.62) ** 1.15
shade2 = Image.fromarray(np.dstack([np.broadcast_to(np.array(NAVY, np.uint8), (SH2, W, 3)), (np.clip(sh2, 0, 0.96) * 255).astype(np.uint8)]), "RGBA")
def slide_bg(k):
    s = cfg["shots"][k][0]; fn = s[0]
    path = fn if fn.startswith("/") else (os.path.join(ROOT, fn[5:]) if fn.startswith("repo:") else os.path.join(CLIP, fn))
    if fn.endswith(".mp4"):
        tmp = "/tmp/_slide_frame.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s[1] + 1.0), "-i", path, "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGB"); fx, fy = s[2], 0.5
    else:
        im = Image.open(path).convert("RGB"); fx, fy = s[2], s[3]
    sc = max(W / im.width, SH2 / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x = int((im.width - W) * fx); y = int((im.height - SH2) * fy)
    a = grade(np.asarray(im.crop((x, y, x + W, y + SH2))).astype(np.float32), 0.85 * ((s[4] if len(s) > 4 else {}).get("luce", 1.0)))
    o = Image.fromarray(a).convert("RGBA"); o.alpha_composite(shade2); return o
def slide(k, out):
    global H
    cat, title, text, src = cfg["news"][k]; n = len(cfg["news"]); T = 99.0
    c = slide_bg(k); d = ImageDraw.Draw(c)
    c.alpha_composite(logo, (60, 60)); put(c, tl("MEZZO MINUTO", BLK, 34, GOLD), 120, 90)
    put(c, tl(cfg["date_label"].upper(), BD, 24, GREY), W - 60, 90, anchor="rm")
    for i in range(n):
        x0 = W - 60 - (n - i) * 34 + 10; d.ellipse([x0, 130, x0 + 16, 146], fill=AMBER if i == k else (255, 255, 255, 90))
    put(c, tl(f"{k + 1:02d}", BLK, 150, AMBER), 62, 240, 1, 1)
    chip(c, cat, CAT.get(cat, (90, 90, 120)), 70, 360, 1)
    if cfg.get("sondaggio") and cfg["sondaggio"]["notizia"] == k:
        yb = headline(c, title, cfg["evidenza"][k], T, 0, 430, 1e9)
        poll(c, T, 0, 1e9, cfg["sondaggio"]["barre"], y=yb + 120, step=100)
        put(c, tl(src, MD, 28, GREY), 58, SH2 - 50, 1, 1)
    else:
        yb = headline(c, title, cfg["evidenza"][k], T, 0, 800, 1e9)
        yb = body(c, text, T, 0, yb + 30, 1e9)
        put(c, tl(src, MD, 28, GREY), 58, min(SH2 - 45, yb + 30), 1, 1)
    c.convert("RGB").save(out, quality=92)

if __name__ == "__main__":
    if sys.argv[2] == "slide":
        for k in range(len(cfg["news"])): slide(k, os.path.join(sys.argv[3], f"slide_{k + 2:02d}.jpg"))
    elif sys.argv[2] == "still":
        os.makedirs("r", exist_ok=True)
        for ts in sys.argv[3:]: frame(float(ts)).save(f"r/n_{ts}.png")
    else:
        i0, i1, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); assert p.wait() == 0; os.rename(out + ".tmp.mp4", out)
