import re,json,subprocess
DUR=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voce.mp3"],capture_output=True,text=True).stdout)
T=open("testo_sottotitoli.txt").read().strip()
NUM={"25":"venticinque","5%":"cinquepercento","5":"cinque","2018":"duemiladiciotto","18":"diciotto","Cgil":"cigiielle","Imu":"imu"}
words=T.split()
def syl(w):
    w=w.lower(); k=re.sub(r"[^\w%]","",w); w=NUM.get(k,NUM.get(k.rstrip("%"),w))
    return max(1,len(re.findall(r"[aeiouàèéìòù]+",w)))
S=[syl(w) for w in words]
out=subprocess.run(["ffmpeg","-i","voce.mp3","-af","silencedetect=noise=-35dB:d=0.15","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",out)]; en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",out)]
# speech segments
segs=[]; cur=en[0]
for s,e in zip(st[1:] if st[0]<0.1 else st, en[1:]):
    pass
starts=[0.0]+en; ends=st+[DUR]
segs=list(zip(starts,ends))
segs=[(a,b) for a,b in segs if b-a>0.15]  # scarta tratti spuri (rumore)
m=[list(segs[0])]
for a,b in segs[1:]:
    if a-m[-1][1]<0.2: m[-1][1]=b
    else: m.append([a,b])
segs=[tuple(x) for x in m]
print(len(segs),segs[:3],segs[-2:])
NOBRK={"case,","risparmi,"}
brk=[i for i,w in enumerate(words) if w.rstrip("»")[-1] in ",.?:" and w not in NOBRK]  # break after word i
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
