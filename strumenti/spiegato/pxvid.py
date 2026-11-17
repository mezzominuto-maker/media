# Scarica clip Pexels senza chiave API indovinando il nome del file (risoluzione e fps).
# Gli id si trovano con la ricerca web (allowed_domains pexels.com).
import sys, subprocess, os
# uso: pxvid.py OUTDIR id:fps[:v] ...   (v = verticale)
out=sys.argv[1]
def ok(u):
    r=subprocess.run(["curl","-s","-r","0-100","-m","20","-o","/dev/null","-w","%{http_code}",u],capture_output=True,text=True).stdout
    return r=="206" or r=="200"
for spec in sys.argv[2:]:
    p=spec.split(":"); vid=p[0]; fps=[p[1]] if len(p)>1 and p[1] else ["25","24","30","60","50"]
    vert=len(p)>2
    sizes=[("hd",1080,1920),("hd",1920,1080),("uhd",2160,3840),("uhd",3840,2160),("hd",1280,720),("hd",720,1280),("uhd",2560,1440),("hd",1366,720)]
    if not vert: sizes=[sizes[1],sizes[0],sizes[3],sizes[2]]+sizes[4:]
    got=None
    for f in fps:
        for q,w,h in sizes:
            u=f"https://videos.pexels.com/video-files/{vid}/{vid}-{q}_{w}_{h}_{f}fps.mp4"
            if ok(u): got=u; break
        if got: break
    if got:
        fn=f"{out}/px{vid}.mp4"
        subprocess.run(["curl","-s","-m","300","-o",fn,got])
        print(vid,"OK",got.split("/")[-1],os.path.getsize(fn)//1024,"KB",flush=True)
    else: print(vid,"NON TROVATO",flush=True)
