"""Bozza B di sigla del notiziario: stile «intro da telegiornale», 87 BPM in la minore, violino solista (originale).

Stessa struttura della sigla attuale del kit: 30,5 s, uno stacco ogni 5,5 s (5 notizie)
e la chiusa da 27,5 s. Tempo 130,9 BPM: ogni notizia dura esattamente 3 battute.
Ispirazione: il carattere epico degli «Epic Classical Strings» (archi incalzanti, re minore),
senza usarne note o campioni.

uso: python3 sigla_violino.py USCITA.wav
Richiede: fluidsynth + /usr/share/sounds/sf2/FluidR3_GM.sf2, pretty_midi.
"""
import sys, subprocess, numpy as np, pretty_midi as pm, soundfile as sf

OUT = sys.argv[1] if len(sys.argv) > 1 else "sigla_violino_b.wav"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
DUR, CUT = 30.5, 5.5
BEAT = CUT / 8                         # 2 battute da 4 per notizia (87,3 BPM)
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

# accordi (la minore): ogni notizia = 2 battute
A_, F_, C_, G_, D_, E_ = 45, 41, 48, 43, 50, 52
CH = {A_: [57, 60, 64], F_: [57, 60, 65], C_: [55, 60, 64], G_: [55, 59, 62], D_: [57, 62, 65], E_: [56, 59, 64]}
blocchi = [[A_, F_], [C_, G_], [A_, F_], [D_, E_], [F_, E_]]
# melodia originale del violino, 8 battiti per notizia (battito, nota, durata)
MOTIVI = [
 [(0, 76, 1), (1, 72, .5), (1.5, 74, .5), (2, 76, 2), (4, 77, 1), (5, 76, .5), (5.5, 74, .5), (6, 72, 2)],
 [(0, 79, 1), (1, 76, .5), (1.5, 77, .5), (2, 79, 2), (4, 74, 1.5), (5.5, 76, .5), (6, 71, 2)],
 [(0, 81, 1), (1, 76, .5), (1.5, 79, .5), (2, 81, 2), (4, 84, 1), (5, 81, .5), (5.5, 79, .5), (6, 77, 2)],
 [(0, 77, 1), (1, 81, 1), (2, 86, 2), (4, 83, 1), (5, 80, 1), (6, 76, 2)],
 [(0, 84, 1.5), (1.5, 81, .5), (2, 77, 2), (4, 80, 1.5), (5.5, 83, .5), (6, 88, 2)]]
for n, (blocco, mot) in enumerate(zip(blocchi, MOTIVI)):
    t0 = n * CUT
    for b, root in enumerate(blocco):
        tb = t0 + b * 4 * BEAT
        for p in CH[root]: note(archi, p, tb, 4 * BEAT, 50 if n == 0 else 60)
        # pulsazione da notiziario: pizzicato in semicrome sulla fondamentale e la quinta
        for k in range(16):
            note(pizz, [root + 12, root + 19][k % 2], tb + k * BEAT / 4, BEAT / 4, 80 if k % 4 == 0 else 60)
        # bassi sul primo e terzo battito, violoncelli a crome
        for k in (0, 2): note(bassi, root - 12, tb + k * BEAT, BEAT * 1.6, 90)
        for k in range(8): note(celli, root, tb + k * BEAT / 2, BEAT / 2 * 0.7, 78 if k % 2 == 0 else 62)
    for (bt, p, d) in mot:
        note(violino, p, t0 + bt * BEAT, d * BEAT * 0.97, 98 if bt in (0, 4) else 86)
    note(timp, A_ - 12, t0, 1.0, 112 if n else 96)
    note(timp, A_ - 12, t0 + 6 * BEAT, 0.3, 70); note(timp, E_ - 24, t0 + 7 * BEAT, 0.3, 80)

# chiusa (27,5 s): accordo pieno di re minore, timpani in rullata, violino tenuto in alto
tf = 5 * CUT
for p in [33, 45, 52, 57, 60, 64, 69]:
    note(archi, p, tf, 2.8, 100)
note(archi2, 57, tf, 2.8, 90); note(celli, 33, tf, 2.8, 100); note(bassi, 33, tf, 2.8, 100)
note(violino, 81, tf, 2.6, 105)
for k in range(10): note(timp, 33, tf + k * 0.09, 0.09, 70 + 4 * k)
note(timp, 33, tf + 0.95, 1.5, 120)

mid.write("/tmp/sigla_violino_b.mid")
subprocess.run(["fluidsynth", "-ni", "-g", "0.8", "-r", "44100", "-F", "/tmp/sigla_raw_b.wav", SF2, "/tmp/sigla_violino_b.mid"],
               check=True, capture_output=True)
y, sr = sf.read("/tmp/sigla_raw_b.wav")
N = int(DUR * sr)
y = y[:N] if len(y) >= N else np.vstack([y, np.zeros((N - len(y), 2))])
fl = int(0.8 * sr); y[-fl:] *= np.linspace(1, 0, fl)[:, None]
y = np.tanh(y * 1.2)
y /= np.abs(y).max() / 0.89
sf.write(OUT, y, sr)
print(f"ok {OUT}: {N/sr:.1f}s, {BPM:.1f} BPM, stacchi ogni {CUT}s")
