# Tempi STIMATI (senza voce) per la bozza: 6,6 sillabe/s, pause dopo punteggiatura.
import re as _r
TOT=sum(max(1,len(_r.findall(r'[aeiouàèéìòù]+',w.lower()))) for w in open('testo.txt').read().split())/5.81  # ritmo di Raf sul condono
# Quando arriva voce.mp3 si sostituisce con align.py (come condono/v4/align.py).
import re,json
T=open("testo_sottotitoli.txt").read()
NUM={"64":"sessantaquattro","67":"sessantasette","2019":"duemiladiciannove","2027":"duemilaventisette","2028":"duemilaventotto","850":"ottocentocinquanta","26":"ventisei"}
def syl(w):
    w=w.lower(); w=NUM.get(re.sub(r"[^\w]","",w),w)
    return max(1,len(re.findall(r"[aeiouàèéìòù]+",w)))
res=[]; t=0.0
for line in T.strip().split("\n"):
    for w in line.split():
        d=syl(w)/6.6; res.append(dict(w=w,s=round(t,3),e=round(t+d,3))); t+=d
        if w[-1] in ".?": t+=0.42
        elif w[-1] in ",:": t+=0.2
    print(f"{res[-1]['e']*1:6.2f}  {line[:70]}")
k=TOT/t  # ritmo medio di Raf misurato sul condono: 5,8 sillabe/s pause comprese
for x in res: x["s"]=round(x["s"]*k,3); x["e"]=round(x["e"]*k,3)
t=t*k
json.dump(res,open("words.json","w"),ensure_ascii=False)
print("fine voce",round(t,2),"-> video",round(t/1.12+2.6,1),"s")
