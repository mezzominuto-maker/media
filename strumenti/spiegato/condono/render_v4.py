import json, math, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FD="/home/claude/media/strumenti/fonts/"
NAVY=(13,18,33); NAVY2=(24,36,62); CREAM=(240,236,226); AMBER=(255,196,61); GOLD=(208,192,150)
GREY=(150,160,185); RED=(235,64,64); GREEN=(70,200,120)
SP=1.12
VEND=64.36
DUR=VEND/SP+2.6
BOUND=[3.6,7.8,13.45,16.7,29.0,33.2,38.7,43.8,50.2,55.1,64.85,67.8,72.2,76.1,79.1,81.35]
IMPACT=[0.35,1.7,6.2,8.3,10.7,16.9,20.9,25.4,31.4,40.6,48.0,51.1,60.3,65.2,66.3,76.2,79.15]
TINT={0:(60,48,18),3:(30,40,90),4:(60,48,18),6:(90,30,30),7:(90,30,30),9:(40,40,90),10:(110,25,25),11:(30,80,50),12:(110,25,25),13:(60,48,18),15:(60,48,18)}
_fc={}
def F(name,size):
    k=(name,size)
    if k not in _fc: _fc[k]=ImageFont.truetype(FD+name,size)
    return _fc[k]
BLK="InterDisplay-Black.otf"; XB="Inter-ExtraBold.otf"; BD="Inter-Bold.otf"; SB="Inter-SemiBold.otf"; MD="Inter-Medium.otf"
def cl(x): return max(0.0,min(1.0,x))
def eo(x): x=cl(x); return 1-(1-x)**3
def eb(x):  # ease out back
    x=cl(x); c=1.9; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def prog(t,t0,d=0.4): return cl((t-t0)/d)
# ---------- background ----------
yy=np.linspace(0,1,H)[:,None]; xx=np.linspace(0,1,W)[None,:]
base=np.zeros((H,W,3),np.float32)
for i in range(3): base[...,i]=NAVY[i]*(1-yy)+NAVY2[i]*yy*0.9+NAVY[i]*0*xx
vign=1-0.55*((xx-0.5)**2*1.2+(yy-0.5)**2)  
base*=vign[...,None]
rng=np.random.default_rng(3)
grains=[(rng.normal(0,6,(H//2,W//2))).repeat(2,0).repeat(2,1)[...,None].astype(np.float32) for _ in range(4)]
gx,gy=np.meshgrid(np.arange(W),np.arange(H))
per=90
stripe=((((gx+gy)//1)%per)<per*0.5).astype(np.float32)[...,None]*5.0
stripe=np.concatenate([stripe,stripe[:, :per]],axis=1)
def tint_at(t):
    idx=sum(1 for b in BOUND if b<=t); keys=sorted(TINT)
    k=max([x for x in keys if x<=idx]); return np.array(TINT[k],np.float32)
def background(t):
    cx=W*(0.5+0.35*math.sin(t*0.5)); cy=H*(0.42+0.2*math.cos(t*0.37))
    d=((gx-cx)**2+(gy-cy)**2)/(650**2)
    glow=np.exp(-d)[...,None]*tint_at(t)*0.9
    off=int(t*70)%per
    a=base+glow+stripe[:,off:off+W]+grains[int(t*12)%4]
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert("RGBA")
# ---------- b-roll v4: clip Pexels + foto ----------
CLIP="/home/claude/clip/"
# (inizio, fine) in tempo voce; tipo v=video p=foto None=solo grafica; file; secondo di partenza o fuoco x; fuoco
SHOTS=[
 (0.0,1.97,'v','px2239154.mp4',3.0,0.5),
 (1.97,3.97,'v','px8482299.mp4',2.0,0.5),
 (3.97,4.99,None),
 (4.99,8.6,'p','foto/montecitorio.jpg',0.5,0.4),
 (8.6,10.4,'p','foto/aula.jpg',0.5,0.5),
 (10.4,12.9,'v','px855388.mp4',1.0,0.5),
 (12.9,15.6,'v','px8482299.mp4',12.0,0.5),
 (15.6,16.8,'v','px10971670.mp4',20.0,0.42),
 (16.8,18.3,'v','px7817162.mp4',3.0,0.5),
 (18.3,21.2,'v','px15959642.mp4',1.0,0.5),
 (21.2,24.2,'v','px7816253.mp4',5.0,0.72),
 (24.2,27.3,'v','px15673263.mp4',1.0,0.55),
 (27.3,29.3,'v','px15261765.mp4',3.0,0.42),
 (29.3,31.4,'v','px5594431.mp4',2.0,0.62),
 (31.4,33.0,None),
 (33.0,36.5,'p',CLIP+'pxf17311028.jpg',0.5,0.6),
 (36.5,38.1,'v','px855672.mp4',12.0,0.5),
 (38.1,39.4,'p',CLIP+'pxf8325257.jpg',0.5,0.5),
 (39.4,41.0,'v','px8482299.mp4',16.0,0.5),
 (41.0,43.8,'v','px12315324.mp4',4.0,0.32),
 (43.8,47.7,None),
 (47.7,52.3,'p','foto/aula.jpg',0.5,0.5),
 (52.3,55.6,'p',CLIP+'pxf30305404.jpg',0.5,0.62),
 (55.6,59.2,'p',CLIP+'pxf2327065.jpg',0.45,0.5),
 (59.2,61.9,'p','foto/montecitorio.jpg',0.5,0.35),
 (61.9,999,None)]
BOUND=[s[0] for s in SHOTS[1:]]+[VEND]
IMPACT=[0.2,4.0,5.3,10.9,13.3,15.65,16.9,20.6,21.9,23.0,24.3,25.9,29.9,31.5,33.6,36.6,38.15,39.45,41.1,44.0,48.0,49.4,50.7,51.4,52.5,55.8,59.4,62.0]
TINT={i:(30,40,90) for i in range(len(BOUND)+2)}
TINT.update({2:(110,40,20),14:(110,40,20),20:(30,80,60),25:(110,40,20)})
GZ=1.12  # margine per lo zoom lento
def grade(a,k=0.66):
    g=a.mean(axis=2,keepdims=True); a=a*0.72+g*0.28
    return np.clip(a*k+np.array(NAVY,np.float32)*0.22,0,255).astype(np.uint8)
shade=np.zeros((H,W,1),np.float32)
for i,yv in enumerate(np.linspace(0,1,H)):
    shade[i]=0.18+0.55*max(0,1-yv/0.2)**1.5+0.8*max(0,(yv-0.64)/0.36)**1.2
shade=np.clip(shade,0,0.9)
shadeL=Image.fromarray(np.dstack([np.broadcast_to(np.array(NAVY,np.uint8),(H,W,3)),(shade*255).astype(np.uint8)]),"RGBA")
_ph={}
def photo_base(fn):
    if fn not in _ph:
        im=Image.open(fn).convert("RGB"); s=max(W*GZ*1.1/im.width,H*GZ*1.1/im.height)
        im=im.resize((int(im.width*s)+2,int(im.height*s)+2),Image.LANCZOS)
        _ph[fn]=Image.fromarray(grade(np.asarray(im).astype(np.float32),0.62))
    return _ph[fn]
class Reader:
    def __init__(s): s.key=None; s.p=None; s.next=None
    def get(s,fn,start,fx,i):
        if s.key!=(fn,start) or s.next!=i:
            if s.p: s.p.kill()
            ss=start+i/FPS
            ow,oh=int(W*GZ)//2*2,int(H*GZ)//2*2
            vf=f"fps={FPS},scale={ow}:{oh}:force_original_aspect_ratio=increase,crop={ow}:{oh}:(iw-{ow})*{fx}:(ih-{oh})/2"
            s.p=subprocess.Popen(["ffmpeg","-v","error","-ss",f"{ss:.3f}","-i",CLIP+fn,"-vf",vf,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
            s.key=(fn,start); s.dim=(ow,oh)
        ow,oh=s.dim; b=s.p.stdout.read(ow*oh*3); s.next=i+1
        if len(b)<ow*oh*3: return s.last
        s.last=np.frombuffer(b,np.uint8).reshape(oh,ow,3); return s.last
RD=Reader()
def broll(t,tr):
    for sh in SHOTS:
        if sh[0]-0.001<=t<sh[1]:
            if sh[2] is None: return None
            t0,t1=sh[0],sh[1]; u=cl((t-t0)/max(0.1,t1-t0))
            if sh[2]=='v':
                i=int(round((tr-t0/SP)*FPS))
                a=RD.get(sh[3],sh[4],sh[5],i)
                im=Image.fromarray(grade(a.astype(np.float32)))
                z=1+0.07*u; cw=im.width/z; ch=cw*H/W
            else:
                im=photo_base(sh[3]); z=1+0.14*u
                cw=W*GZ/z; ch=cw*H/W
            cx=(im.width-cw)*(sh[4] if sh[2]=='p' else 0.5); cy=(im.height-ch)*(sh[5] if sh[2]=='p' else 0.5)
            out=im.crop((int(cx),int(cy),int(cx+cw),int(cy+ch))).resize((W,H),Image.BILINEAR).convert("RGBA")
            out.alpha_composite(shadeL); return out
    return None
# ---------- text helpers ----------
_tc={}
def tlayer(text,font,size,color,stroke=0):
    k=(text,font,size,color,stroke)
    if k not in _tc:
        f=F(font,size); b=f.getbbox(text,stroke_width=stroke)
        im=Image.new("RGBA",(b[2]-b[0]+20,b[3]-b[1]+20),(0,0,0,0))
        ImageDraw.Draw(im).text((10-b[0],10-b[1]),text,font=f,fill=color,stroke_width=stroke,stroke_fill=(0,0,0,200) if stroke else None)
        _tc[k]=im
    return _tc[k]
def put(canvas,layer,cx,cy,scale=1.0,alpha=1.0,anchor="mm"):
    if alpha<=0.01 or scale<=0.01: return
    L=layer
    if abs(scale-1)>0.01: L=L.resize((max(1,int(L.width*scale)),max(1,int(L.height*scale))),Image.BICUBIC)
    if alpha<0.99:
        L=L.copy(); a=L.split()[3].point(lambda v:int(v*alpha)); L.putalpha(a)
    x=int(cx-L.width/2) if anchor[0]=="m" else (int(cx) if anchor[0]=="l" else int(cx-L.width))
    y=int(cy-L.height/2)
    canvas.alpha_composite(L,(max(0,x),max(0,y)) if x>=0 and y>=0 else (0,0)) if (x>=0 and y>=0) else canvas.paste(L,(x,y),L)
def text(c,s,font,size,color,cx,cy,t,t0,d=0.35,mode="pop",anchor="mm",out=None):
    p=prog(t,t0,d)
    if p<=0: return
    a=eo(p); sc=1.0; dy=0
    if mode=="pop": sc=0.6+0.4*eb(p)
    elif mode=="up": dy=(1-eo(p))*60
    elif mode=="zoom": sc=1.6-0.6*eo(p)
    if out is not None:
        q=prog(t,out,0.25); a*=1-q; sc*= 1+0.15*q
    put(c,tlayer(s,font,size,color),cx,cy+dy,sc,a,anchor)
def rrect(c,box,r,fill,t,t0,d=0.35,out=None):
    p=eo(prog(t,t0,d))
    if p<=0: return
    a=p
    if out is not None: a*=1-prog(t,out,0.25)
    x0,y0,x1,y1=box; cx=(x0+x1)/2
    w=(x1-x0)*(0.85+0.15*p)
    L=Image.new("RGBA",c.size,(0,0,0,0)); ImageDraw.Draw(L).rounded_rectangle([cx-w/2,y0,cx+w/2,y1],r,fill=fill[:3]+(int(fill[3]*a) if len(fill)>3 else int(255*a),))
    c.alpha_composite(L)
def stamp(c,s,color,cx,cy,t,t0,size=74,angle=-8,out=None):
    p=prog(t,t0,0.25)
    if p<=0: return
    a=1.0
    if out is not None: a=1-prog(t,out,0.25)
    f=F(BLK,size); b=f.getbbox(s); w=b[2]-b[0]+60; h=b[3]-b[1]+44
    L=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle([10,10,10+w,10+h],14,outline=color,width=8)
    d.text((10+w/2,10+h/2),s,font=f,fill=color,anchor="mm")
    L=L.rotate(angle,resample=Image.BICUBIC,expand=True)
    sc=2.2-1.2*eo(p)
    put(c,L,cx,cy,sc,a*eo(p))
class OV:
    def __init__(s,c): s.c=c; s.L=Image.new("RGBA",c.size,(0,0,0,0)); s.d=ImageDraw.Draw(s.L)
    def __enter__(s): return s.d
    def __exit__(s,*a): s.c.alpha_composite(s.L)
def fmt(n): return f"{int(n):,}".replace(",",".")
# ---------- captions ----------
words=json.load(open("v4/words.json"))
DISP={}
chunks=[]; cur=[]
for i,w in enumerate(words):
    cur.append(w); txt=" ".join(DISP.get(x["w"],x["w"]) for x in cur)
    nxt=words[i+1] if i+1<len(words) else None
    endp=w["w"][-1] in ".?,:" ; gap= nxt and nxt["s"]-w["e"]>0.12
    if len(cur)>=3 or len(txt)>16 or endp or gap or nxt is None:
        chunks.append(cur); cur=[]
def captions(c,t):
    for ch in chunks:
        if ch[0]["s"]-0.05<=t<ch[-1]["e"]+0.12:
            p=prog(t,ch[0]["s"]-0.05,0.14); sc=0.85+0.15*eb(p)
            parts=[DISP.get(x["w"],x["w"]).upper() for x in ch]
            f=F(BLK,76); sp=F(BLK,76).getlength(" ")
            ws=[f.getlength(s) for s in parts]; tot=sum(ws)+sp*(len(parts)-1)
            L=Image.new("RGBA",(int(tot)+60,140),(0,0,0,0)); d=ImageDraw.Draw(L); x=30
            for s,wd,wobj in zip(parts,ws,ch):
                act=wobj["s"]-0.03<=t<wobj["e"]+0.05
                if act:
                    d.rounded_rectangle([x-12,22,x+wd+12,120],16,fill=AMBER)
                    d.text((x,70),s,font=f,fill=NAVY,anchor="lm")
                else:
                    d.text((x,70),s,font=f,fill=CREAM,anchor="lm",stroke_width=5,stroke_fill=(0,0,0))
                x+=wd+sp
            if L.width>W-60: sc*= (W-60)/L.width
            put(c,L,W/2,1470,sc,1)
            return
# ---------- header / progress ----------
logo=Image.open("/home/claude/media/strumenti/logo_mark.png").convert("RGBA"); logo=logo.resize((int(logo.width*64/logo.height),64))
def header(c,t):
    c.alpha_composite(logo,(60,120))
    put(c,tlayer("MEZZO MINUTO",BLK,34,GOLD),118,152,anchor="lm")
    put(c,tlayer("IL CONTESTO",XB,26,AMBER),W-60,152,anchor="rm")
    with OV(c) as d:
        d.rectangle([0,0,W,10],fill=(255,255,255,40)); d.rectangle([0,0,int(W*min(1,t/VEND)),10],fill=AMBER)
def source(c,s,t,t0,t1):
    if t0<=t<t1: text(c,s,MD,26,GREY,W/2,1335,t,t0,0.4,"up",out=t1-0.25)
# ---------- elementi grafici v4 ----------
def cross(c,cx,cy,size,t,t0,col=RED,out=None):
    p=eo(prog(t,t0,0.2))
    if p<=0: return
    a=p*(1-prog(t,out,0.2) if out else 1)
    L=Image.new("RGBA",(size+40,size+40),(0,0,0,0)); d=ImageDraw.Draw(L); w=size//6
    d.line([(20,20),(20+size,20+size)],fill=col,width=w); d.line([(20+size,20),(20,20+size)],fill=col,width=w)
    put(c,L,cx,cy,1.8-0.8*p,a)
def check(c,cx,cy,size,t,t0,col=GREEN,out=None):
    p=eo(prog(t,t0,0.2))
    if p<=0: return
    a=p*(1-prog(t,out,0.2) if out else 1)
    L=Image.new("RGBA",(size+40,size+40),(0,0,0,0)); d=ImageDraw.Draw(L); w=size//6
    d.line([(20,20+size*0.55),(20+size*0.38,20+size*0.9),(20+size,20+size*0.1)],fill=col,width=w,joint="curve")
    put(c,L,cx,cy,1.8-0.8*p,a)
def card(c,y,label,t,t0,col,out=None,h=110,wd=860,font_size=50,icon=None):
    p=eo(prog(t,t0,0.25))
    if p<=0: return
    a=p*(1-prog(t,out,0.2) if out else 1)
    L=Image.new("RGBA",(wd+20,h+20),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle([10,10,10+wd,10+h],22,fill=(13,18,33,225),outline=col,width=5)
    x=50
    if icon=="check":
        d.line([(x,10+h*0.52),(x+20,10+h*0.72),(x+52,10+h*0.3)],fill=col,width=10,joint="curve"); x+=80
    d.text((x,10+h/2),label,font=F(BLK,font_size),fill=CREAM,anchor="lm")
    dx=(1-p)*-180
    put(c,L,W/2+dx,y,1,a)
def chip(c,y,label,t,t0,col,out=None,fs=64):
    p=prog(t,t0,0.22)
    if p<=0: return
    a=eo(p)*(1-prog(t,out,0.2) if out else 1)
    f=F(BLK,fs); tw=f.getlength(label)
    L=Image.new("RGBA",(int(tw)+100,130),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle([10,10,int(tw)+90,120],60,fill=col)
    d.text((int(tw)/2+50,66),label,font=f,fill=CREAM,anchor="mm")
    put(c,L,W/2,y,0.5+0.5*eb(p),a)
def scene(c,t):
    if t<1.97:
        text(c,"HAI COSTRUITO",BLK,104,CREAM,W/2,640,t,0.0,0.22,"up",out=1.9)
        text(c,"SENZA PERMESSO?",BLK,104,AMBER,W/2,770,t,0.6,0.22,"pop",out=1.9)
    elif t<3.97:
        text(c,"LO STATO",BLK,110,CREAM,W/2,640,t,1.97,0.22,"up",out=3.9)
        text(c,"POTREBBE",BLK,110,CREAM,W/2,770,t,2.3,0.22,"up",out=3.9)
        text(c,"PERDONARTI",BLK,130,AMBER,W/2,920,t,2.75,0.25,"zoom",out=3.9)
    elif t<4.99:
        text(c,"DI NUOVO.",BLK,170,AMBER,W/2,760,t,3.97,0.2,"zoom")
        stamp(c,"4° CONDONO",RED,W/2,1010,t,4.15,size=78,angle=-7)
    elif t<10.4:
        text(c,"FRATELLI D'ITALIA",XB,56,CREAM,W/2,560,t,5.0,0.3,"up",out=10.3)
        text(c,"RIAPRE IL",BLK,96,CREAM,W/2,690,t,5.3,0.25,"up",out=10.3)
        text(c,"CONDONO",BLK,150,AMBER,W/2,830,t,5.75,0.25,"zoom",out=10.3)
        text(c,"2003",BLK,190,CREAM,W/2,1010,t,6.9,0.25,"pop",out=10.3)
        chip(c,1200,"EMENDAMENTO ALLA MANOVRA",t,8.65,(170,120,20),out=10.3,fs=48)
        source(c,"Bozza di FdI anticipata da Repubblica, 17 novembre",t,5.2,10.3)
    elif t<15.6:
        text(c,"COS'È UN CONDONO",XB,58,CREAM,W/2,520,t,10.45,0.25,"up",out=15.5)
        text(c,"PAGHI",BLK,150,AMBER,W/2,700,t,11.4,0.25,"zoom",out=12.85)
        text(c,"€",BLK,200,CREAM,W/2,900,t,11.6,0.25,"pop",out=12.85)
        text(c,"COSTRUITA",BLK,110,CREAM,W/2,700,t,13.1,0.25,"up",out=15.5)
        text(c,"SENZA PERMESSI",BLK,96,CREAM,W/2,830,t,13.5,0.25,"up",out=15.5)
        stamp(c,"ABUSIVA",RED,W/2,1030,t,14.3,size=96,angle=-8,out=15.5)
        text(c,"→ IN REGOLA",BLK,90,GREEN,W/2,1210,t,14.8,0.25,"pop",out=15.5)
    elif t<16.8:
        cross(c,W/2,720,300,t,15.65)
        text(c,"NIENTE",BLK,110,CREAM,W/2,1000,t,15.7,0.2,"up")
        text(c,"DEMOLIZIONE",BLK,110,RED,W/2,1120,t,15.85,0.2,"pop")
    elif t<18.3:
        check(c,W/2,720,280,t,16.85)
        text(c,"LA CASA",BLK,110,CREAM,W/2,1000,t,16.9,0.2,"up")
        text(c,"SI PUÒ VENDERE",BLK,96,GREEN,W/2,1120,t,17.3,0.2,"pop")
    elif t<24.2:
        text(c,"GIÀ",BLK,90,CREAM,W/2,470,t,18.35,0.22,"up",out=24.1)
        text(c,"3 CONDONI",BLK,140,AMBER,W/2,600,t,18.6,0.25,"zoom",out=24.1)
        for k,(yr,t0,lab) in enumerate([("1985",20.55,"governo Craxi"),("1994",21.85,"Berlusconi I"),("2003",22.95,"Berlusconi II")]):
            y=800+k*165
            rrect(c,(150,y-70,930,y+70),24,(13,18,33,210),t,t0,0.25,out=24.1)
            text(c,yr,BLK,104,AMBER if k==2 else CREAM,330,y,t,t0,0.25,"pop",out=24.1)
            text(c,lab,SB,46,GREY,640,y,t,t0+0.12,0.25,"up",out=24.1)
    elif t<27.3:
        text(c,"MA IN",XB,64,CREAM,W/2,520,t,24.25,0.22,"up",out=27.2)
        text(c,"CAMPANIA",BLK,160,AMBER,W/2,660,t,24.45,0.25,"zoom",out=27.2)
        text(c,"il condono 2003",SB,58,CREAM,W/2,820,t,24.9,0.25,"up",out=27.2)
        stamp(c,"MAI APPLICATO",RED,W/2,1010,t,25.9,size=80,angle=-6,out=27.2)
    elif t<31.4:
        p=cl((t-28.3)/1.6); n=int(50000*(1-(1-p)**3))
        if t>=27.5:
            text(c,"OGGI RESTANO",XB,60,CREAM,W/2,560,t,27.45,0.25,"up",out=31.3)
            put(c,tlayer(fmt(n),BLK,210,AMBER),W/2,760,1.0+0.08*(1-prog(t,29.9,0.3)) if t>29.9 else 1.0,eo(prog(t,28.2,0.2))*(1-prog(t,31.3,0.2)))
            text(c,"ORDINI DI",BLK,92,CREAM,W/2,960,t,29.6,0.25,"up",out=31.3)
            text(c,"DEMOLIZIONE",BLK,110,RED,W/2,1080,t,29.9,0.25,"pop",out=31.3)
        source(c,"Stima della deputata FdI Imma Vietri",t,28.4,31.3)
    elif t<33.0:
        text(c,"LA BOZZA",BLK,130,CREAM,W/2,700,t,31.45,0.22,"up")
        text(c,"VA OLTRE",BLK,170,AMBER,W/2,880,t,31.95,0.25,"zoom")
    elif t<41.0:
        if t<36.5:
            text(c,"IN TUTTA",BLK,110,CREAM,W/2,560,t,33.1,0.22,"up",out=36.4)
            text(c,"ITALIA",BLK,170,AMBER,W/2,720,t,33.4,0.25,"zoom",out=36.4)
            text(c,"si potrebbero sanare",SB,56,CREAM,W/2,890,t,34.0,0.25,"up",out=36.4)
            text(c,"PICCOLE IRREGOLARITÀ",BLK,78,AMBER,W/2,1000,t,35.0,0.25,"pop",out=36.4)
        else:
            text(c,"PICCOLE IRREGOLARITÀ",BLK,66,AMBER,W/2,470,t,36.5,0.2,"up",out=40.9)
            card(c,620,"MURO INTERNO SPOSTATO",t,36.6,AMBER,out=40.9,icon="check",font_size=46)
            card(c,770,"SECONDO BAGNO",t,38.15,AMBER,out=40.9,icon="check")
            card(c,920,"FINESTRE DIVERSE",t,39.45,AMBER,out=40.9,icon="check")
            source(c,"Bozza di emendamento FdI · fonte: Il Politico",t,36.7,40.9)
    elif t<43.8:
        text(c,"RESTANO",BLK,100,CREAM,W/2,560,t,41.05,0.22,"up",out=43.7)
        stamp(c,"ESCLUSE",RED,W/2,740,t,41.1,size=120,angle=-6,out=43.7)
        text(c,"le zone dove",SB,58,CREAM,W/2,930,t,41.9,0.25,"up",out=43.7)
        text(c,"NON SI PUÒ COSTRUIRE",BLK,74,AMBER,W/2,1030,t,42.3,0.25,"pop",out=43.7)
    elif t<47.7:
        text(c,"OGNI REGIONE",BLK,96,CREAM,W/2,520,t,43.95,0.22,"up",out=47.6)
        n=int(60*eo(cl((t-44.0)/1.4)))
        if t>=43.95: put(c,tlayer(str(n),BLK,360,AMBER),W/2,780,1.0,eo(prog(t,43.95,0.2))*(1-prog(t,47.6,0.2)))
        text(c,"GIORNI",BLK,110,CREAM,W/2,1000,t,44.5,0.25,"up",out=47.6)
        text(c,"per decidere se applicarlo",SB,52,CREAM,W/2,1120,t,45.6,0.25,"up",out=47.6)
    elif t<52.3:
        text(c,"CONTRARI",BLK,140,RED,W/2,520,t,47.8,0.25,"zoom",out=52.2)
        chip(c,700,"LEGA",t,48.0,(60,70,100),out=52.2)
        chip(c,830,"PD",t,49.4,(60,70,100),out=52.2)
        chip(c,960,"AVS",t,50.7,(60,70,100),out=52.2)
        chip(c,1090,"LEGAMBIENTE",t,51.35,(60,70,100),out=52.2)
    elif t<55.6:
        rrect(c,(90,560,990,1150),36,(20,90,55,215),t,52.4,0.3,out=55.5)
        text(c,"A FAVORE",BLK,96,CREAM,W/2,660,t,52.5,0.25,"pop",out=55.5)
        text(c,"si chiude",SB,62,CREAM,W/2,820,t,53.3,0.25,"up",out=55.5)
        text(c,"UN'INGIUSTIZIA",BLK,82,AMBER,W/2,920,t,53.6,0.25,"pop",out=55.5)
        text(c,"verso la Campania",SB,62,CREAM,W/2,1040,t,54.4,0.25,"up",out=55.5)
    elif t<59.2:
        rrect(c,(90,560,990,1150),36,(120,30,35,215),t,55.7,0.3,out=59.1)
        text(c,"CONTRO",BLK,96,CREAM,W/2,660,t,55.8,0.25,"pop",out=59.1)
        text(c,"si premia ancora",SB,62,CREAM,W/2,820,t,56.6,0.25,"up",out=59.1)
        text(c,"CHI HA VIOLATO",BLK,82,AMBER,W/2,920,t,57.4,0.25,"pop",out=59.1)
        text(c,"LE REGOLE",BLK,82,AMBER,W/2,1030,t,58.1,0.25,"pop",out=59.1)
    elif t<61.9:
        text(c,"SI DECIDE A",XB,64,CREAM,W/2,560,t,59.4,0.22,"up",out=61.8)
        text(c,"DICEMBRE",BLK,160,AMBER,W/2,720,t,59.7,0.25,"zoom",out=61.8)
        text(c,"commissione Bilancio",SB,58,CREAM,W/2,880,t,60.6,0.25,"up",out=61.8)
    elif t<VEND:
        text(c,"TU COSA",BLK,130,CREAM,W/2,600,t,62.0,0.22,"pop")
        text(c,"NE PENSI?",BLK,130,AMBER,W/2,750,t,62.35,0.22,"pop")
        text(c,"SCRIVILO NEI COMMENTI",XB,54,CREAM,W/2,960,t,63.2,0.3,"up")
        p=prog(t,63.4,0.3)
        if p>0:
            yb=1060+12*math.sin(t*9); a=int(255*eo(p))
            with OV(c) as d: d.polygon([(W/2-50,yb),(W/2+50,yb),(W/2,yb+60)],fill=AMBER+(a,))
    else:
        p=eo(prog(t,VEND,0.4))
        L=logo.resize((int(logo.width*3),192)); put(c,L,W/2,640,0.8+0.2*p,p)
        text(c,"MEZZO MINUTO",BLK,96,GOLD,W/2,820,t,VEND+0.15,0.35,"up")
        text(c,"Il Contesto · Capire le notizie",SB,46,CREAM,W/2,920,t,VEND+0.4,0.35,"up")
        text(c,"SEGUI LA PAGINA",BLK,64,AMBER,W/2,1080,t,VEND+0.8,0.3,"pop")
        text(c,"Fonti: ANSA · Il Sole 24 Ore · QN · Il Politico",MD,28,GREY,W/2,1250,t,VEND+1.0,0.4,"up")
        text(c,"Video e foto: Pexels · Wikimedia Commons (crediti in descrizione)",MD,26,GREY,W/2,1300,t,VEND+1.1,0.4,"up")
def frame(tr):
    t=tr*SP if tr*SP<VEND else VEND+(tr-VEND/SP)
    c=background(t)
    br=broll(t,tr)
    if br is not None:
        sh=[s for s in SHOTS if s[0]-0.001<=t<s[1]][0]; a=eo(prog(t,sh[0],0.12))
        c=Image.blend(c,br,a) if a<0.99 else br
    L=Image.new("RGBA",(W,H),(0,0,0,0)); scene(L,t)
    b=max([0]+[x for x in BOUND if x<=t]); dt=t-b
    z=1+0.04*min(1,dt/3.0); ox=oy=0
    if b>0 and dt<0.22: oy=int((1-eo(dt/0.22))*200)
    for i in IMPACT:
        if 0<=t-i<0.28:
            k=1-(t-i)/0.28; r=np.random.default_rng(int(t*100)); ox+=int(r.uniform(-1,1)*18*k); oy+=int(r.uniform(-1,1)*18*k); z+=0.07*k
    if b>0 and dt<0.1: L=L.filter(ImageFilter.BoxBlur(int(10*(1-dt/0.1))+1))
    if abs(z-1)>0.002:
        nw,nh=int(W*z),int(H*z); L=L.resize((nw,nh),Image.BILINEAR); L=L.crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
    c.alpha_composite(L,(0,0)) if ox==0 and oy==0 else c.paste(L,(ox,oy),L)
    if b>0 and dt<0.07: c.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,int(90*(1-dt/0.07)))))
    header(c,t)
    if t<VEND: captions(c,t)
    return c.convert("RGB")
# ---------- effetti sonori ----------
def sfx(out):
    sr=48000; n=int((DUR+0.5)*sr); a=np.zeros(n,np.float32); rng=np.random.default_rng(1)
    def add(tr,x,g):
        i=int(tr*sr); j=min(n,i+len(x)); a[i:j]+=x[:j-i]*g
    def whoosh(d=0.32):
        m=int(d*sr); nz=rng.normal(0,1,m).astype(np.float32); env=np.sin(np.linspace(0,np.pi,m))**2
        k=np.linspace(0.02,0.25,m); y=np.zeros(m,np.float32); s=0.0
        for i in range(m): s+=k[i]*(nz[i]-s); y[i]=s
        return y*env*3
    def hit(d=0.5):
        m=int(d*sr); tt=np.arange(m)/sr; f=55*np.exp(-tt*4)+40
        return (np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt*7)*1.0+rng.normal(0,1,m)*np.exp(-tt*40)*0.35).astype(np.float32)
    def tick():
        m=int(0.03*sr); tt=np.arange(m)/sr; return (np.sin(2*np.pi*1800*tt)*np.exp(-tt*200)).astype(np.float32)
    def riser(d=1.0):
        m=int(d*sr); tt=np.arange(m)/sr; nz=rng.normal(0,1,m).astype(np.float32)
        return (nz*(tt/d)**2*0.25+np.sin(2*np.pi*(200+600*tt/d)*tt)*(tt/d)**2*0.15).astype(np.float32)
    W_=whoosh(); Hh=hit(); Tk=tick()
    for b in BOUND[:-1]: add(b/SP-0.12,W_,0.16)
    for i in IMPACT: add(i/SP,Hh,0.32)
    add(3.97/SP-1.0,riser(1.0),0.5); add(28.3/SP-0.9,riser(0.9),0.4)
    for k in range(14): add((28.3+k*1.6/14)/SP,Tk,0.12)
    for k in range(10): add((44.0+k*1.4/10)/SP,Tk,0.12)
    add(VEND/SP,Hh,0.35)
    a=np.clip(a,-1,1); import wave
    with wave.open(out,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a*32767).astype(np.int16).tobytes())
if __name__=="__main__":
    if sys.argv[1]=="still":
        os.makedirs("r4",exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)/SP).save(f"r4/f_{ts}.png")
    elif sys.argv[1]=="sfx": sfx(sys.argv[2])
    else:
        i0,i1,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",out+".tmp.mp4"],stdin=subprocess.PIPE)
        for i in range(i0,i1): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); assert p.wait()==0; os.rename(out+".tmp.mp4",out)
