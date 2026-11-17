import json, math, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FD="/home/claude/media/strumenti/fonts/"
NAVY=(13,18,33); NAVY2=(24,36,62); CREAM=(240,236,226); AMBER=(255,196,61); GOLD=(208,192,150)
GREY=(150,160,185); RED=(235,64,64); GREEN=(70,200,120)
SP=1.12
DUR=81.35/SP+2.7
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
words=json.load(open("words.json"))
DISP={"quindici":"15","seicentocinquantamila.":"650.000.","cinquantamila":"50.000","quarant'anni?":"40 ANNI?","vent'anni.":"20 ANNI.","quattro":"4"}
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
    put(c,tlayer("UN MINUTO E MEZZO",XB,26,AMBER),W-60,152,anchor="rm")
    with OV(c) as d:
        d.rectangle([0,0,W,10],fill=(255,255,255,40)); d.rectangle([0,0,int(W*min(1,t/81.3)),10],fill=AMBER)
def source(c,s,t,t0,t1):
    if t0<=t<t1: text(c,s,MD,26,GREY,W/2,1335,t,t0,0.4,"up",out=t1-0.25)
# ---------- house icon ----------
def house(c,cx,cy,s,color,t,t0,out=None):
    p=eo(prog(t,t0,0.4))
    if p<=0: return
    a=p*(1-prog(t,out,0.25) if out else 1)
    L=Image.new("RGBA",(420,420),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.polygon([(210,20),(400,190),(20,190)],fill=color); d.rectangle([60,180,360,400],fill=color)
    d.rectangle([170,270,250,400],fill=NAVY); d.rectangle([90,220,150,280],fill=NAVY); d.rectangle([270,220,330,280],fill=NAVY)
    put(c,L,cx,cy,s*(0.7+0.3*eb(prog(t,t0,0.4))),a)
# ---------- scenes ----------
def scene(c,t):
    # S1 hook 0-3.4
    if t<3.5:
        text(c,"IL QUARTO",BLK,110,CREAM,W/2,560,t,0.0,0.3,"up",out=3.35)
        text(c,"CONDONO",BLK,150,AMBER,W/2,720,t,0.35,0.3,"zoom",out=3.35)
        text(c,"EDILIZIO?",BLK,110,CREAM,W/2,870,t,1.2,0.3,"up",out=3.35)
        p=prog(t,1.7,0.3)
        if p>0: put(c,tlayer("4°",BLK,300,AMBER),W/2,1150,2.0-1.0*eo(p),eo(p)*(1-prog(t,3.35,0.25)))
    # S2 3.6-7.5
    elif t<7.6:
        text(c,"COS'È UN",BLK,100,CREAM,W/2,600,t,3.6,0.3,"up",out=7.45)
        text(c,"CONDONO?",BLK,140,AMBER,W/2,740,t,3.9,0.3,"pop",out=7.45)
        text(c,"40",BLK,330,CREAM,W/2,1030,t,6.2,0.3,"zoom",out=7.45)
        text(c,"ANNI DI SANATORIE",XB,48,GREY,W/2,1220,t,6.4,0.3,"up",out=7.45)
    # S3 7.8-16.6
    elif t<16.6:
        house(c,W/2,700,1.0,CREAM,t,7.8,out=16.45)
        if t<13.4:
            stamp(c,"ABUSIVA",RED,W/2,760,t,8.3,out=10.6)
            p=prog(t,10.6,0.3)
            if p>0:
                stamp(c,"IN REGOLA",GREEN,W/2,760,t,10.7,out=13.3)
            text(c,"PAGANDO  €",BLK,80,AMBER,W/2,1080,t,9.6,0.3,"pop",out=13.3)
            text(c,"costruita senza permessi",SB,44,GREY,W/2,1180,t,11.2,0.3,"up",out=13.3)
        else:
            rrect(c,(150,1000,930,1110),24,(235,64,64,60),t,13.6,out=16.45)
            text(c,"×  NIENTE DEMOLIZIONE",XB,52,CREAM,W/2,1055,t,13.6,0.3,"pop",out=16.45)
            rrect(c,(150,1140,930,1250),24,(70,200,120,60),t,15.0,out=16.45)
            text(c,"✓  LA CASA SI PUÒ VENDERE",XB,48,CREAM,W/2,1195,t,15.0,0.3,"pop",out=16.45)
    # S4 timeline 16.7-29
    elif t<29.0:
        text(c,"I TRE CONDONI",BLK,72,AMBER,W/2,330,t,16.7,0.3,"up",out=28.85)
        p=eo(prog(t,16.8,1.0)); x0=170
        y0,y1=470,1250
        a=1-prog(t,28.85,0.2)
        with OV(c) as d: d.line([(x0,y0),(x0,y0+(y1-y0)*p)],fill=GOLD+(int(200*a),),width=6)
        for (yr,who,ts,yy_) in [("1985","Governo Craxi",16.9,560),("1994","Governo Berlusconi I",20.9,860),("2003","Governo Berlusconi II",25.4,1160)]:
            q=prog(t,ts,0.35)
            if q>0:
                r=int(22*eb(q))
                with OV(c) as d: d.ellipse([x0-r,yy_-r,x0+r,yy_+r],fill=AMBER+(int(255*a),))
                text(c,yr,BLK,150,CREAM,x0+60,yy_-40,t,ts,0.35,"up",anchor="lm",out=28.85)
                text(c,who,SB,44,AMBER,x0+66,yy_+70,t,ts+0.9,0.35,"up",anchor="lm",out=28.85)
        source(c,"Leggi 47/1985, 724/1994 e Dl 269/2003",t,17.5,28.9)
    # S5 numbers 29-38.6
    elif t<38.6:
        p=eo(prog(t,29.2,2.2)); n=15007199*p
        text(c,"DOMANDE PRESENTATE",XB,50,GREY,W/2,430,t,29.2,0.3,"up",out=38.45)
        put(c,tlayer(fmt(n) if p<1 else "15 MILIONI",BLK,130 if p<1 else 150,AMBER),W/2,600,1,eo(prog(t,29.2,0.3))*(1-prog(t,38.45,0.2)))
        if t>=33.2:
            text(c,"ANCORA SENZA RISPOSTA",XB,50,GREY,W/2,830,t,35.3,0.3,"up",out=38.45)
            q=eo(prog(t,35.4,1.6))
            put(c,tlayer(fmt(4263897*q) if q<1 else "4,26 MILIONI",BLK,120,CREAM),W/2,990,1,eo(prog(t,35.3,0.3))*(1-prog(t,38.45,0.2)))
            # bar
            a=eo(prog(t,35.4,0.3))*(1-prog(t,38.45,0.2))
            if a>0:
                with OV(c) as d:
                    d.rounded_rectangle([120,1110,960,1170],30,fill=(255,255,255,int(40*a)))
                    d.rounded_rectangle([120,1110,120+max(60,840*0.284*q),1170],30,fill=RED+(int(255*a),))
                text(c,"28% DEL TOTALE",XB,40,CREAM,W/2,1225,t,36.8,0.3,"up",out=38.45)
            source(c,"Rapporto 2019 sui condoni, via Italia Oggi",t,33.3,38.5)
        else:
            source(c,"Domande dei tre condoni (rapporto 2019)",t,29.6,33.1)
    # S6 ranking 38.7-43.7
    elif t<43.7:
        text(c,"REGIONI CON PIÙ",XB,56,GREY,W/2,420,t,38.75,0.3,"up",out=43.55)
        text(c,"PRATICHE FERME",BLK,90,CREAM,W/2,510,t,38.9,0.3,"up",out=43.55)
        a=1-prog(t,43.55,0.2)
        for i,(nm,v,ts,col) in enumerate([("CAMPANIA",656832,40.6,AMBER),("LAZIO",623897,41.0,GOLD)]):
            q=eo(prog(t,ts,0.9)); y=700+i*230
            if q>0:
                with OV(c) as d: d.rounded_rectangle([110,y,110+max(40,860*(v/656832)*q),y+120],20,fill=col+(int(235*a),))
                put(c,tlayer(nm,BLK,64,NAVY),140,y+60,1,a*eo(prog(t,ts+0.2,0.3)),anchor="lm")
                put(c,tlayer(fmt(v*q),BLK,64,CREAM),110,y+180,1,a*eo(prog(t,ts,0.3)),anchor="lm")
        source(c,"Domande di condono ancora da evadere (2019)",t,39.2,43.6)
    # S7 Campania 43.8-55
    elif t<55.0:
        text(c,"CAMPANIA",BLK,140,AMBER,W/2,430,t,43.85,0.3,"zoom",out=54.85)
        if t<50.2:
            text(c,"CONDONO 2003",BLK,90,CREAM,W/2,700,t,46.3,0.3,"up",out=50.1)
            stamp(c,"MAI RECEPITO",RED,W/2,900,t,48.0,size=80,out=50.1)
            source(c,"La Regione non adottò la legge regionale",t,46.6,50.1)
        else:
            text(c,"RISULTATO",XB,56,GREY,W/2,640,t,50.25,0.3,"up",out=54.85)
            q=eo(prog(t,51.1,1.4))
            put(c,tlayer("~"+fmt(50000*q),BLK,190,CREAM),W/2,830,1,eo(prog(t,51.1,0.3))*(1-prog(t,54.85,0.2)))
            text(c,"ORDINI DI DEMOLIZIONE",BLK,64,AMBER,W/2,1010,t,52.0,0.3,"up",out=54.85)
            text(c,"IN SOSPESO",BLK,64,AMBER,W/2,1090,t,53.6,0.3,"pop",out=54.85)
            source(c,"Fonte: Quotidiano Nazionale, 17 novembre 2026",t,51.2,54.9)
    # S8 proposal 55.1-67.7
    elif t<67.7:
        if t<64.8:
            text(c,"LA PROPOSTA",XB,56,GREY,W/2,400,t,55.15,0.3,"up",out=64.7)
            rrect(c,(110,460,970,700),30,(255,255,255,28),t,55.2,out=64.7)
            text(c,"EMENDAMENTO FdI",BLK,74,AMBER,W/2,530,t,55.3,0.3,"pop",out=64.7)
            text(c,"alla manovra 2027",SB,50,CREAM,W/2,620,t,57.4,0.3,"up",out=64.7)
            text(c,"ABUSI ENTRO IL",XB,54,GREY,W/2,800,t,59.1,0.3,"up",out=64.7)
            text(c,"31 MARZO 2003",BLK,110,CREAM,W/2,910,t,60.3,0.3,"zoom",out=64.7)
            text(c,"IPOTESI: TUTTA ITALIA",BLK,64,AMBER,W/2,1130,t,62.4,0.3,"pop",out=64.7)
        else:
            text(c,"CHI DICE NO",BLK,90,CREAM,W/2,520,t,64.85,0.3,"up",out=67.55)
            stamp(c,"LEGA: NO",RED,W/2,790,t,65.2,size=96,angle=-6,out=67.55)
            stamp(c,"OPPOSIZIONI: NO",RED,W/2,1060,t,66.3,size=80,angle=5,out=67.55)
    # S9 pro/contro 67.8-76
    elif t<76.0:
        text(c,"LE DUE POSIZIONI",BLK,72,CREAM,W/2,360,t,67.8,0.3,"up",out=75.85)
        rrect(c,(80,450,1000,840),34,(70,200,120,48),t,67.9,out=75.85)
        text(c,"FAVOREVOLI",BLK,70,GREEN,W/2,530,t,68.0,0.3,"pop",out=75.85)
        text(c,"famiglie in un limbo",SB,54,CREAM,W/2,650,t,69.6,0.3,"up",out=75.85)
        text(c,"da 20 anni",XB,64,CREAM,W/2,740,t,70.9,0.3,"up",out=75.85)
        rrect(c,(80,880,1000,1270),34,(235,64,64,48),t,72.2,out=75.85)
        text(c,"CONTRARI",BLK,70,RED,W/2,960,t,72.2,0.3,"pop",out=75.85)
        text(c,"premia chi ha",SB,54,CREAM,W/2,1080,t,73.6,0.3,"up",out=75.85)
        text(c,"violato le regole",XB,64,CREAM,W/2,1170,t,74.5,0.3,"up",out=75.85)
    # S10 closing 76.1-81.4
    elif t<81.35:
        if t<79.1:
            text(c,"DICEMBRE",BLK,150,AMBER,W/2,640,t,76.2,0.3,"zoom",out=79.0)
            text(c,"decide la commissione",SB,54,CREAM,W/2,800,t,78.0,0.3,"up",out=79.0)
        else:
            text(c,"TU COSA",BLK,130,CREAM,W/2,600,t,79.15,0.25,"pop")
            text(c,"NE PENSI?",BLK,130,AMBER,W/2,750,t,79.45,0.25,"pop")
            text(c,"SCRIVILO NEI COMMENTI",XB,54,CREAM,W/2,960,t,80.2,0.3,"up")
            p=prog(t,80.4,0.3)
            if p>0:
                yb=1060+12*math.sin(t*9); a=int(255*eo(p))
                with OV(c) as d: d.polygon([(W/2-50,yb),(W/2+50,yb),(W/2,yb+60)],fill=AMBER+(a,))
    else:
        # end card
        p=eo(prog(t,81.35,0.4))
        L=logo.resize((int(logo.width*3),192)); put(c,L,W/2,640,0.8+0.2*p,p)
        text(c,"MEZZO MINUTO",BLK,96,GOLD,W/2,820,t,81.5,0.35,"up")
        text(c,"Un minuto e mezzo · la politica spiegata",SB,46,CREAM,W/2,920,t,81.8,0.35,"up")
        text(c,"SEGUI LA PAGINA",BLK,64,AMBER,W/2,1080,t,82.2,0.3,"pop")
        text(c,"Fonti: Italia Oggi · AGI · QN · Il Fatto Quotidiano · Il Politico",MD,28,GREY,W/2,1250,t,82.4,0.4,"up")
def frame(tr):
    t=tr*SP if tr*SP<81.35 else 81.35+(tr-81.35/SP)
    c=background(t)
    L=Image.new("RGBA",(W,H),(0,0,0,0)); scene(L,t)
    b=max([0]+[x for x in BOUND if x<=t]); dt=t-b
    z=1+0.05*min(1,dt/3.0)
    ox=oy=0
    if b>0 and dt<0.3:
        oy=int((1-eo(dt/0.3))*260)
    for i in IMPACT:
        if 0<=t-i<0.3:
            k=1-(t-i)/0.3; r=np.random.default_rng(int(t*100)); ox+=int(r.uniform(-1,1)*16*k); oy+=int(r.uniform(-1,1)*16*k); z+=0.06*k
    if b>0 and dt<0.12: L=L.filter(ImageFilter.BoxBlur(int(10*(1-dt/0.12))+1))
    if abs(z-1)>0.002:
        nw,nh=int(W*z),int(H*z); L=L.resize((nw,nh),Image.BILINEAR); L=L.crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
    c.alpha_composite(L,(0,0)) if ox==0 and oy==0 else c.paste(L,(ox,oy),L)
    if b>0 and dt<0.08:
        c.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,int(70*(1-dt/0.08)))))
    header(c,t)
    if t<81.35: captions(c,t)
    return c.convert("RGB")
if __name__=="__main__":
    if sys.argv[1]=="still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"r/f_{ts}.png")
    else:
        i0,i1,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",out+".tmp.mp4"],stdin=subprocess.PIPE)
        for i in range(i0,i1):
            p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); assert p.wait()==0; os.rename(out+".tmp.mp4",out)
