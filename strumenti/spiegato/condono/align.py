import re,json,subprocess
T="""In Italia potrebbe arrivare il quarto condono edilizio. Ma che cos'è un condono, e perché se ne parla ancora dopo quarant'anni?
Un condono permette di mettere in regola, pagando, una costruzione fatta senza permessi. Così si evita la demolizione e la casa si può vendere.
Il primo arriva nel 1985, con il governo Craxi. Il secondo nel 1994, con il primo governo Berlusconi. Il terzo nel 2003, con il secondo governo Berlusconi.
In tutto sono state presentate circa quindici milioni di domande. Secondo un rapporto del 2019, più di quattro milioni aspettavano ancora una risposta. La regione con più pratiche ferme? La Campania, con oltre seicentocinquantamila.
E proprio la Campania è il punto di oggi. Lì il condono del 2003 non è mai stato recepito dalla Regione. Risultato: circa cinquantamila ordini di demolizione ancora in sospeso.
Fratelli d'Italia vuole riaprire i termini con un emendamento alla manovra, solo per gli abusi fatti entro il 31 marzo 2003. Si ragiona anche di estenderlo a tutta Italia. La Lega è contraria, le opposizioni anche.
Chi è favorevole dice che migliaia di famiglie vivono in un limbo da vent'anni. Chi è contrario dice che ogni condono premia chi ha violato le regole.
La decisione arriverà a dicembre, in commissione. Tu cosa ne pensi? Scrivilo nei commenti."""
NUM={"1985":"millenovecentottantacinque","1994":"millenovecentonovantaquattro","2003":"duemilatre","2019":"duemiladiciannove","31":"trentuno"}
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
starts=[0.0]+en; ends=st+[81.3]
segs=list(zip(starts,ends))
segs=[(a,b) for a,b in segs if b>a]
print(len(segs),segs[:3],segs[-2:])
brk=[i for i,w in enumerate(words) if w[-1] in ",.?:"]  # break after word i
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
