"""Allunga un brano corto a una durata esatta, ripetendo un blocco a tempo e lasciando la chiusa alla fine.

uso: python3 loop_musica.py BRANO.mp3 DURATA_SECONDI USCITA.wav [--lufs -25.3] [--info]

- trova i battiti (librosa), il punto dove inizia la chiusa (l'energia crolla)
  e un blocco di battute intere (multiplo di 4 battute) che finisce prima della chiusa;
- costruisce: inizio … blocco ripetuto … chiusa, con dissolvenze brevi alle giunture
  sul battito, in modo che la chiusa cada esattamente alla fine del video;
- normalizza il risultato a -25,3 LUFS: è il livello della musica di sottofondo
  approvato (Winery a volume 0,25). Nel mix poi la musica entra a volume 1,0.
Con --info stampa solo l'analisi.
"""
import sys, argparse, subprocess, json, numpy as np, librosa, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("brano"); ap.add_argument("durata", type=float); ap.add_argument("out")
ap.add_argument("--lufs", type=float, default=-25.3); ap.add_argument("--info", action="store_true")
ap.add_argument("--battute", default="", help="blocco da ripetere, es. 4-7 (battute da 4 battiti contate dal primo battito); vedi BRANI.md")
a = ap.parse_args()

y, sr = librosa.load(a.brano, sr=48000, mono=False)
if y.ndim == 1: y = np.stack([y, y])
mono = y.mean(axis=0)
tempo, bf = librosa.beat.beat_track(y=librosa.resample(mono, orig_sr=sr, target_sr=22050), sr=22050)
beats = librosa.frames_to_time(bf, sr=22050)
period = float(np.median(np.diff(beats)))
# griglia regolare dal primo battito (i brani di libreria sono a tempo fisso)
grid = beats[0] + period * np.arange(int((len(mono) / sr - beats[0]) / period) + 1)
# inizio della chiusa: ultimo secondo con energia vicina alla media del brano
hop = 2400; rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, "same")[::hop]) + 1e-9
db = 20 * np.log10(rms); t = np.arange(len(db)) * hop / sr
ref = np.median(db[db > db.max() - 30])
loud = t[db > ref - 6]
fine_piena = float(loud[-1])
A = grid[0]
cand = [g for i, g in enumerate(grid) if g <= fine_piena - 0.25 and i >= 16 and i % 4 == 0]
B = cand[-1]
if a.battute:
    b0, b1 = map(int, a.battute.split("-"))
    A, B = grid[0] + (b0 - 1) * 4 * period, grid[0] + b1 * 4 * period
nb = int(round((B - A) / period))
blocco = B - A
dur = len(mono) / sr
if a.info or True:
    print(json.dumps(dict(brano=a.brano, durata=round(dur, 2), bpm=round(60 / period, 1),
                          inizio_blocco=round(A, 2), fine_blocco=round(B, 2), battiti_blocco=nb,
                          chiusa_da=round(B, 2) if not a.battute else round(B, 2), energia_piena_fino=round(fine_piena, 2))))
if a.info: sys.exit()

def seg(t0, t1): return y[:, int(t0 * sr):int(t1 * sr)]
coda = seg(B, dur)                       # chiusa (fino alla fine del file)
target = a.durata
corpo_len = target - coda.shape[1] / sr   # quanto deve durare ciò che precede la chiusa
# corpo = ripetizioni del blocco [A,B); si parte dentro il brano in modo da finire esattamente su B
intro = seg(0, A)                         # quello che viene prima del blocco (intro)
n = max(1, int(np.ceil((corpo_len - A) / blocco)))
corpo = np.concatenate([intro] + [seg(A, B)] * n, axis=1)
X = int(0.04 * sr)                        # dissolvenza alle giunture (40 ms, sul battito)
w = np.linspace(0, 1, X)
for k in range(1, n):                     # ammorbidisce le giunture
    i = intro.shape[1] + k * int(round(blocco * sr))
    if i + X < corpo.shape[1] and i - X > 0:
        prev_tail = y[:, int(B * sr):int(B * sr) + X]
        if prev_tail.shape[1] == X:
            corpo[:, i:i + X] = corpo[:, i:i + X] * w + prev_tail * (1 - w)
corpo = corpo[:, corpo.shape[1] - int(round(corpo_len * sr)):]   # taglia dall'inizio
# la prima battuta tagliata entra con una dissolvenza
fi = int(0.6 * sr); corpo[:, :fi] *= np.linspace(0, 1, fi)
out = np.concatenate([corpo, coda], axis=1)
# raccordo corpo/chiusa
j = corpo.shape[1]
if j > X:
    out[:, j - X:j] = out[:, j - X:j] * (1 - w) + y[:, int(B * sr) - X:int(B * sr)] * w
sf.write(a.out + ".tmp.wav", out.T, sr)
# normalizzazione al livello di sottofondo
m = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.out + ".tmp.wav", "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
I = float([l for l in m.splitlines() if l.strip().startswith("I:")][-1].split()[1])
g = 10 ** ((a.lufs - I) / 20)
sf.write(a.out, np.clip(out * g, -1, 1).T, sr)
import os; os.remove(a.out + ".tmp.wav")
print(f"ok {a.out}: {out.shape[1]/sr:.2f}s, chiusa negli ultimi {coda.shape[1]/sr:.2f}s, guadagno {20*np.log10(g):.1f} dB")
