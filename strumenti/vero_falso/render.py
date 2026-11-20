"""«Vero o falso?» di Mezzo Minuto: una frase del giorno verificata con i dati, solo testo e grafica (niente voce).

uso: python3 render.py config.json still T1 T2 ...     fotogrammi di prova in r/
     python3 render.py config.json vid I0 I1 out.mp4   fotogrammi I0..I1 a 30 fps
     python3 render.py config.json sfx out.wav         effetti sonori sui tempi delle scene
config.json: tag, citazione (parole *gialle* tra asterischi), chi, dove, fatti [ {titolo, testo} ],
             barre {titolo, voci [[etichetta, valore, nota]], unita}, verdetto, verdetto_colore, spiegazione, domanda, fonti.
"""
import json, math, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "fonts") + "/"
NAVY = (13, 18, 33); NAVY2 = (24, 32, 58); CREAM = (240, 236, 226); AMBER = (255, 196, 61); GREY = (165, 172, 195)
GREEN = (46, 190, 120); RED = (230, 72, 72)
BLK = "InterDisplay-Black.otf"; XB = "Inter-ExtraBold.otf"; BD = "Inter-Bold.otf"; SB = "Inter-SemiBold.otf"; MD = "Inter-Medium.otf"
cfg = json.load(open(sys.argv[1]))
# scene: (nome, inizio)
T = {"hook": 0.0, "conto": 3.2, "f0": 6.6, "f1": 10.6, "barre": 14.6, "verdetto": 19.4, "fine": 24.2}
DUR = 27.0
_fc = {}
def F(n, s):
    if (n, s) not in _fc: _fc[(n, s)] = ImageFont.truetype(FD + n, s)
    return _fc[(n, s)]
def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eb(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pr(t, t0, d): return cl((t - t0) / d)

# ---------- sfondo: blu notte con luce che si muove e grana ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(3); GRAIN = [rng.normal(0, 5, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]
def bg(t, accent=AMBER):
    cx = W * (0.5 + 0.28 * math.sin(t * 0.35)); cy = H * (0.32 + 0.1 * math.cos(t * 0.27))
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / H
    glow = np.exp(-d * 3.2)[..., None]
    base = np.array(NAVY, np.float32) * (1 - 0.5 * yy[..., None] / H * 0)
    col = base + glow * (np.array(NAVY2, np.float32) * 1.4 - base) + glow ** 3 * np.array(accent, np.float32) * 0.10
    g = GRAIN[int(t * 12) % 4]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    return Image.fromarray(np.clip(col + g, 0, 255).astype(np.uint8))

# ---------- testo ----------
def parse(s):
    out = []; hl = False
    for i, part in enumerate(s.split("*")):
        for w in part.split():
            out.append((w, i % 2 == 1))
    return out
def wrap(words, font, maxw, d):
    lines, cur = [], []
    for w in words:
        test = " ".join(x[0] for x in cur + [w])
        if cur and d.textlength(test, font=font) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    return lines
def rich(img, d, text, font, x, y, maxw, t0, t, lh=1.18, col=CREAM, stagger=0.045, center=False):
    """parole che salgono una alla volta; quelle tra *asterischi* su fondo giallo"""
    words = parse(text); lines = wrap(words, font, maxw, d)
    asc = font.getmetrics()[0]; L = int(font.size * lh); k = 0; sp = d.textlength(" ", font=font)
    for li, ln in enumerate(lines):
        lw = sum(d.textlength(w, font=font) for w, _ in ln) + sp * (len(ln) - 1)
        cx = x + (maxw - lw) / 2 if center else x
        for j, (w, hl) in enumerate(ln):
            ph = j > 0 and ln[j - 1][1]; nh = j + 1 < len(ln) and ln[j + 1][1]
            p = eo(pr(t, t0 + k * stagger, 0.35)); k += 1
            pad = 10
            if hl and not ph: cx += pad
            ww = d.textlength(w, font=font)
            if p > 0:
                dy = (1 - p) * 40; a = int(255 * p)
                if hl:
                    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                    hp = eo(pr(t, t0 + k * stagger + 0.15, 0.3))
                    x0 = cx - (sp if ph else pad); x1 = cx + ww + (sp if nh else pad)
                    od.rectangle([x0, y + li * L + dy - 6, x0 + (x1 - x0) * hp, y + li * L + dy + font.size * 1.08], fill=AMBER + (a,))
                    img.alpha_composite(ov)
                    d.text((cx, y + li * L + dy + asc), w, font=font, fill=NAVY + (a,), anchor="ls")
                else:
                    d.text((cx, y + li * L + dy + asc), w, font=font, fill=col + (a,), anchor="ls")
            cx += ww + sp
            if hl and not nh: cx += pad
    return y + len(lines) * L
def pill(d, x, y, text, font, fill, fg, pad=(26, 14), anchor="l"):
    tw = d.textlength(text, font=font); w = tw + 2 * pad[0]; h = font.size + 2 * pad[1]
    if anchor == "c": x = x - w / 2
    d.rounded_rectangle([x, y, x + w, y + h], h / 2, fill=fill)
    d.text((x + pad[0], y + pad[1] + font.size * 0.8), text, font=font, fill=fg, anchor="ls")
    return x + w

# ---------- header fisso: marchio + barra di avanzamento ----------
def header(img, d, t):
    pill(d, 70, 120, "VERO O FALSO?", F(BLK, 40), AMBER, NAVY)
    d.text((W - 70, 158), "MEZZO MINUTO", font=F(XB, 30), fill=GREY, anchor="rs")
    p = cl(t / (T["fine"]))
    d.rounded_rectangle([70, 222, W - 70, 230], 4, fill=(255, 255, 255, 40))
    d.rounded_rectangle([70, 222, 70 + (W - 140) * p, 230], 4, fill=AMBER)

def quote_block(img, d, t, t0, y=520, small=False):
    fs = 64 if not small else 46
    d.text((70, y - 10), "«", font=F(BLK, 200 if not small else 130), fill=AMBER + (int(255 * eo(pr(t, t0, 0.3))),), anchor="lt")
    yb = rich(img, d, cfg["citazione"], F(BLK, fs), 70, y + (170 if not small else 110), W - 140, t0 + 0.05, t, stagger=0.035 if not small else 0)
    a = int(255 * eo(pr(t, t0 + 0.6, 0.4)))
    d.text((70, yb + 40), cfg["chi"], font=F(XB, 42 if not small else 34), fill=CREAM + (a,), anchor="lt")
    d.text((70, yb + 100 if not small else yb + 86), cfg["dove"], font=F(MD, 34 if not small else 28), fill=GREY + (a,), anchor="lt")
    return yb

def scene(t):
    img = bg(t).convert("RGBA"); d = ImageDraw.Draw(img)
    if t < T["conto"]:
        quote_block(img, d, t, T["hook"])
    elif t < T["f0"]:
        # domanda con conto alla rovescia
        quote_block(img, d, t, -10, y=380, small=True)
        u = t - T["conto"]
        d.text((W / 2, 1180), "Secondo te?", font=F(BLK, 72), fill=CREAM + (int(255 * eo(u / 0.3)),), anchor="ms")
        for i, (lab, c) in enumerate([("VERO", GREEN), ("FALSO", RED)]):
            p = eb(pr(u, 0.15 + i * 0.1, 0.4)); cx = W / 2 + (i * 2 - 1) * 230
            bw, bh = 380 * p, 150 * p
            pulse = 1 + 0.03 * math.sin(u * 9 + i * 3)
            bw *= pulse; bh *= pulse
            if p > 0.02:
                d.rounded_rectangle([cx - bw / 2, 1260 - bh / 2 + 75, cx + bw / 2, 1260 + bh / 2 + 75], 32 * p, fill=c)
                d.text((cx, 1335 + 26 * p), lab, font=F(BLK, max(8, int(68 * p))), fill=(255, 255, 255), anchor="ms")
        n = 3 - int(u)
        if 1 <= n <= 3:
            fr = u - int(u); s = 1 + 0.6 * (1 - eo(fr / 0.25))
            d.text((W / 2, 1640), str(n), font=F(BLK, int(150 * s)), fill=AMBER + (int(255 * (1 - cl((fr - 0.7) / 0.3))),), anchor="ms")
    elif t < T["barre"]:
        k = 0 if t < T["f1"] else 1; t0 = T["f0"] if k == 0 else T["f1"]
        fa = cfg["fatti"][k]
        pill(d, 70, 500, f"I DATI · {k + 1}/3", F(XB, 32), (255, 255, 255, 30), AMBER)
        yb = rich(img, d, fa["titolo"], F(BLK, 84), 70, 600, W - 140, t0, t, stagger=0.05)
        rich(img, d, fa["testo"], F(SB, 52), 70, yb + 60, W - 140, t0 + 0.5, t, lh=1.32, stagger=0.025)
    elif t < T["verdetto"]:
        b = cfg["barre"]; t0 = T["barre"]
        pill(d, 70, 500, "I DATI · 3/3", F(XB, 32), (255, 255, 255, 30), AMBER)
        yb = rich(img, d, b["titolo"], F(BLK, 68), 70, 600, W - 140, t0, t, stagger=0.04)
        vmax = max(v[1] for v in b["voci"]); y = yb + 90
        for i, (lab, val, nota) in enumerate(b["voci"]):
            p = eo(pr(t, t0 + 0.6 + i * 0.5, 1.0)); a = int(255 * cl(pr(t, t0 + 0.5 + i * 0.5, 0.3)))
            d.text((70, y), lab, font=F(XB, 42), fill=CREAM + (a,), anchor="lt")
            bw = (W - 140) * val / vmax * p
            col = AMBER if i == 0 else (120, 170, 255)
            d.rounded_rectangle([70, y + 64, 70 + max(bw, 1), y + 64 + 96], 18, fill=col + (a,))
            num = f"{val * p:.1f}".replace(".", ",").replace(",0", "") + " " + b["unita"]
            tx = 70 + bw + 20; anc = "lm"
            if bw > 420: tx = 70 + bw - 24; anc = "rm"
            d.text((tx, y + 112), num, font=F(BLK, 50), fill=(NAVY if anc == "rm" else CREAM) + (a,), anchor=anc)
            d.text((70, y + 188), nota, font=F(MD, 32), fill=GREY + (a,), anchor="lt")
            y += 300
    elif t < T["fine"]:
        t0 = T["verdetto"]; u = t - t0
        d.text((W / 2, 600), "IL VERDETTO", font=F(XB, 40), fill=GREY + (int(255 * eo(u / 0.3)),), anchor="ms")
        # timbro
        p = eo(pr(u, 0.25, 0.22)); s = 1 + 1.4 * (1 - p)
        if p > 0:
            col = tuple(cfg.get("verdetto_colore", AMBER)); txt = cfg["verdetto"]
            f = F(BLK, 112); tw = d.textlength(txt, font=f) + 90; th = 200
            st = Image.new("RGBA", (int(tw) + 40, th + 40), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle([20, 20, 20 + tw, 20 + th], 28, outline=col, width=14)
            sd.text((20 + tw / 2, 20 + th / 2 + 40), txt, font=f, fill=col, anchor="ms")
            st = st.rotate(-6, expand=True, resample=Image.BICUBIC)
            st = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.LANCZOS)
            st.putalpha(st.getchannel("A").point(lambda v: int(v * p)))
            img.alpha_composite(st, (int(W / 2 - st.width / 2), int(850 - st.height / 2)))
        rich(img, d, cfg["spiegazione"], F(SB, 52), 70, 1100, W - 140, t0 + 0.9, t, lh=1.3, stagger=0.03, center=True)
    else:
        t0 = T["fine"]
        rich(img, d, cfg["domanda"], F(BLK, 80), 70, 640, W - 140, t0, t, stagger=0.05, center=True)
        a = int(255 * eo(pr(t, t0 + 0.8, 0.4)))
        pill(d, W / 2, 1080, "Scrivilo nei commenti 👇".replace(" 👇", ""), F(XB, 44), AMBER + (a,), NAVY + (a,), anchor="c")
        d.text((W / 2, 1300), "Segui Mezzo Minuto", font=F(XB, 46), fill=CREAM + (a,), anchor="ms")
        d.text((W / 2, 1360), "il contesto verificato delle notizie", font=F(MD, 36), fill=GREY + (a,), anchor="ms")
    header(img, d, t)
    # fonti sempre in basso
    d.text((70, H - 230), "Fonti: " + cfg["fonti"], font=F(MD, 26), fill=GREY + (150,), anchor="lt")
    im = img.convert("RGB")
    # flash leggero sui cambi scena
    for k in ["conto", "f0", "f1", "barre", "verdetto", "fine"]:
        q = t - T[k]
        if 0 <= q < 0.12:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.18 * (1 - q / 0.12))
    if 0 <= t - T["verdetto"] - 0.47 < 0.2:   # scossa sul timbro
        q = (t - T["verdetto"] - 0.47) / 0.2; dx = int(14 * (1 - q) * math.sin(q * 40))
        im = im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, int(dx * 0.6)))
    return im

def sfx(out):
    sr = 48000; n = int(DUR * sr); a = np.zeros(n, np.float32); r = np.random.default_rng(1)
    def add(t, s):
        i = int(t * sr); a[i:i + len(s)] += s[:max(0, n - i)]
    def whoosh(d=0.45, g=0.5):
        m = int(d * sr); w = r.normal(0, 1, m).astype(np.float32); env = np.sin(np.linspace(0, np.pi, m)) ** 2
        k = np.exp(-np.linspace(0, 6, 64)); w = np.convolve(w, k / k.sum(), "same"); return w * env * g
    def tick(f=1800, d=0.06, g=0.5):
        m = int(d * sr); tt = np.arange(m) / sr; return (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 70) * g).astype(np.float32)
    def thud(g=0.9):
        m = int(0.6 * sr); tt = np.arange(m) / sr; f = 110 * np.exp(-tt * 6) + 45
        s = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 7); s += r.normal(0, 1, m) * np.exp(-tt * 40) * 0.5; return (s * g).astype(np.float32)
    def pop(g=0.35):
        m = int(0.12 * sr); tt = np.arange(m) / sr; f = 500 + 900 * tt / 0.12; return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 30) * g).astype(np.float32)
    for k in ["conto", "f0", "f1", "barre", "verdetto", "fine"]: add(T[k] - 0.2, whoosh())
    add(0.05, thud(0.5))
    for i in range(3): add(T["conto"] + i + 0.02, tick(1500 + 300 * i))
    add(T["conto"] + 0.15, pop()); add(T["conto"] + 0.25, pop())
    add(T["barre"] + 0.6, pop(0.25)); add(T["barre"] + 1.1, pop(0.25))
    add(T["verdetto"] + 0.45, thud(1.0))
    a = a / max(1e-6, np.abs(a).max()) * 0.8
    import soundfile as sf; sf.write(out, a, sr)

if __name__ == "__main__":
    mode = sys.argv[2]
    if mode == "still":
        os.makedirs("r", exist_ok=True)
        for x in sys.argv[3:]: scene(float(x)).save(f"r/f_{float(x):05.2f}.jpg", quality=88)
    elif mode == "sfx":
        sfx(sys.argv[3])
    else:
        i0, i1, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(scene(i / FPS).tobytes())
        p.stdin.close(); p.wait()
