"""«Vero o falso?» con clip e voce: la frase detta (clip con sottotitoli), fermo immagine, voce con i dati, verdetto.

uso: python3 render_clip.py CONFIG.json still T1 T2 ...      fotogrammi di prova in CARTELLA/r/
     python3 render_clip.py CONFIG.json vid I0 I1 OUT.mp4    fotogrammi I0..I1
     python3 render_clip.py CONFIG.json sfx OUT.wav
CONFIG (percorsi relativi alla sua cartella): sorgente, clip_fine (s), voce_t0 (s nel video), voce_taglio (s tagliati
all'inizio della voce già accelerata), durata, citazione (*parola* evidenziata), chi, fonti, frasi [[inizio, fine, testo]]
(tempi della voce accelerata), scene [{tipo, da, ...}], verdetto, verdetto_colore, domanda.
"""
import json, math, sys, os, subprocess, re, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(os.path.dirname(HERE), "fonts") + "/"
NAVY = (13, 18, 33); CREAM = (240, 236, 226); AMBER = (255, 196, 61); GREY = (175, 182, 205)
GREEN = (46, 190, 120); RED = (232, 64, 64)
BLK = "InterDisplay-Black.otf"; XB = "Inter-ExtraBold.otf"; SB = "Inter-SemiBold.otf"; MD = "Inter-Medium.otf"
CP = sys.argv[1]; DIR = os.path.dirname(os.path.abspath(CP)); C = json.load(open(CP))
A = C["clip_fine"]; V0 = C["voce_t0"]; CUT = C["voce_taglio"]; D = C["durata"]
_fc = {}
def F(n, s):
    if (n, s) not in _fc: _fc[(n, s)] = ImageFont.truetype(FD + n, s)
    return _fc[(n, s)]
def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eb(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def vt(t): return t - V0 + CUT          # tempo nella voce accelerata
def tv(v): return v - CUT + V0          # da tempo voce a tempo video

class Src:
    def __init__(s, p): s.cap = cv2.VideoCapture(p); s.i = -1; s.f = None; s.n = int(s.cap.get(7))
    def get(s, k):
        k = max(0, min(k, s.n - 1))
        if k < s.i or k > s.i + 60: s.cap.set(1, k); s.i = k - 1
        while s.i < k:
            ok, f = s.cap.read()
            if not ok: break
            s.f = f; s.i += 1
        return s.f
SRC = Src(os.path.join(DIR, C["sorgente"]))

def bg_blur(t):
    f = SRC.get(int(t * FPS))
    small = cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 6)
    big = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    big = big * 0.38 + np.array(NAVY[::-1], np.float32) * 0.35
    return Image.fromarray(cv2.cvtColor(np.clip(big, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))

def parse(s):
    out = []
    for i, part in enumerate(s.split("*")):
        for w in part.split(): out.append((w, i % 2 == 1))
    return out
def rich(img, d, text, font, x, y, maxw, t0, t, lh=1.18, col=CREAM, stagger=0.04, center=False, hlcol=AMBER):
    words = parse(text); lines, cur = [], []
    for w in words:
        if cur and d.textlength(" ".join(x[0] for x in cur + [w]), font=font) + 40 > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    asc = font.getmetrics()[0]; L = int(font.size * lh); k = 0; sp = d.textlength(" ", font=font); pad = 10
    for li, ln in enumerate(lines):
        lw = sum(d.textlength(w, font=font) for w, _ in ln) + sp * (len(ln) - 1)
        cx = x + (maxw - lw) / 2 if center else x
        for j, (w, hl) in enumerate(ln):
            ph = j > 0 and ln[j - 1][1]; nh = j + 1 < len(ln) and ln[j + 1][1]
            p = eo((t - t0 - k * stagger) / 0.35); k += 1
            if hl and not ph: cx += pad
            ww = d.textlength(w, font=font)
            if p > 0:
                dy = (1 - p) * 36; a = int(255 * p); yy = y + li * L + dy
                if hl:
                    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                    x0 = cx - (sp if ph else pad); x1 = cx + ww + (sp if nh else pad)
                    hp = eo((t - t0 - k * stagger - 0.12) / 0.3)
                    od.rectangle([x0, yy - 6, x0 + (x1 - x0) * hp, yy + font.size * 1.08], fill=hlcol + (a,))
                    img.alpha_composite(ov)
                    d.text((cx, yy + asc), w, font=font, fill=NAVY + (a,), anchor="ls")
                else:
                    d.text((cx, yy + asc), w, font=font, fill=col + (a,), anchor="ls")
            cx += ww + sp
            if hl and not nh: cx += pad
    return y + len(lines) * L
def pill(d, x, y, text, font, fill, fg, pad=(26, 14), center=False):
    tw = d.textlength(text, font=font); w = tw + 2 * pad[0]; h = font.size + 2 * pad[1]
    if center: x -= w / 2
    d.rounded_rectangle([x, y, x + w, y + h], h / 2, fill=fill)
    d.text((x + pad[0], y + pad[1] + font.size * 0.8), text, font=font, fill=fg, anchor="ls")

def header(d, t):
    pill(d, 60, 110, "VERO O FALSO?", F(BLK, 38), AMBER, NAVY)
    d.text((W - 60, 146), "MEZZO MINUTO", font=F(XB, 30), fill=CREAM, anchor="rs")
    p = cl(t / D); d.rounded_rectangle([60, 206, W - 60, 213], 3, fill=(255, 255, 255, 50))
    d.rounded_rectangle([60, 206, 60 + (W - 120) * p, 213], 3, fill=AMBER)

def captions(img, d, t):
    v = vt(t)
    for a, b, txt in C["frasi"]:
        if a - 0.05 <= v < b + 0.25:
            words = txt.split(); n = len(words)
            # gruppi da max 5 parole, tempi in proporzione alle lettere
            groups, cur = [], []
            for w in words:
                cur.append(w)
                if len(cur) >= 5 or w[-1] in ",.:?": groups.append(cur); cur = []
            if cur: groups.append(cur)
            tot = sum(len("".join(g)) for g in groups); acc = a
            for g in groups:
                dur = (b - a) * len("".join(g)) / tot
                if acc <= v < acc + dur or (g is groups[-1] and v >= acc):
                    s = " ".join(g); f = F(XB, 54)
                    tw = d.textlength(s, font=f)
                    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                    od.rounded_rectangle([W / 2 - tw / 2 - 26, 1560, W / 2 + tw / 2 + 26, 1650], 18, fill=(0, 0, 0, 170))
                    img.alpha_composite(ov)
                    d.text((W / 2, 1622), s, font=f, fill=CREAM, anchor="ms")
                    return
                acc += dur
            return

def scene(t):
    if t < A:   # la clip originale, con i suoi sottotitoli
        f = SRC.get(int(t * FPS))
        img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA"); d = ImageDraw.Draw(img)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, 0, W, 300], fill=(10, 14, 26, 150)); img.alpha_composite(ov)
        header(d, t)
        a = int(255 * eo(t / 0.4))
        d.text((60, 268), C["chi"], font=F(XB, 36), fill=CREAM + (a,), anchor="ls")
        return img.convert("RGB")
    img = bg_blur(t).convert("RGBA"); d = ImageDraw.Draw(img)
    v = vt(t); S = C["scene"]
    cur = [s for s in S if v >= s["da"]]; sc = cur[-1] if cur else S[0]
    v0 = sc["da"]
    if sc["tipo"] == "domanda_iniziale":
        u = t - A
        rich(img, d, "«" + C["citazione"] + "»", F(BLK, 70), 60, 420, W - 120, A, t, stagger=0.03)
        d.text((60, 790), C["chi"], font=F(SB, 38), fill=GREY, anchor="ls")
        for i, (lab, c) in enumerate([("VERO", GREEN), ("FALSO", RED)]):
            p = eb((t - A - 0.25 - i * 0.12) / 0.4); cx = W / 2 + (i * 2 - 1) * 230
            if p > 0.02:
                pu = 1 + 0.03 * math.sin(t * 9 + i * 3); bw, bh = 380 * p * pu, 150 * p * pu
                d.rounded_rectangle([cx - bw / 2, 1100 - bh / 2, cx + bw / 2, 1100 + bh / 2], 32 * p, fill=c)
                d.text((cx, 1100 + 24 * p), lab, font=F(BLK, max(8, int(68 * p))), fill=(255, 255, 255), anchor="ms")
    elif sc["tipo"] == "barre":
        d.text((60, 400), sc["titolo"], font=F(BLK, 58), fill=CREAM, anchor="ls")
        d.text((60, 452), sc["sotto"], font=F(MD, 32), fill=GREY, anchor="ls")
        base = 1080; scale = 900; n = len(sc["voci"]); bw = 230; gap = (W - 120 - n * bw) / (n - 1)
        d.line([60, base, W - 60, base], fill=(255, 255, 255, 120), width=4)
        for i, (lab, val, at, hl) in enumerate(sc["voci"]):
            p = eo((v - at) / 0.7)
            if p <= 0: continue
            x0 = 60 + i * (bw + gap); h = max(10, val * scale) * p
            col = AMBER if hl and v >= at else (120, 170, 255)
            d.rounded_rectangle([x0, base - h, x0 + bw, base], 16, fill=col)
            num = ("+" if val > 0 else "") + f"{val * p:.1f}".replace(".", ",") + "%"
            d.text((x0 + bw / 2, base - h - 26), num, font=F(BLK, 64), fill=CREAM, anchor="ms")
            d.text((x0 + bw / 2, base + 64), lab, font=F(XB, 36), fill=CREAM, anchor="ms")
        if sc.get("timbro") and v >= sc["timbro"][0]:
            p = eo((v - sc["timbro"][0]) / 0.25)
            txt = sc["timbro"][1]; f = F(BLK, 56); tw = d.textlength(txt, font=f)
            y = 1290; d.rounded_rectangle([W / 2 - tw / 2 - 34, y, W / 2 + tw / 2 + 34, y + 100], 22, fill=AMBER + (int(255 * p),))
            d.text((W / 2, y + 70), txt, font=f, fill=NAVY + (int(255 * p),), anchor="ms")
    elif sc["tipo"] == "ragione":
        p0 = eo((v - v0) / 0.4)
        d.text((60, 430), sc["titolo"], font=F(BLK, 66), fill=GREEN + (int(255 * p0),), anchor="ls")
        for i, (num, lab, at) in enumerate(sc["voci"]):
            p = eo((v - at) / 0.45)
            if p <= 0: continue
            y = 540 + i * 360 + (1 - p) * 40; a = int(255 * p)
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([60, y, W - 60, y + 300], 28, fill=(255, 255, 255, int(28 * p)))
            od.rectangle([60, y, 72, y + 300], fill=GREEN + (a,)); img.alpha_composite(ov)
            d.text((110, y + 170), num, font=F(BLK, 150), fill=AMBER + (a,), anchor="ls")
            d.text((112, y + 240), lab, font=F(SB, 40), fill=CREAM + (a,), anchor="ls")
    elif sc["tipo"] == "verdetto":
        d.text((W / 2, 520), "IL VERDETTO", font=F(XB, 44), fill=GREY, anchor="ms")
        at = sc["timbro"]
        p = eo((v - at) / 0.2); s = 1 + 1.4 * (1 - p)
        if p > 0:
            col = tuple(C.get("verdetto_colore", RED)); txt = C["verdetto"]; f = F(BLK, 150)
            tw = d.textlength(txt, font=f) + 110; th = 240
            st = Image.new("RGBA", (int(tw) + 40, th + 40), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle([20, 20, 20 + tw, 20 + th], 30, outline=col, width=16)
            sd.text((20 + tw / 2, 20 + th / 2 + 54), txt, font=f, fill=col, anchor="ms")
            st = st.rotate(-7, expand=True, resample=Image.BICUBIC)
            st = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.LANCZOS)
            st.putalpha(st.getchannel("A").point(lambda q: int(q * p)))
            img.alpha_composite(st, (int(W / 2 - st.width / 2), int(780 - st.height / 2)))
        rich(img, d, sc["testo"], F(SB, 54), 60, 1040, W - 120, tv(sc["testo_da"]), t, lh=1.28, stagger=0.03, center=True)
    elif sc["tipo"] == "fine":
        rich(img, d, C["domanda"], F(BLK, 76), 60, 560, W - 120, tv(v0), t, stagger=0.04, center=True)
        a = int(255 * eo((v - v0 - 0.8) / 0.4))
        pill(d, W / 2, 1000, "Scrivilo nei commenti", F(XB, 44), AMBER + (a,), NAVY + (a,), center=True)
        d.text((W / 2, 1210), "Segui Mezzo Minuto", font=F(XB, 46), fill=CREAM + (a,), anchor="ms")
        d.text((W / 2, 1268), "il contesto verificato delle notizie", font=F(MD, 36), fill=GREY + (a,), anchor="ms")
    captions(img, d, t)
    header(d, t)
    d.text((60, H - 210), "Fonti: " + C["fonti"], font=F(MD, 26), fill=GREY + (170,), anchor="ls")
    im = img.convert("RGB")
    q = t - A
    if 0 <= q < 0.14: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.35 * (1 - q / 0.14))
    for s in S[1:]:
        q = t - tv(s["da"])
        if 0 <= q < 0.1: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.15 * (1 - q / 0.1))
    vs = [s for s in S if s["tipo"] == "verdetto"]
    if vs:
        q = (t - tv(vs[0]["timbro"]) - 0.18) / 0.22
        if 0 <= q < 1:
            dx = int(16 * (1 - q) * math.sin(q * 40)); im = im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, int(dx * 0.6)))
    return im

def sfx(out):
    import soundfile as sf
    sr = 48000; n = int(D * sr); a = np.zeros(n, np.float32); r = np.random.default_rng(1)
    def add(t, s):
        i = int(t * sr)
        if 0 <= i < n: a[i:i + len(s)] += s[:n - i]
    def whoosh(d=0.45, g=0.5):
        m = int(d * sr); w = r.normal(0, 1, m).astype(np.float32); k = np.exp(-np.linspace(0, 6, 64))
        return np.convolve(w, k / k.sum(), "same") * np.sin(np.linspace(0, np.pi, m)) ** 2 * g
    def thud(g=0.9):
        m = int(0.6 * sr); tt = np.arange(m) / sr; f = 110 * np.exp(-tt * 6) + 45
        s = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 7) + r.normal(0, 1, m) * np.exp(-tt * 40) * 0.5
        return (s * g).astype(np.float32)
    def pop(g=0.3):
        m = int(0.12 * sr); tt = np.arange(m) / sr; f = 500 + 900 * tt / 0.12
        return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 30) * g).astype(np.float32)
    add(A - 0.05, thud(0.8)); add(A - 0.3, whoosh(0.5, 0.6))
    for s in C["scene"][1:]: add(tv(s["da"]) - 0.25, whoosh())
    for s in C["scene"]:
        for x in s.get("voci", []):
            if isinstance(x[-1], bool): add(tv(x[2]), pop())
            elif isinstance(x[-1], (int, float)): add(tv(x[-1]), pop())
        if s["tipo"] == "verdetto": add(tv(s["timbro"]) + 0.15, thud(1.0))
    a = a / max(1e-6, np.abs(a).max()) * 0.8
    sf.write(out, a, sr)

if __name__ == "__main__":
    m = sys.argv[2]
    if m == "still":
        os.makedirs(os.path.join(DIR, "r"), exist_ok=True)
        for x in sys.argv[3:]: scene(float(x)).save(os.path.join(DIR, "r", f"f_{float(x):05.2f}.jpg"), quality=88)
    elif m == "sfx": sfx(sys.argv[3])
    else:
        i0, i1, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(scene(i / FPS).tobytes())
        p.stdin.close(); p.wait()
