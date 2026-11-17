"""Scarica foto e video gratuiti da Pexels senza chiave API (gli id si trovano con WebSearch, allowed_domains pexels.com).

uso: python3 strumenti/notiziario/scarica.py CARTELLA foto:ID video:ID[:fps[:v]] ...
- foto -> pxfID.jpg (lato lungo ~2200 px); video -> pxID.mp4 (indovina il nome del file: risoluzione e fps)
- fps tipici: 25, 24, 30, 60 (29,97 -> 30; 23,98 -> 24; 59,94 -> 60); ":v" se il video è verticale
Stampa OK/NON TROVATO per ciascuno: se un video non si trova, prova un altro id.
"""
import sys, subprocess, os
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def code(u, rng=True):
    a = ["curl", "-s", "-m", "20", "-o", "/dev/null", "-w", "%{http_code}"] + (["-r", "0-100"] if rng else []) + [u]
    return subprocess.run(a, capture_output=True, text=True).stdout
for spec in sys.argv[2:]:
    kind, rest = spec.split(":", 1); p = rest.split(":"); vid = p[0]
    if kind == "foto":
        fn = f"{out}/pxf{vid}.jpg"
        subprocess.run(["curl", "-s", "-m", "60", "-o", fn, f"https://images.pexels.com/photos/{vid}/pexels-photo-{vid}.jpeg?auto=compress&cs=tinysrgb&h=2200"])
        ok = os.path.exists(fn) and os.path.getsize(fn) > 20000
        print(f"foto {vid}", "OK" if ok else "NON TROVATA", flush=True); continue
    fps = [p[1]] if len(p) > 1 and p[1] else ["25", "24", "30", "60", "50"]; vert = len(p) > 2
    sizes = [("hd", 1080, 1920), ("hd", 1920, 1080), ("uhd", 2160, 3840), ("uhd", 3840, 2160), ("hd", 1280, 720), ("hd", 720, 1280), ("hd", 1366, 720), ("uhd", 2560, 1440)]
    if not vert: sizes = [sizes[1], sizes[0], sizes[4], sizes[6], sizes[3], sizes[2], sizes[5], sizes[7]]
    got = None
    for f in fps:
        for q, w, h in sizes:
            u = f"https://videos.pexels.com/video-files/{vid}/{vid}-{q}_{w}_{h}_{f}fps.mp4"
            if code(u) in ("206", "200"): got = u; break
        if got: break
    if got:
        subprocess.run(["curl", "-s", "-m", "300", "-o", f"{out}/px{vid}.mp4", got]); print(f"video {vid} OK", got.rsplit("/", 1)[1], flush=True)
    else: print(f"video {vid} NON TROVATO", flush=True)
