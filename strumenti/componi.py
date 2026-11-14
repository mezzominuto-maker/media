"""Schermo intero con sfumatura, volto sotto il titolo e centrato, controllo sottotitoli.
uso: python3 componi.py CARTELLA SHOTS.json PARAMETRI.json
CARTELLA: quella creata da apertura.py (src.mp4, cfg.json, hook.json)
SHOTS.json: da analizza.py (sulla SORGENTE, non su src.mp4)
PARAMETRI.json: {"eyes": riga degli occhi nella sorgente, "band_top": prima riga utile (sotto loghi/bande),
  "bottom": ultima riga utile (sopra bande TV in basso), "E": dove mettere gli occhi in uscita (default 560),
  "faces": [x del volto per ogni inquadratura, in pixel della griglia di analizza.py]}
Regole: sottotitoli in uscita tra ~1260 e ~1480; se il riquadro del contesto copre il volto alza E (es. 700-760).
Scrive CARTELLA/out.mp4 e CARTELLA/verifica.png (fotogrammi con le frasi più lunghe: bordi azzurri = limiti schermo)."""
import json,subprocess,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
w,shp,pp=sys.argv[1],sys.argv[2],sys.argv[3]
J=json.load(open(shp)); sh=J["shots"]; s_old=J["s"]; F=json.load(open(pp))
H=json.load(open(w+"/hook.json")); a,b,hd=H["a"],H["b"],H["hd"]
cfg=json.load(open(w+"/cfg.json",encoding="utf-8"))
E_=F.get("E",560); S=max((1920-E_)/(F["bottom"]-F["eyes"]),1.0)
Y0=int(E_-(F["eyes"]-F["band_top"])*S)
cfg.update(full=True,full_y=Y0,full_s=round(S,4),band_top=F["band_top"])
VWn=int(1080*S)//2*2; xs=[]
faces=F.get("faces") or [None]*len(sh)
for s_,f in zip(sh,faces):
    if f is None: xs.append((VWn-1080)//2); continue
    fx=f/s_old*S; lo=s_["sub_lo"]/s_old*S; hi=s_["sub_hi"]/s_old*S
    x=fx-540; a_=max(0,hi-1080+10); b_=min(VWn-1080,lo-10)
    x=min(max(x,a_),b_) if a_<=b_ else (lo+hi)/2-540
    xs.append(int(min(max(x,0),VWn-1080)))
sub_out=int(Y0+(cfg.get("sub_y",1300)-F["band_top"])*S)
print("scala",round(S,3),"video da y",Y0,"sottotitoli a y",sub_out,"spostamenti",xs)
if Y0<0 or F["band_top"]+(1920-Y0)/S>1921: sys.exit("STOP: parametri fuori sorgente, rivedi eyes/bottom/band_top/E")
segs=[]
for s_,x in zip(sh,xs):
    lo,hi=max(s_["a"],a),min(s_["b"],b)
    if hi>lo: segs.append((lo-a,hi-a,x))
for s_,x in zip(sh,xs): segs.append((s_["a"]+hd,s_["b"]+hd,x))
segs.sort(); expr=str(xs[-1])
for st,en,x in reversed(segs): expr=f"if(lt(t\\,{en:.2f})\\,{x}\\,{expr})"
cfg["full_x"]=expr
json.dump(cfg,open(w+"/cfg.json","w"),ensure_ascii=False,indent=1)
subprocess.run(["python3",os.path.join(HERE,"impagina.py"),w+"/cfg.json",w+"/src.mp4",w+"/out.mp4",w+"/ov"],check=True)
ts=[round((b-a)/2,2)]
for s_ in sh: ts+=[round(hd+k/30.0,2) for k in s_.get("wide",[])[-2:]] or [round(hd+(s_["a"]+s_["b"])/2,2)]
tiles=[]
for i,t in enumerate(ts):
    p=f"{w}/v{i}.png"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i",w+"/out.mp4","-frames:v","1","-vf","drawbox=x=0:y=0:w=6:h=1920:c=cyan@1:t=fill,drawbox=x=1074:y=0:w=6:h=1920:c=cyan@1:t=fill,scale=216:384",p],check=True); tiles.append(p)
rows=[]
for j in range(0,len(tiles),8):
    r=tiles[j:j+8]; r+= [r[-1]]*(8-len(r)); o=f"{w}/row{j}.png"
    subprocess.run(["ffmpeg","-v","error","-y"]+sum([["-i",p] for p in r],[])+["-filter_complex","hstack=8",o],check=True); rows.append(o)
subprocess.run(["ffmpeg","-v","error","-y"]+sum([["-i",p] for p in rows],[])+(["-filter_complex",f"vstack={len(rows)}"] if len(rows)>1 else [])+[w+"/verifica.png"],check=True)
print("ok",w+"/out.mp4",w+"/verifica.png")
