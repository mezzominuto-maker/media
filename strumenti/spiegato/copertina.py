"""Copertina dei reel «Il Contesto» (Mezzo Minuto).

Modello unico per tutta la rubrica: cambiano solo foto, occhiello, titolo e sottotitolo.
Le parole tra *asterischi* nel titolo diventano gialle.

Esempio:
  python3 copertina.py --foto ruspa.png --occhiello "LA BOZZA DI FDI" \
      --titolo "CONDONO," --titolo "*DI NUOVO?*" \
      --sotto "Cosa cambia e chi è contrario" --out copertina.png

Il testo resta dentro la fascia centrale 1080x1350 (taglio 4:5 della griglia
Instagram/Facebook): con --anteprima salva anche quel ritaglio per controllo.
"""
import argparse, re, numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FD = "/home/claude/media/strumenti/fonts/"
LOGO = "/home/claude/media/strumenti/logo_mark.png"
NAVY = (13, 18, 33); NAVY2 = (24, 36, 62); CREAM = (240, 236, 226)
AMBER = (255, 196, 61); GOLD = (208, 192, 150); GREY = (150, 160, 185)
BLK = "InterDisplay-Black.otf"; XB = "Inter-ExtraBold.otf"; SB = "Inter-SemiBold.otf"
SAFE_TOP, SAFE_BOT = (H - 1350) // 2, (H + 1350) // 2   # 285 .. 1635

def F(n, s): return ImageFont.truetype(FD + n, s)

def sfondo():
    y = np.linspace(0, 1, H)[:, None, None]
    a = np.array(NAVY, np.float32) * (1 - y) + np.array(NAVY2, np.float32) * y * 0.9
    a = np.broadcast_to(a, (H, W, 3)).copy()
    gx, gy = np.meshgrid(np.arange(W), np.arange(H))
    a += ((((gx + gy) % 90) < 45)[..., None]) * 5.0
    return a

def foto_layer(path, fx, fy, alto):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, alto / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = int((im.width - W) * fx); y = int((im.height - alto) * fy)
    a = np.asarray(im.crop((x, y, x + W, y + alto))).astype(np.float32)
    g = a.mean(axis=2, keepdims=True); a = a * 0.75 + g * 0.25
    return a * 0.78 + np.array(NAVY, np.float32) * 0.15

def lente(d, x, y, r, col, w):
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=w)
    d.line([(x + r * 0.7, y + r * 0.7), (x + r * 1.55, y + r * 1.55)], fill=col, width=w + 2)

def titolo_righe(d, righe, cy_top, max_w=960):
    size = 170
    while size > 80:
        f = F(BLK, size)
        if all(f.getlength(r.replace("*", "")) <= max_w for r in righe): break
        size -= 6
    f = F(BLK, size); lh = int(size * 1.02); y = cy_top
    for r in righe:
        parti = re.split(r"(\*[^*]+\*)", r); tot = f.getlength(r.replace("*", ""))
        x = (W - tot) / 2
        for p in parti:
            if not p: continue
            gialla = p.startswith("*"); p = p.strip("*")
            d.text((x + 5, y + 7), p, font=f, fill=(0, 0, 0, 150))      # ombra
            d.text((x, y), p, font=f, fill=AMBER if gialla else CREAM)
            x += f.getlength(p)
        y += lh
    return y

def copertina(foto, occhiello, righe, sotto, out, fx=0.5, fy=0.5, anteprima=False):
    a = sfondo()
    alto = 1250
    ph = foto_layer(foto, fx, fy, alto)
    m = np.ones((alto, 1, 1), np.float32)
    fade = np.linspace(0, 1, 420)[:, None, None]
    m[alto - 420:] = 1 - fade ** 1.3
    top = np.linspace(1, 0, 260)[:, None, None] ** 2 * 0.55          # leggibilità dell'intestazione
    a[:alto] = a[:alto] * (1 - m) + ph * m
    a[:260] *= (1 - top)
    c = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)

    # intestazione (fuori dalla fascia 4:5, come nel video)
    logo = Image.open(LOGO).convert("RGBA"); logo = logo.resize((int(logo.width * 64 / logo.height), 64))
    L.alpha_composite(logo, (60, 120))
    d.text((118, 152), "MEZZO MINUTO", font=F(BLK, 34), fill=GOLD, anchor="lm")

    # etichetta della rubrica, dentro la fascia 4:5
    f = F(BLK, 46); lab = "IL CONTESTO"; tw = f.getlength(lab)
    bw = int(tw + 150); bx = (W - bw) // 2; by = 840
    d.rounded_rectangle([bx, by, bx + bw, by + 84], 42, fill=AMBER)
    lente(d, bx + 52, by + 38, 17, NAVY, 7)
    d.text((bx + 95, by + 43), lab, font=f, fill=NAVY, anchor="lm")

    y = by + 125
    if occhiello:
        d.text((W / 2, y + 22), occhiello, font=F(XB, 46), fill=CREAM, anchor="mm")
        y += 75
    y = titolo_righe(d, righe, y)
    if sotto:
        d.text((W / 2, y + 62), sotto, font=F(SB, 50), fill=CREAM, anchor="mm")
        y += 110
    d.rectangle([W / 2 - 60, SAFE_BOT - 70, W / 2 + 60, SAFE_BOT - 62], fill=AMBER)
    d.text((W / 2, SAFE_BOT - 25), "Capire le notizie", font=F(SB, 36), fill=GREY, anchor="mm")
    if y > SAFE_BOT - 90: print("ATTENZIONE: il testo esce dalla fascia 4:5, accorcia il titolo")
    c.alpha_composite(L)
    c = c.convert("RGB"); c.save(out, quality=95)
    if anteprima:
        c.crop((0, SAFE_TOP, W, SAFE_BOT)).save(out.rsplit(".", 1)[0] + "_griglia.jpg", quality=90)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True); ap.add_argument("--occhiello", default="")
    ap.add_argument("--titolo", action="append", required=True); ap.add_argument("--sotto", default="")
    ap.add_argument("--fx", type=float, default=0.5); ap.add_argument("--fy", type=float, default=0.5)
    ap.add_argument("--out", required=True); ap.add_argument("--anteprima", action="store_true")
    a = ap.parse_args()
    copertina(a.foto, a.occhiello, a.titolo, a.sotto, a.out, a.fx, a.fy, a.anteprima)
