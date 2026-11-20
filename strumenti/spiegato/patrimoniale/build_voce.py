# Ricostruisce voce.mp3: voce_v1.mp3 con le frasi sostituite (chiusa e, se c'è, citazione di Meloni)
import subprocess, os
def seg(f,a,b): return f"[{f}]atrim={a}:{b},asetpts=PTS-STARTPTS"
inp=["voce_v1.mp3","voce_finale.mp3"]; parts=[]
M=os.path.exists("voce_meloni.mp3")
if M: inp.append("voce_meloni.mp3")
def sil(d): return f"anullsrc=r=44100:cl=mono,atrim=0:{d}"
# originale fino a prima di «E Giorgia Meloni risponde» (58.57) / fino a prima di «La manovra va approvata» (69.72)
if M:
    parts+= [seg(0,0,58.45), seg(2,0,"DUR_M"), sil(0.3), seg(0,63.5,69.55)]
else:
    parts+= [seg(0,0,69.55)]
parts+= [seg(1,0,7.98), sil(0.3), seg(0,71.85,74.45)]
if M:
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voce_meloni.mp3"],capture_output=True,text=True).stdout)
    parts=[p.replace("DUR_M",str(d)) for p in parts]
fc=";".join(f"{p},aresample=44100,aformat=channel_layouts=mono[p{i}]" for i,p in enumerate(parts))+";"+"".join(f"[p{i}]" for i in range(len(parts)))+f"concat=n={len(parts)}:v=0:a=1[o]"
cmd=["ffmpeg","-v","error","-y"]
for f in inp: cmd+=["-i",f]
cmd+=["-filter_complex",fc,"-map","[o]","-b:a","192k","voce.mp3"]
subprocess.run(cmd,check=True); print("ok, meloni:",M)
