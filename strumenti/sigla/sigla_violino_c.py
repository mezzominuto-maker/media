"""Bozza C di sigla del notiziario: energica, 131 BPM, la minore, violino solista + archi spiccato + batteria (originale).

30,5 s, uno stacco ogni 5,5 s (3 battute per notizia), chiusa da 27,5 s.
uso: python3 sigla_violino_c.py USCITA.wav   (richiede fluidsynth + FluidR3_GM.sf2, pretty_midi)
"""
import sys, subprocess, numpy as np, pretty_midi as pm, soundfile as sf

OUT = sys.argv[1] if len(sys.argv) > 1 else "sigla_violino_c.wav"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
DUR, CUT = 30.5, 5.5
B = CUT / 12; S = B / 4                 # battito e semicroma (130,9 BPM)
mid = pm.PrettyMIDI(initial_tempo=60 / B)
def inst(prog, name, drum=False):
    i = pm.Instrument(program=prog, name=name, is_drum=drum); mid.instruments.append(i); return i
vl = inst(40, "violino"); vl2 = inst(40, "violino ottava")
spic = inst(48, "archi spiccato"); pad = inst(49, "archi tenuti")
vc = inst(42, "violoncelli"); cb = inst(43, "contrabbassi")
tim = inst(47, "timpani"); hit = inst(55, "colpo orchestra")
dr = inst(0, "batteria", drum=True)
def n(i, p, t, d, v): i.notes.append(pm.Note(velocity=int(max(1, min(127, v))), pitch=int(p), start=t, end=t + d))

A, F, C, G, D, E = 45, 41, 48, 43, 50, 40
CH = {A: [57, 60, 64], F: [57, 60, 65], C: [55, 60, 64], G: [55, 59, 62], D: [57, 62, 65], E: [56, 59, 64]}
BLOCCHI = [[A, F, G], [A, F, E], [D, F, G], [A, C, G], [F, G, E]]
# violino: frasi ritmiche di 3 battute (battito, nota, durata in battiti)
FR = [
 [(0, 76, .5), (.5, 76, .25), (.75, 79, .25), (1, 81, 1), (2, 79, .5), (2.5, 76, .5), (3, 74, 1),
  (4, 72, .5), (4.5, 74, .5), (5, 76, 1.5), (6.5, 74, .5), (7, 72, 1), (8, 71, .5), (8.5, 72, .5), (9, 74, 1), (10, 76, 2)],
 [(0, 81, .5), (.5, 81, .25), (.75, 84, .25), (1, 86, 1), (2, 84, .5), (2.5, 81, .5), (3, 79, 1),
  (4, 77, .5), (4.5, 79, .5), (5, 81, 1.5), (6.5, 79, .5), (7, 77, 1), (8, 76, 1), (9, 80, 1), (10, 83, 2)],
 [(0, 77, .75), (.75, 81, .25), (1, 86, 1), (2, 84, .5), (2.5, 81, .5), (3, 77, 1),
  (4, 77, .5), (4.5, 81, .5), (5, 84, 1), (6, 86, 1), (7, 84, 1), (8, 83, .5), (8.5, 79, .5), (9, 81, 1), (10, 83, 2)],
 [(0, 88, .5), (.5, 88, .25), (.75, 86, .25), (1, 84, 1), (2, 83, .5), (2.5, 84, .5), (3, 81, 1),
  (4, 84, .5), (4.5, 86, .5), (5, 88, 1.5), (6.5, 86, .5), (7, 84, 1), (8, 83, .5), (8.5, 84, .5), (9, 86, 1), (10, 83, 2)],
 [(0, 89, .5), (.5, 88, .5), (1, 86, 1), (2, 84, .5), (2.5, 86, .5), (3, 88, 1),
  (4, 91, .5), (4.5, 89, .5), (5, 88, 1), (6, 86, 1), (7, 84, 1), (8, 83, 1), (9, 86, 1), (10, 88, 2)]]
KICK, SNARE, HHC, HHO, CRASH, TOMH, TOML, TOMF = 36, 38, 42, 46, 49, 50, 47, 41

for k, (blocco, fr) in enumerate(zip(BLOCCHI, FR)):
    t0 = k * CUT
    for b, root in enumerate(blocco):
        tb = t0 + b * 4 * B
        for p in CH[root]: n(pad, p, tb, 4 * B, 58)
        for s in range(16):                                   # 16 semicrome per battuta
            t = tb + s * S
            # archi spiccato: arpeggio in semicrome
            arp = [CH[root][0], CH[root][1], CH[root][2], CH[root][1] + 12]
            n(spic, arp[s % 4] + 12, t, S * 0.6, 88 if s % 4 == 0 else 66)
            # violoncelli: ostinato a semicrome con salto d'ottava
            n(vc, root + (12 if s % 4 == 2 else 0), t, S * 0.7, 96 if s % 4 == 0 else 72)
            # charleston chiuso in semicrome, aperto sul controtempo
            n(dr, HHO if s % 8 == 6 else HHC, t, S, 70 if s % 2 == 0 else 48)
        for s in (0, 6, 8, 11):                                # cassa sincopata
            n(dr, KICK, tb + s * S, S, 118); n(cb, root - 12, tb + s * S, S * 1.5, 100)
        for s in (4, 12): n(dr, SNARE, tb + s * S, S, 104)    # rullante su 2 e 4
    for (bt, p, d) in fr:                                       # violino + ottava sotto, più leggera
        n(vl, p, t0 + bt * B, d * B * 0.95, 110 if bt in (0, 4, 8) else 96)
        n(vl2, p - 12, t0 + bt * B, d * B * 0.95, 70)
    # stacco: crash, colpo d'orchestra, timpano
    n(dr, CRASH, t0, 1.5, 112 if k else 100); n(hit, 69, t0, 0.4, 100 if k else 80); n(tim, 33, t0, 1.0, 120)
    # rullata di tom e crescendo d'archi nell'ultimo battito prima dello stacco
    if k < 5:
        te = t0 + CUT
        for j, tom in enumerate([TOMH, TOMH, TOML, TOMF]): n(dr, tom, te - B + j * S, S, 90 + 8 * j)
        for j in range(8): n(pad, 81, te - B + j * S / 2, S / 2, 60 + 7 * j)

tf = 5 * CUT                                                   # chiusa
for p in [33, 45, 52, 57, 60, 64, 69, 76]: n(pad, p, tf, 2.6, 110)
n(vl, 93, tf, 2.4, 115); n(vl2, 81, tf, 2.4, 100); n(vc, 33, tf, 2.6, 115); n(cb, 33, tf, 2.6, 115)
n(dr, CRASH, tf, 2.5, 127); n(dr, KICK, tf, .3, 127); n(hit, 69, tf, .5, 120)
for j in range(12): n(tim, 33, tf + j * 0.07, 0.07, 70 + 4 * j)
n(tim, 33, tf + 0.9, 1.4, 127); n(dr, CRASH, tf + 0.9, 1.5, 110)

mid.write("/tmp/sigla_c.mid")
subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "44100", "-F", "/tmp/sigla_raw_c.wav", SF2, "/tmp/sigla_c.mid"], check=True, capture_output=True)
y, sr = sf.read("/tmp/sigla_raw_c.wav")
N = int(DUR * sr)
y = y[:N] if len(y) >= N else np.vstack([y, np.zeros((N - len(y), 2))])
fl = int(0.6 * sr); y[-fl:] *= np.linspace(1, 0, fl)[:, None]
y = np.tanh(y * 1.6)                                           # più presenza
y /= np.abs(y).max() / 0.92
sf.write(OUT, y, sr)
print(f"ok {OUT}: {N/sr:.1f}s, {60/B:.1f} BPM")
