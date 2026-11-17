"""Crea il notiziario nella nuova modalità: video con musica + slide 2-6 del carosello.

uso: python3 strumenti/notiziario/crea.py CONFIG.json CARTELLA_USCITA
- CONFIG.json: vedi LEGGIMI_NOTIZIARIO.md (news, evidenza, shots, sondaggio facoltativo, clip_dir)
- in uscita: video.mp4 (31,5 s, 1080x1920, musica del notiziario), slide_02.jpg ... slide_06.jpg (1080x1350),
  prev_1.jpg ... prev_5.jpg (un fotogramma per notizia, per il controllo)
Copertina, slide_01 e slide_07 restano quelle del kit.
"""
import sys, os, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
cfgp, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(out, exist_ok=True)
R = os.path.join(HERE, "notiziario_v2.py")
N = int(round(31.5 * 30)); h = N // 2
p1 = subprocess.Popen(["python3", R, cfgp, "vid", "0", str(h), f"{out}/_a.mp4"], stderr=subprocess.DEVNULL)
p2 = subprocess.Popen(["python3", R, cfgp, "vid", str(h), str(N), f"{out}/_b.mp4"], stderr=subprocess.DEVNULL)
subprocess.run(["python3", R, cfgp, "slide", out], check=True, stderr=subprocess.DEVNULL)
assert p1.wait() == 0 and p2.wait() == 0, "render del video non riuscito"
open(f"{out}/_l.txt", "w").write(f"file '{out}/_a.mp4'\nfile '{out}/_b.mp4'\n")
mus = os.path.join(HERE, "musica_notiziario.mp3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/_l.txt", "-i", mus,
                "-filter_complex", "[1:a]atrim=0:31.5,afade=t=out:st=30.3:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", f"{out}/video.mp4"], check=True)
for f in ("_a.mp4", "_b.mp4", "_l.txt"): os.remove(f"{out}/{f}")
cuts = [0, 6.41, 11.75, 17.07, 22.41]
for i, c in enumerate(cuts):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c + 4.0), "-i", f"{out}/video.mp4", "-frames:v", "1", "-vf", "scale=540:960", f"{out}/prev_{i + 1}.jpg"], check=True)
print("VIDEO", f"{out}/video.mp4"); print("SLIDE", " ".join(f"{out}/slide_{k:02d}.jpg" for k in range(2, 7)))
print("PREVIEW", " ".join(f"{out}/prev_{i}.jpg" for i in range(1, 6)))
