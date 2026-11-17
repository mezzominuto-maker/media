"""Bozza di nuova sigla del notiziario Mezzo Minuto: violino solista e archi (originale).

Stessa struttura della sigla attuale del kit: 30,5 s, uno stacco ogni 5,5 s (5 notizie)
e la chiusa da 27,5 s. Tempo 130,9 BPM: ogni notizia dura esattamente 3 battute.
Ispirazione: il carattere epico degli «Epic Classical Strings» (archi incalzanti, re minore),
senza usarne note o campioni.

uso: python3 sigla_violino.py USCITA.wav
Richiede: fluidsynth + /usr/share/sounds/sf2/FluidR3_GM.sf2, pretty_midi.
"""
import sys, subprocess, numpy as np, pretty_midi as pm, soundfile as sf

OUT = sys.argv[1] if len(sys.argv) > 1 else "sigla_violino.wav"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
DUR, CUT = 30.5, 5.5
BEAT = CUT / 12                        # 3 battute da 4 per notizia
BPM = 60 / BEAT
mid = pm.PrettyMIDI(initial_tempo=BPM)
def inst(prog, name): i = pm.Instrument(program=prog, name=name); mid.instruments.append(i); return i
violino = inst(40, "violino")          # Violin
archi = inst(48, "archi")              # String Ensemble 1
archi2 = inst(49, "archi lenti")       # String Ensemble 2
celli = inst(42, "violoncelli")        # Cello
bassi = inst(43, "contrabbassi")       # Contrabass
pizz = inst(45, "pizzicato")           # Pizzicato Strings
timp = inst(47, "timpani")             # Timpani
def note(i, p, t, d, v): i.notes.append(pm.Note(velocity=int(v), pitch=int(p), start=t, end=t + d))

# accordi per battuta (re minore): ogni notizia = i - VI - VII, l'ultima va sulla dominante
D, Bb, C, A, F, Gm = 50, 46, 48, 45, 53, 43
CH = {D: [62, 65, 69], Bb: [58, 62, 65], C: [60, 64, 67], A: [57, 61, 64], F: [57, 60, 65], Gm: [55, 58, 62]}
blocchi = [[D, Bb, C], [D, Bb, C], [F, C, D], [Gm, Bb, C], [D, Bb, A]]

# motivo del violino (in battiti, altezza, durata) su 3 battute; varianti per notizia
M1 = [(0, 74, 1.5), (1.5, 69, .5), (2, 74, 1), (3, 77, 1),      # re-la-re-fa
      (4, 76, 1.5), (5.5, 74, .5), (6, 72, 1), (7, 70, 1),       # mi-re-do-sib
      (8, 72, 2.5), (10.5, 76, .5), (11, 77, 1)]                  # do ... mi-fa (slancio)
M2 = [(0, 81, 1.5), (1.5, 77, .5), (2, 81, 1), (3, 84, 1),
      (4, 82, 1.5), (5.5, 81, .5), (6, 79, 1), (7, 77, 1),
      (8, 79, 3), (11, 76, 1)]
M3 = [(0, 77, 1), (1, 76, .5), (1.5, 74, .5), (2, 72, 2),
      (4, 74, 1), (5, 76, .5), (5.5, 77, .5), (6, 79, 2),
      (8, 81, 3), (11, 79, .5), (11.5, 77, .5)]
M4 = [(0, 79, 1.5), (1.5, 77, .5), (2, 74, 2),
      (4, 77, 1.5), (5.5, 79, .5), (6, 81, 2),
      (8, 79, 2), (10, 81, 1), (11, 84, 1)]
M5 = [(0, 86, 1.5), (1.5, 81, .5), (2, 86, 1), (3, 89, 1),
      (4, 88, 1.5), (5.5, 86, .5), (6, 82, 2),
      (8, 85, 2), (10, 88, 2)]                                    # sale verso la chiusa
MOTIVI = [M1, M2, M3, M4, M5]

for n, (blocco, mot) in enumerate(zip(blocchi, MOTIVI)):
    t0 = n * CUT
    for b, root in enumerate(blocco):
        tb = t0 + b * 4 * BEAT
        # tappeto di archi (entra piano nella prima notizia)
        for p in CH[root]:
            note(archi, p, tb, 4 * BEAT, 52 if n == 0 else 62)
        note(archi2, root + 12, tb, 4 * BEAT, 50)
        # ostinato di violoncelli e contrabbassi a crome, accento sui battiti
        for k in range(8):
            v = 92 if k % 2 == 0 else 70
            note(celli, root, tb + k * BEAT / 2, BEAT / 2 * 0.8, v)
            if k % 2 == 0: note(bassi, root - 12, tb + k * BEAT / 2, BEAT / 2 * 0.9, 85)
        # pizzicato in semicrome sull'arpeggio (dalla seconda notizia in poi)
        if n >= 1:
            arp = CH[root] + [CH[root][1] + 12]
            for k in range(16):
                note(pizz, arp[[0, 1, 2, 3, 2, 1, 0, 1][k % 8]], tb + k * BEAT / 4, BEAT / 4, 58 if k % 4 else 74)
    # violino solista
    for (b, p, d) in mot:
        note(violino, p, t0 + b * BEAT, d * BEAT * 0.97, 96 if b in (0, 4, 8) else 84)
    # timpano sullo stacco di ogni notizia (+ rullata breve prima)
    note(timp, D - 12 if n % 2 == 0 else A - 12, t0, 1.2, 112 if n else 100)
    if n > 0:
        for k in range(4): note(timp, A - 12, t0 - (4 - k) * BEAT / 4, BEAT / 4, 60 + 10 * k)

# chiusa (27,5 s): accordo pieno di re minore, timpani in rullata, violino tenuto in alto
tf = 5 * CUT
for p in [38, 50, 57, 62, 65, 69, 74]:
    note(archi, p, tf, 2.8, 100)
note(archi2, 62, tf, 2.8, 90); note(celli, 38, tf, 2.8, 100); note(bassi, 26, tf, 2.8, 100)
note(violino, 86, tf, 2.6, 105)
for k in range(10): note(timp, 26, tf + k * 0.09, 0.09, 70 + 4 * k)
note(timp, 26, tf + 0.95, 1.5, 120)

mid.write("/tmp/sigla_violino.mid")
subprocess.run(["fluidsynth", "-ni", "-g", "0.8", "-r", "44100", "-F", "/tmp/sigla_raw.wav", SF2, "/tmp/sigla_violino.mid"],
               check=True, capture_output=True)
y, sr = sf.read("/tmp/sigla_raw.wav")
N = int(DUR * sr)
y = y[:N] if len(y) >= N else np.vstack([y, np.zeros((N - len(y), 2))])
fl = int(0.8 * sr); y[-fl:] *= np.linspace(1, 0, fl)[:, None]
y = np.tanh(y * 1.2)
y /= np.abs(y).max() / 0.89
sf.write(OUT, y, sr)
print(f"ok {OUT}: {N/sr:.1f}s, {BPM:.1f} BPM, stacchi ogni {CUT}s")
