import json, math, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FD="/home/claude/media/strumenti/fonts/"
NAVY=(13,18,33); NAVY2=(24,36,62); CREAM=(240,236,226); AMBER=(255,196,61); GOLD=(208,192,150)
GREY=(150,160,185); RED=(235,64,64); GREEN=(70,200,120)
SP=1.12
words=json.load(open("words.json"))
def S(i): return words[i]["s"]   # inizio della parola i (tempo voce)
def E(i): return words[i]["e"]
VEND=words[-1]["e"]+0.35
DUR=VEND/SP+2.6
BOZZA=not os.path.exists("voce.mp3")   # senza voce: scritta «bozza» in basso
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
# ---------- b-roll: clip Pexels + foto Commons ----------
CLIP="/tmp/claude-0/clips/"
FOTO="../condono/foto/"
SHOTS=[
 (0.0,S(6),'v','px9807882.mp4',1.0,0.5),
 (S(6),S(14),'v','px4186966.mp4',1.0,0.5),
 (S(14),S(24),None),
 (S(24),S(33),'v','px7608129.mp4',1.0,0.5),
 (S(33),S(41),'v','px4694592.mp4',2.0,0.5),
 (S(41),S(43),None),
 (S(43),S(54),'v','px9807886.mp4',1.0,0.5),
 (S(54),S(65),None),
 (S(65),S(75),'v','px3994170.mp4',0.5,0.5),
 (S(75),S(85),'v','px7821854.mp4',1.0,0.5),
 (S(85),S(93),'v','px855388.mp4',1.0,0.5),
 (S(93),S(107),'v','px6780089.mp4',1.0,0.5),
 (S(107),S(117),'v','px5981723.mp4',1.0,0.5),
 (S(117),S(125),'v','px5617895.mp4',1.0,0.5),
 (S(125),S(136),None),
 (S(136),S(143),'v','px7607575.mp4',3.0,0.5),
 (S(143),S(153),'v','px5354227.mp4',1.0,0.5),
 (S(153),S(163),None),
 (S(163),S(168),'p',FOTO+'montecitorio.jpg',0.5,0.3),
 (S(168),S(172),'p',FOTO+'aula.jpg',0.5,0.5),
 (S(172),999,None)]
BOUND=[s[0] for s in SHOTS[1:]]+[VEND]
IMPACT=[S(3),S(10),S(20)+0.6,S(27),S(38),S(41),S(47),S(59),S(64),S(71),S(84),S(90),S(99),S(119),S(126),S(131),S(140),S(149),S(159),S(166)]
TINT={i:(30,40,90) for i in range(len(BOUND)+2)}
TINT.update({2:(60,48,18),4:(110,25,25),5:(60,48,18),7:(60,48,18),11:(20,80,45),12:(110,25,25),13:(110,25,25),14:(60,48,18),17:(60,48,18)})
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
def fmt(n): return str(int(n)) if 1900<=int(n)<=2100 else f"{int(n):,}".replace(",",".")
# ---------- captions ----------

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
NEU=(60,70,100)
def counter(c,v0,v1,t,t0,d,cy,size,col,out,suffix=""):
    if t<t0: return
    p=eo(cl((t-t0)/d)); n=int(round(v0+(v1-v0)*p))
    sc=1.0+0.08*(1-prog(t,t0+d,0.3)) if t>t0+d else 1.0
    put(c,tlayer(f"{fmt(n)}{suffix}",BLK,size,col),W/2,cy,sc,eo(prog(t,t0,0.2))*(1-prog(t,out,0.2)))
def bar(c,y,frac,t,t0,d,out,label,inner="METÀ"):
    p=eo(prog(t,t0,d))
    if p<=0: return
    a=1-prog(t,out,0.2)
    with OV(c) as dr:
        x0,x1=110,970
        dr.rounded_rectangle([x0,y-45,x1,y+45],26,fill=(255,255,255,int(50*a)))
        xe=x0+(x1-x0)*frac*p
        if xe>x0+30: dr.rounded_rectangle([x0,y-45,xe,y+45],26,fill=AMBER+(int(255*a),))
    put(c,tlayer(inner,BLK,44,NAVY),x0+30,y,1,a*cl(p*1.5-0.3),anchor="lm")
    put(c,tlayer(label,BLK,56,CREAM),W/2,y+110,1,a*cl(p*1.5-0.3))
def arrow(c,cy,t,t0,out=None):
    p=eo(prog(t,t0,0.25))
    if p<=0: return
    a=p*(1-prog(t,out,0.2) if out else 1)
    L=Image.new("RGBA",(140,140),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.polygon([(45,10),(95,10),(95,70),(130,70),(70,130),(10,70),(45,70)],fill=AMBER)
    put(c,L,W/2,cy-30*(1-p),1,a)
def days(c,y,t,t0,tnew,out):
    p=prog(t,t0,0.25)
    if p<=0: return
    a=eo(p)*(1-prog(t,out,0.2))
    D=["LUN","MAR","MER","GIO","VEN","SAB","DOM"]; on={1,3,4,5}
    for k,d in enumerate(D):
        x=W/2+(k-3)*140; pk=eo(prog(t,t0+k*0.06,0.2))
        isnew=(k==2 and t>=tnew)
        col=AMBER if isnew else ((60,70,100) if k in on else (35,42,62))
        L=Image.new("RGBA",(140,150),(0,0,0,0)); dr=ImageDraw.Draw(L)
        dr.rounded_rectangle([8,8,132,142],22,fill=col+(235,))
        dr.text((70,52),d,font=F(BLK,36),fill=NAVY if isnew else CREAM,anchor="mm")
        if k in on or isnew:
            dr.ellipse([45,85,95,135],fill=NAVY if isnew else AMBER)
        sc=1.0+(0.35*(1-eo(prog(t,tnew,0.3))) if isnew else 0)
        put(c,L,x,y+(1-pk)*60,sc,a*pk)
def upbar(c,x,y,label,t,t0,out,col=AMBER):
    p=eo(prog(t,t0,0.3))
    if p<=0: return
    a=p*(1-prog(t,out,0.2))
    L=Image.new("RGBA",(420,330),(0,0,0,0)); dr=ImageDraw.Draw(L)
    dr.polygon([(210,10),(330,130),(260,130),(260,230),(160,230),(160,130),(90,130)],fill=col)
    dr.text((210,290),label,font=F(BLK,52),fill=CREAM,anchor="mm")
    put(c,L,x,y+(1-p)*80,1,a)
def scene(c,t):
    if t<S(6):
        o=S(6)-0.08
        text(c,"PIÙ GIOCHI,",BLK,140,CREAM,W/2,640,t,0.0,0.22,"up",out=o)
        text(c,"PIÙ INCASSA",BLK,130,AMBER,W/2,820,t,S(2),0.22,"zoom",out=o)
        text(c,"LO STATO?",BLK,150,CREAM,W/2,990,t,S(4),0.22,"up",out=o)
    elif t<S(14):
        o=S(14)-0.08
        text(c,"LA MANOVRA",BLK,120,CREAM,W/2,620,t,S(6),0.22,"up",out=o)
        text(c,"CAMBIA LE REGOLE",BLK,86,AMBER,W/2,780,t,S(8),0.25,"zoom",out=o)
        text(c,"DEL GIOCO D'AZZARDO",XB,64,CREAM,W/2,920,t,S(11),0.25,"up",out=o)
        source(c,"Ddl di bilancio 2027",t,S(6)+0.3,o)
    elif t<S(24):
        o=S(24)-0.08
        text(c,"NEL 2025",BLK,110,CREAM,W/2,520,t,S(14),0.22,"up",out=o)
        text(c,"GLI ITALIANI HANNO GIOCATO",XB,54,CREAM,W/2,660,t,S(16),0.25,"up",out=o)
        counter(c,0,165,t,S(20)-0.3,0.9,860,300,AMBER,o)
        text(c,"MILIARDI DI EURO",BLK,96,CREAM,W/2,1070,t,S(21),0.25,"pop",out=o)
        source(c,"Raccolta 2025: 165,3 miliardi · ADM, bilancio d'esercizio",t,S(20),o)
    elif t<S(33):
        o=S(33)-0.08
        text(c,"IL DATO UFFICIALE",BLK,84,CREAM,W/2,560,t,S(24),0.22,"up",out=o)
        card(c,760,"AGENZIA DELLE DOGANE",t,S(27),AMBER,out=o,font_size=56,icon="check")
        card(c,900,"E DEI MONOPOLI",t,S(29),AMBER,out=o,font_size=56)
        source(c,"ADM · Relazione sui giochi pubblici alla Camera",t,S(24)+0.3,o)
    elif t<S(41):
        o=S(41)-0.08
        text(c,"TOLTE LE VINCITE",XB,66,CREAM,W/2,520,t,S(33),0.22,"up",out=o)
        text(c,"PERSI QUASI",BLK,110,CREAM,W/2,680,t,S(36),0.25,"up",out=o)
        counter(c,0,22,t,S(39)-0.2,0.6,880,300,RED,o)
        text(c,"MILIARDI",BLK,110,CREAM,W/2,1080,t,S(40),0.25,"pop",out=o)
        source(c,"Spesa 2025: 21,8 miliardi (giocato meno vinto) · ADM",t,S(37),o)
    elif t<S(43):
        text(c,"COSA",BLK,170,CREAM,W/2,700,t,S(41),0.2,"up")
        text(c,"CAMBIA?",BLK,190,AMBER,W/2,900,t,S(41)+0.15,0.22,"zoom")
    elif t<S(54):
        o=S(54)-0.08
        text(c,"1",BLK,90,AMBER,W/2,470,t,S(43),0.2,"pop",out=o)
        text(c,"PRELIEVO DELLO STATO",XB,64,CREAM,W/2,600,t,S(46),0.25,"up",out=o)
        upbar(c,W/2,830,"PIÙ ALTO",t,S(45),o)
        text(c,"SLOT E VIDEOLOTTERY",BLK,72,AMBER,W/2,1120,t,S(51),0.25,"up",out=o)
        source(c,"Agipronews, PressGiochi · proposta, non ancora approvata",t,S(43)+0.3,o)
    elif t<S(65):
        o=S(65)-0.08
        text(c,"2",BLK,90,AMBER,W/2,470,t,S(54),0.2,"pop",out=o)
        text(c,"LOTTO E SUPERENALOTTO",BLK,70,CREAM,W/2,600,t,S(54),0.25,"up",out=o)
        text(c,"QUINTA ESTRAZIONE",BLK,90,AMBER,W/2,740,t,S(59),0.25,"zoom",out=o)
        days(c,940,t,S(58),S(63),o)
        text(c,"IL MERCOLEDÌ",BLK,96,CREAM,W/2,1150,t,S(63),0.25,"pop",out=o)
        source(c,"Fortune Italia, Il Mattino, Gioconews",t,S(54)+0.3,o)
    elif t<S(75):
        o=S(75)-0.08
        text(c,"3",BLK,90,AMBER,W/2,470,t,S(65),0.2,"pop",out=o)
        text(c,"SLOT DA BAR",BLK,110,CREAM,W/2,610,t,S(65),0.25,"up",out=o)
        upbar(c,W/2-210,980,"PUNTATA",t,S(71),o)
        upbar(c,W/2+210,980,"VINCITA",t,S(74),o)
        source(c,"Agipronews, Irpiniaoggi · importi non ancora definiti",t,S(65)+0.3,o)
    elif t<S(85):
        o=S(85)-0.08
        text(c,"4",BLK,90,AMBER,W/2,470,t,S(75),0.2,"pop",out=o)
        text(c,"CONCESSIONI DEL GIOCO",XB,64,CREAM,W/2,610,t,S(77),0.25,"up",out=o)
        text(c,"PROROGATE",BLK,120,AMBER,W/2,770,t,S(81),0.25,"zoom",out=o)
        text(c,"FINO AL",XB,64,CREAM,W/2,920,t,S(82),0.25,"up",out=o)
        counter(c,2026,2029,t,S(83),0.5,1070,200,AMBER,o)
        source(c,"Agipronews, Casinos.com",t,S(75)+0.3,o)
    elif t<S(93):
        o=S(93)-0.08
        text(c,"SOLDI CHE SERVONO",BLK,84,CREAM,W/2,640,t,S(85),0.22,"up",out=o)
        text(c,"A FINANZIARE",BLK,110,CREAM,W/2,790,t,S(88),0.25,"up",out=o)
        text(c,"LA MANOVRA",BLK,130,AMBER,W/2,950,t,S(91),0.25,"zoom",out=o)
    elif t<S(107):
        o=S(107)-0.08
        rrect(c,(90,520,990,1200),36,(20,90,55,215),t,S(93),0.3,out=o)
        text(c,"A FAVORE",BLK,96,CREAM,W/2,620,t,S(93)+0.1,0.25,"pop",out=o)
        text(c,"ENTRATE",BLK,130,CREAM,W/2,790,t,S(98),0.25,"up",out=o)
        text(c,"SICURE",BLK,150,AMBER,W/2,950,t,S(99),0.25,"zoom",out=o)
        text(c,"da un settore che muove tantissimi soldi",SB,44,CREAM,W/2,1110,t,S(101),0.25,"up",out=o)
    elif t<S(117):
        o=S(117)-0.08
        rrect(c,(90,520,990,1200),36,(120,30,35,215),t,S(107),0.3,out=o)
        text(c,"CONTRO",BLK,96,CREAM,W/2,620,t,S(107)+0.1,0.25,"pop",out=o)
        chip(c,820,"CARITAS",t,S(112),NEU,out=o,fs=64)
        chip(c,980,"ASSOCIAZIONI DELLE FAMIGLIE",t,S(114),NEU,out=o,fs=48)
    elif t<S(125):
        o=S(125)-0.08
        rrect(c,(90,560,990,1160),36,(120,30,35,215),t,S(117),0.3,out=o)
        text(c,"LO STATO SPINGE",BLK,88,CREAM,W/2,690,t,S(117),0.25,"up",out=o)
        text(c,"A GIOCARE",BLK,130,AMBER,W/2,850,t,S(120),0.25,"zoom",out=o)
        text(c,"PER FARE CASSA",BLK,88,CREAM,W/2,1010,t,S(122),0.25,"up",out=o)
        source(c,"Caritas e Forum delle associazioni familiari · Jamma, Agimeg",t,S(117)+0.3,o)
    elif t<S(136):
        o=S(136)-0.08
        chip(c,560,"CORTE DEI CONTI",t,S(125),NEU,out=o,fs=64)
        text(c,"DUBBI",BLK,190,AMBER,W/2,780,t,S(131),0.25,"zoom",out=o)
        text(c,"SULLE STIME",BLK,100,CREAM,W/2,960,t,S(132),0.25,"up",out=o)
        text(c,"DEGLI INCASSI",BLK,100,CREAM,W/2,1080,t,S(134),0.25,"up",out=o)
        source(c,"Audizione sulla manovra, novembre · Jamma, Agimeg",t,S(125)+0.3,o)
    elif t<S(143):
        o=S(143)-0.08
        chip(c,560,"PARTITO DEMOCRATICO",t,S(136),NEU,out=o,fs=58)
        text(c,"FERMARE",BLK,150,AMBER,W/2,780,t,S(140),0.25,"zoom",out=o)
        text(c,"L'AUMENTO DELL'OFFERTA",BLK,70,CREAM,W/2,950,t,S(141),0.25,"up",out=o)
        source(c,"Emendamenti Pd · Agimeg, Jamma",t,S(136)+0.3,o)
    elif t<S(153):
        o=S(153)-0.08
        chip(c,520,"LEGA",t,S(143),NEU,out=o,fs=58)
        chip(c,660,"FORZA ITALIA",t,S(145),NEU,out=o,fs=58)
        text(c,"RINVIARE",BLK,140,AMBER,W/2,880,t,S(149),0.25,"zoom",out=o)
        text(c,"L'AUMENTO DEL PRELIEVO",BLK,70,CREAM,W/2,1050,t,S(150),0.25,"up",out=o)
        source(c,"Emendamenti Lega e FI · Agipronews, Agimeg",t,S(143)+0.3,o)
    elif t<S(163):
        o=S(163)-0.08
        text(c,"SALE GIOCHI",BLK,120,CREAM,W/2,560,t,S(153),0.22,"up",out=o)
        stamp(c,"CHIUSE",RED,W/2,760,t,S(155),size=120,angle=-6,out=o)
        counter(c,0,7,t,S(159)-0.1,0.4,980,240,AMBER,o)
        text(c,"ORE DI NOTTE",BLK,96,CREAM,W/2,1170,t,S(160),0.25,"up",out=o)
    elif t<S(172):
        o=S(172)-0.08
        text(c,"SI DECIDE A",XB,70,CREAM,W/2,560,t,S(163),0.22,"up",out=o)
        text(c,"DICEMBRE",BLK,170,AMBER,W/2,730,t,S(166),0.25,"zoom",out=o)
        chip(c,950,"COMMISSIONE BILANCIO · CAMERA",t,S(168),NEU,out=o,fs=44)
        source(c,"Voto sugli emendamenti dopo l'8 dicembre",t,S(163)+0.3,o)
    elif t<VEND:
        text(c,"TU COSA",BLK,130,CREAM,W/2,600,t,S(172),0.22,"pop")
        text(c,"NE PENSI?",BLK,130,AMBER,W/2,750,t,S(174),0.22,"pop")
        text(c,"SCRIVILO NEI COMMENTI",XB,54,CREAM,W/2,960,t,S(176),0.3,"up")
        p=prog(t,S(176)+0.2,0.3)
        if p>0:
            yb=1060+12*math.sin(t*9); a=int(255*eo(p))
            with OV(c) as d: d.polygon([(W/2-50,yb),(W/2+50,yb),(W/2,yb+60)],fill=AMBER+(a,))
    else:
        p=eo(prog(t,VEND,0.4))
        L=logo.resize((int(logo.width*3),192)); put(c,L,W/2,640,0.8+0.2*p,p)
        text(c,"MEZZO MINUTO",BLK,96,GOLD,W/2,820,t,VEND+0.15,0.35,"up")
        text(c,"Il Contesto · Capire le notizie",SB,46,CREAM,W/2,920,t,VEND+0.4,0.35,"up")
        text(c,"SEGUI LA PAGINA",BLK,64,AMBER,W/2,1080,t,VEND+0.8,0.3,"pop")
        text(c,"Fonti: ADM · ANSA · Sole 24 Ore · Agipronews · Agimeg · Jamma",MD,28,GREY,W/2,1250,t,VEND+1.0,0.4,"up")
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
    if BOZZA: put(c,tlayer("BOZZA · TEMPI STIMATI, VOCE DA AGGIUNGERE",XB,30,(255,120,120)),W/2,1840)
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
    add(S(20)/SP-1.0,riser(1.0),0.5); add(S(39)/SP-0.9,riser(0.9),0.4); add(S(41)/SP-0.8,riser(0.8),0.35); add(S(155)/SP-0.9,riser(0.9),0.4)
    for t0,d in [(S(20)-0.3,0.9),(S(39)-0.2,0.6),(S(83),0.5),(S(159)-0.1,0.4)]:
        for k in range(10): add((t0+k*d/10)/SP,Tk,0.12)
    add(VEND/SP,Hh,0.35)
    a=np.clip(a,-1,1); import wave
    with wave.open(out,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a*32767).astype(np.int16).tobytes())
if __name__=="__main__":
    if sys.argv[1]=="still":
        os.makedirs("r",exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)/SP).save(f"r/f_{ts}.png")
    elif sys.argv[1]=="sfx": sfx(sys.argv[2])
    else:
        i0,i1,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",out+".tmp.mp4"],stdin=subprocess.PIPE)
        for i in range(i0,i1): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); assert p.wait()==0; os.rename(out+".tmp.mp4",out)
