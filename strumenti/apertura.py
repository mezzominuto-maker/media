"""Apertura forte + reel intero.
uso: python3 apertura.py SORGENTE CFG.json INIZIO FINE CARTELLA
- SORGENTE: il video approvato (1080x1920, sottotitoli già impressi), lo STESSO usato per la versione approvata
- INIZIO/FINE: secondi della frase forte dentro SORGENTE (2-4 s); i tagli si agganciano ai silenzi
Scrive CARTELLA/src.mp4 (apertura + reel intero), CARTELLA/cfg.json (tempi spostati), CARTELLA/hook.json."""
import json, subprocess, sys, os, re
def silences(src, a, b):
    out = subprocess.run(["ffmpeg","-hide_banner","-ss",str(a),"-t",str(b-a),"-i",src,"-vn","-af","silencedetect=noise=-33dB:d=0.08","-f","null","-"],capture_output=True,text=True).stderr
    return [float(x)+a for x in re.findall(r"silence_start: ([\d.]+)",out)], [float(x)+a for x in re.findall(r"silence_end: ([\d.]+)",out)]
def snap(src,a,b):
    st,en=silences(src,max(0,a-0.8),b+0.9)
    ends=[e for e in en if a-0.6<=e<=a+0.25]; a2=max(ends) if ends else a
    starts=[s for s in st if b-0.3<=s<=b+0.7]; b2=min(starts)+0.08 if starts else b
    return round(max(0,a2-0.05),2), round(b2,2)
def enc(src,a,d,out):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(a),"-t",f"{d:.3f}","-i",src,"-filter_complex",
      f"[0:v]fps=30,format=yuv420p[v];[0:a]aresample=44100,afade=t=in:st=0:d=0.03,afade=t=out:st={max(0,d-0.06):.3f}:d=0.06[a]",
      "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","16","-c:a","aac","-b:a","192k","-ac","2",out],check=True)
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
src,cfgp,a,b,w=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
os.makedirs(w,exist_ok=True)
cfg=json.load(open(cfgp,encoding="utf-8")); sd=dur(src)
# controllo anti-errore Boschi: la sorgente deve essere quella del reel approvato (fine entro pochi secondi dalla durata)
if not (cfg["content_end"]-0.3 <= sd <= cfg["content_end"]+4):
    sys.exit(f"STOP: la sorgente dura {sd:.1f}s ma il reel approvato finisce a {cfg['content_end']}s: non è la stessa sorgente")
a,b=snap(src,a,b)
enc(src,a,b-a,w+"/h.mp4"); enc(src,0,sd,w+"/m.mp4")
open(w+"/l.txt","w").write("file 'h.mp4'\nfile 'm.mp4'\n")
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",w+"/l.txt","-c","copy",w+"/src.mp4"],check=True)
hd=dur(w+"/h.mp4")
cfg["context_start"]=round(cfg["context_start"]+hd,2); cfg["content_end"]=round(cfg["content_end"]+hd,2); cfg["full"]=True
json.dump(cfg,open(w+"/cfg.json","w"),ensure_ascii=False,indent=1)
json.dump({"a":a,"b":b,"hd":round(hd,3)},open(w+"/hook.json","w"))
print("apertura",a,b,"durata",round(hd,2))
