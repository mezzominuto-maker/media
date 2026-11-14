"""Inquadrature e limiti dei sottotitoli.
uso: python3 analizza.py SORGENTE CFG.json PREFISSO_USCITA
Scrive PREFISSO_shots.json (tagli, limiti sottotitoli) e PREFISSO_shots.jpg (un fotogramma per inquadratura con griglia ogni 100 px: linee rosse ogni 500)."""
import json,subprocess,sys,re,cv2,numpy as np
src,cfgp,pref=sys.argv[1],sys.argv[2],sys.argv[3]; cfg=json.load(open(cfgp,encoding="utf-8"))
ct=cfg.get("crop_top",0); cb=cfg.get("crop_bottom",1920); sub_y=cfg.get("sub_y",1300)
s=1920/(cb-ct); VW=int(1080*s)//2*2
out=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-vf","select='gt(scene,0.25)',showinfo","-f","null","-"],capture_output=True,text=True).stderr
cuts=[0.0]+[float(x) for x in re.findall(r"pts_time:([\d.]+)",out)]
D=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src]))
cuts=[c for c in cuts if c<cfg["content_end"]]+[min(D,cfg["content_end"])]
cap=cv2.VideoCapture(src); fps=cap.get(5)
bands=[];smalls=[];k=0
while True:
    ok,f=cap.read()
    if not ok: break
    bands.append(f[sub_y-40:sub_y+36:2,::2].copy() if k%3==0 else None)
    smalls.append(cv2.resize(f[ct:cb],(VW//4,480)) if k%5==0 else None)
    k+=1
nF=k
res=[]; tiles=[]
for i in range(len(cuts)-1):
    a,b=cuts[i],cuts[i+1]
    if b-a<0.3: continue
    idx=range(int(a*fps)+1,min(nF,int(b*fps)))
    los=[];his=[];wf=[]
    for k in idx:
        bd=bands[k]
        if bd is None: continue
        g=bd.min(2); wht=g>205; dark=(bd.max(2)<70)
        dk=cv2.dilate(dark.astype(np.uint8),np.ones((7,7),np.uint8))>0
        hsv=cv2.cvtColor(bd,cv2.COLOR_BGR2HSV)
        red=((hsv[...,0]<8)|(hsv[...,0]>170))&(hsv[...,1]>140)&(hsv[...,2]>140)
        txt=(wht&dk)
        cols=np.where(txt.sum(0)>=2)[0]*2
        if len(cols)<20: continue
        lo,hi=cols.min(),cols.max(); c=(lo+hi)/2
        if abs(c-540)>70 or hi-lo<80: continue
        los.append(lo);his.append(hi);wf.append((hi-lo,k))
    if los:
        lo=int(np.percentile(los,1)*s+ (1-s)*0); hi=int(np.percentile(his,99)*s)
    else: lo,hi=0,VW
    m=(idx[0]+idx[-1])//2; m=m-m%5
    t=smalls[m].copy()
    for x in range(0,VW,100): cv2.line(t,(x//4,0),(x//4,480),(0,255,255) if x%500 else (0,0,255),1)
    cv2.putText(t,f"{i}: {a:.1f}-{b:.1f}",(5,30),0,0.8,(0,255,0),2)
    tiles.append(t)
    res.append(dict(i=i,a=round(a,2),b=round(b,2),sub_lo=lo,sub_hi=hi,xmin=max(0,hi-1080+15),xmax=min(VW-1080,lo-15),wide=[k for _,k in sorted(wf)[-3:]]))
rows=[np.hstack(tiles[j:j+6]+[np.zeros_like(tiles[0])]*(6-len(tiles[j:j+6]))) for j in range(0,len(tiles),6)]
cv2.imwrite(pref+"_shots.jpg",np.vstack(rows))
json.dump(dict(VW=VW,s=s,shots=res),open(pref+"_shots.json","w"),indent=1)
print("VW",VW,"center x",(VW-1080)//2); [print(r) for r in res]
