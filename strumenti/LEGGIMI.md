# Strumenti reel Mezzo Minuto

Catena standard (clip verticali 1080x1920 con sottotitoli già impressi, es. Ssemble):
1. `python3 analizza.py SORGENTE CFG.json PREF` → inquadrature, limiti sottotitoli, foglio `PREF_shots.jpg`
2. `python3 apertura.py SORGENTE CFG.json INIZIO FINE CARTELLA` → frase forte + reel intero
3. `python3 componi.py CARTELLA PREF_shots.json PARAMETRI.json` → `out.mp4` + `verifica.png`

Interviste orizzontali (16:9): `python3 verticale.py SPEC.json SORGENTE_VERT.mp4` crea la sorgente
verticale a schermo intero con sottotitoli (spec: shots `fw:<cx>`/`fc:<cx>`, subs), poi
`apertura.py` + `impagina.py CARTELLA/cfg.json CARTELLA/src.mp4 out.mp4 lavoro` con cfg
`{"full": true, "crop_top": 0, "crop_bottom": 1920, "sub_y": 1250}`.

CFG.json (impaginazione): title, subtitle, fonte, context [2 frasi], context_start (s), question,
content_end (s, fine del parlato = durata della sorgente approvata), end_len 2.4, crop_top, crop_bottom, sub_y.
Requisiti: python3, ffmpeg, Pillow, numpy, opencv-python.
