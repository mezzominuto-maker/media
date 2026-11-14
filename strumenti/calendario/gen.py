"""Builds the Mezzo Minuto calendar page from calendar.json (edit the JSON, rerun, republish)."""
import json, html, os, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "calendar.json"), encoding="utf-8"))

STATUS = {"ok": ("PROGRAMMATO", "ok"), "todo": ("DA CONFERMARE", "todo"),
          "auto": ("AUTOMATICO", "auto"), "done": ("PUBBLICATO", "done"), "free": ("", "")}

def slot(s, idx, date=''):
    label, cls = STATUS[s.get("status", "ok")]
    iso = f'{date}T{s["time"]}:00+01:00' if date else ''
    st = f'<span class="status {cls}" data-iso="{iso}">{label}</span>' if label else ""
    kind = s.get("kind", "reel")
    tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in s.get("where", []))
    meta = f'<div class="meta">{html.escape(s["meta"])}</div>' if s.get("meta") else ""
    play = ""
    attrs = ""
    if s.get("clip"):
        play = '<span class="play">▶ guarda</span>'
        attrs = f' data-i="{idx}" tabindex="0" role="button"'
    title_style = ' style="color:var(--muted)"' if s.get("status") == "free" else ""
    return (f'<div class="slot{" clickable" if s.get("clip") else ""}"{attrs}><div class="time">{s["time"]}</div>'
            f'<div class="{kind}"><div class="what"{title_style}>{html.escape(s["title"])}{st}</div>{meta}'
            f'<div class="tags">{tags}{play}</div></div></div>')

flat, days_html = [], []
for d in data["days"]:
    rows = []
    for s in d["slots"]:
        rows.append(slot(s, len(flat), d.get('date','')))
        flat.append(s)
    days_html.append(f'<section class="day"><h2>{html.escape(d["label"])} <small>{html.escape(d.get("sub",""))}</small></h2>{"".join(rows)}</section>')

details = [{"title": s["title"], "clip": s.get("clip"), "caption": s.get("caption", ""), "planner": s.get("planner", []),
            "when": s.get("when", ""), "meta": s.get("meta", "")} for s in flat]

page = f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mezzo Minuto – Calendario pubblicazioni</title>
<style>
:root{{--bg:#0d1221;--card:#161e36;--line:#26304f;--text:#f0ece2;--muted:#9aa3bd;--amber:#ffc43d;--blue:#569cff;--green:#40ce96;--violet:#be82ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:28px 18px 60px}}h1{{font-size:28px;margin:0 0 4px;letter-spacing:-.5px}}
.sub{{color:var(--muted);margin:0 0 18px;font-size:15px}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 22px;font-size:13px;color:var(--muted)}}.legend span{{display:inline-flex;align-items:center;gap:6px}}
.dot{{width:10px;height:10px;border-radius:50%;display:inline-block}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
.day{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}}.day h2{{margin:0 0 12px;font-size:18px}}.day h2 small{{color:var(--muted);font-weight:500;font-size:13px;margin-left:6px}}
.slot{{display:grid;grid-template-columns:54px 1fr;gap:10px;padding:10px 6px;border-top:1px solid var(--line);border-radius:8px}}.slot:first-of-type{{border-top:none}}
.clickable{{cursor:pointer}}.clickable:hover,.clickable:focus{{background:#1d2747;outline:none}}
.time{{font-weight:800;font-variant-numeric:tabular-nums;color:var(--amber)}}.what{{font-weight:650;line-height:1.3}}
.meta{{color:var(--muted);font-size:13px;margin-top:4px;line-height:1.4}}.tags{{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px;align-items:center}}
.tag{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:#0f1730;border:1px solid var(--line)}}
.play{{font-size:12px;font-weight:800;color:var(--bg);background:var(--amber);padding:2px 9px;border-radius:999px}}
.status{{display:inline-block;font-size:11px;font-weight:800;padding:2px 8px;border-radius:6px;margin-left:6px;vertical-align:1px}}
.ok{{background:rgba(64,206,150,.15);color:var(--green)}}.todo{{background:rgba(255,196,61,.15);color:var(--amber)}}.auto{{background:rgba(86,156,255,.15);color:var(--blue)}}.done{{background:rgba(154,163,189,.15);color:var(--muted)}}
.reel{{border-left:3px solid var(--violet);padding-left:10px}}.news{{border-left:3px solid var(--blue);padding-left:10px}}
footer{{color:var(--muted);font-size:13px;margin-top:26px;line-height:1.5}}
#modal{{position:fixed;inset:0;background:rgba(5,8,16,.86);display:none;align-items:center;justify-content:center;padding:16px;z-index:9}}
#modal.open{{display:flex}}.box{{background:var(--card);border:1px solid var(--line);border-radius:18px;max-width:880px;width:100%;max-height:94vh;overflow:auto;display:grid;grid-template-columns:minmax(220px,340px) 1fr;gap:18px;padding:16px}}
@media(max-width:700px){{.box{{grid-template-columns:1fr}}}}
video{{width:100%;border-radius:12px;background:#000;aspect-ratio:9/16}}
.box h3{{margin:2px 0 6px;font-size:19px}}.box .when{{color:var(--amber);font-weight:700;font-size:14px}}
.cap{{white-space:pre-wrap;background:#0f1730;border:1px solid var(--line);border-radius:12px;padding:12px;font-size:14px;line-height:1.45;margin:12px 0}}
.links a{{display:inline-block;margin:0 8px 8px 0;color:var(--bg);background:var(--blue);padding:6px 12px;border-radius:999px;font-weight:700;font-size:13px;text-decoration:none}}
.close{{float:right;background:none;border:1px solid var(--line);color:var(--text);border-radius:999px;padding:4px 12px;cursor:pointer}}
</style></head><body><main>
<h1>⏱️ Mezzo Minuto – Calendario</h1>
<p class="sub">Aggiornato il {html.escape(data["updated"])} · orari di Roma · tocca un reel per guardarlo</p>
<div class="legend"><span><i class="dot" style="background:var(--blue)"></i>Notizie del giorno (automatiche)</span>
<span><i class="dot" style="background:var(--violet)"></i>Reel dibattiti/podcast</span>
<span><b class="status ok">PROGRAMMATO</b> su Metricool</span><span><b class="status done">PUBBLICATO</b></span></div>
<div class="grid">{"".join(days_html)}</div>
<footer>{html.escape(data.get("note",""))}</footer>
</main>
<div id="modal" role="dialog" aria-modal="true"><div class="box"><div><video id="v" controls playsinline preload="metadata"></video></div>
<div><button class="close" id="x">Chiudi</button><div class="when" id="w"></div><h3 id="t"></h3><div class="meta" id="m"></div><div class="cap" id="c"></div><div class="links" id="l"></div></div></div></div>
<script>
const D={json.dumps(details, ensure_ascii=False)};
const M=document.getElementById('modal'),V=document.getElementById('v');
function openI(i){{const d=D[i];if(!d||!d.clip)return;V.src=d.clip;document.getElementById('t').textContent=d.title;
document.getElementById('w').textContent=d.when;document.getElementById('m').textContent=d.meta;
document.getElementById('c').textContent=d.caption||'';const L=document.getElementById('l');L.innerHTML='';
(d.planner||[]).forEach(p=>{{const a=document.createElement('a');a.href=p.url;a.target='_blank';a.rel='noopener';a.textContent='Apri in Metricool – '+p.label;L.appendChild(a);}});
M.classList.add('open');}}
function closeM(){{M.classList.remove('open');V.pause();V.removeAttribute('src');V.load();}}
document.querySelectorAll('.clickable').forEach(el=>{{el.addEventListener('click',()=>openI(+el.dataset.i));el.addEventListener('keydown',e=>{{if(e.key==='Enter')openI(+el.dataset.i)}});}});
document.getElementById('x').onclick=closeM;M.addEventListener('click',e=>{{if(e.target===M)closeM();}});
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeM();}});
(function(){{const now=Date.now();document.querySelectorAll('.status[data-iso]').forEach(el=>{{
 if(!(el.classList.contains('ok')||el.classList.contains('auto')))return;const t=Date.parse(el.dataset.iso);
 if(!isNaN(t)&&now>t+10*60000){{el.textContent='PUBBLICATO';el.className='status done';}}}});}})();

</script></body></html>"""
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
print("ok", len(flat), "slots")
