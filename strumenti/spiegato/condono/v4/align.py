import re,json,subprocess
T="""Hai costruito senza permesso? Lo Stato potrebbe perdonarti. Di nuovo.
Fratelli d'Italia vuole riaprire il condono edilizio del 2003, con un emendamento alla manovra.
Un condono permette di mettere in regola, pagando, una costruzione fatta senza permessi. Niente demolizione, e la casa si può vendere.
In Italia ce ne sono già stati tre: nel 1985, nel '94 e nel 2003.
Ma la Campania quello del 2003 non l'ha mai applicato. E lì oggi restano circa 50.000 ordini di demolizione.
La bozza però va oltre. In tutta Italia si potrebbero sanare anche piccole irregolarità: un muro interno spostato, un secondo bagno, finestre diverse dal progetto. Restano escluse le zone dove non si può costruire. Poi ogni Regione avrebbe 60 giorni per decidere se applicarlo.
La Lega è contraria. Contrari anche Pd, Avs e Legambiente.
Per chi è a favore, si chiude un'ingiustizia verso la Campania. Per chi è contro, si premia ancora una volta chi ha violato le regole.
Si decide a dicembre, in commissione Bilancio.
Tu cosa ne pensi? Scrivilo nei commenti."""
NUM={"1985":"millenovecentoottantacinque","94":"novantaquattro","2003":"duemilatre","50000":"cinquantamila","60":"sessanta","Pd":"piddi","Avs":"avuesse"}
words=T.split()
def syl(w):
    w=w.lower(); w=NUM.get(re.sub(r"\W","",w),w)
    return max(1,len(re.findall(r"[aeiouàèéìòù]+",w)))
S=[syl(w) for w in words]
out=subprocess.run(["ffmpeg","-i","voce.mp3","-af","silencedetect=noise=-35dB:d=0.15","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",out)]; en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",out)]
# speech segments
segs=[]; cur=en[0]
for s,e in zip(st[1:] if st[0]<0.1 else st, en[1:]):
    pass
starts=[0.0]+en; ends=st+[64.36]
segs=list(zip(starts,ends))
segs=[(a,b) for a,b in segs if b>a]
print(len(segs),segs[:3],segs[-2:])
brk=[i for i,w in enumerate(words) if w[-1] in ",.?:" and w not in ("favore,","contro,")]  # break after word i
n=len(segs); 
# DP: choose n-1 breaks from brk (monotonic) to minimize squared deviation of syllable rate
import math
cs=[0]
for s in S: cs.append(cs[-1]+s)
best={}
def cost(i0,i1,k):
    syl=cs[i1]-cs[i0]; d=segs[k][1]-segs[k][0]
    r=max(syl,0.01)/max(d,0.01); return (math.log(r/6.6))**2
cand=brk
INF=1e9
# dp[k][j]: segments 0..k-1 assigned, last break at cand index j (word end idx)
dp=[{} for _ in range(n+1)]; dp[0][-1]=(0,None)
for k in range(n):
    for prev,(c,_) in dp[k].items():
        i0=prev+1
        opts=[b for b in cand if b>=i0] if k<n-1 else [len(words)-1]
        for b in opts:
            cc=c+cost(i0,b+1,k)
            if b not in dp[k+1] or cc<dp[k+1][b][0]: dp[k+1][b]=(cc,prev)
b=len(words)-1; path=[]
for k in range(n,0,-1):
    path.append(b); b=dp[k][b][1]
path=path[::-1]
res=[]; i0=0
for k,b in enumerate(path):
    a,e=segs[k]; tot=cs[b+1]-cs[i0]; t=a
    for i in range(i0,b+1):
        d=(e-a)*S[i]/tot; res.append(dict(w=words[i],s=round(t,3),e=round(t+d,3))); t+=d
    print(f"{a:6.2f}-{e:6.2f} r={tot/(e-a):.1f}  "+" ".join(words[i0:b+1]))
    i0=b+1
json.dump(res,open("words.json","w"),ensure_ascii=False)
