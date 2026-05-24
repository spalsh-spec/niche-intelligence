"""Single-file shareable web app — Apple-style, multi-niche.

Bakes every niche's analysis into one self-contained index.html: a niche-picker
home ("marketplace"), a per-niche dashboard, an in-browser brief generator, and
inline optimization hints. No server, no API keys. Works on laptop and phone.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from .. import config
from ..brand.brief import _survivor_features
from ..brand.filter import translate_pattern
from ..pipeline import run
from .report import off_brand_winners, steal_this


def _niche_payload(insight, niche: dict) -> Dict[str, Any]:
    survivors = [{
        "feature": c.feature, "statement": c.statement, "robustness": c.robustness,
        "lift": c.lift, "support": c.support, "population": c.population,
        "counterexamples": c.counterexamples, "contradictions": c.contradictions,
        "falsification_ratio": c.falsification_ratio,
        "guidance": translate_pattern(c)[0], "recommended": translate_pattern(c)[1],
        "examples": c.examples,
    } for c in insight.survivors]
    return {
        "meta": {
            "label": niche["label"], "emoji": niche["emoji"],
            "tagline": niche["tagline"], "persona": niche["persona"],
            "pillars": niche["pillars"], "anti_patterns": niche["anti_patterns"],
            "tone": niche["tone"], "topics": niche["topics"],
            "live": insight.live_mode, "llm": insight.llm_mode,
            "n_videos": len(insight.videos),
            "n_creators": len({v.creator for v in insight.videos}),
            "n_survivors": len(insight.survivors),
            "n_claims": len(insight.all_claims),
        },
        "topVideos": [{
            "creator": v.creator, "title": v.title, "score": v.performance_score,
            "engagement": round(v.engagement_rate * 100, 1),
        } for v in insight.top],
        "survivors": survivors,
        "recommendedFeatures": sorted(_survivor_features(insight.survivors)),
        "stealThis": {p: (translate_pattern(c)[0] if c else None)
                      for p, c in steal_this(insight).items()},
        "offBrand": [{"statement": c.statement, "guidance": translate_pattern(c)[0]}
                     for c in off_brand_winners(insight)],
        "ledger": [{
            "feature": c.feature, "verdict": c.verdict, "robustness": c.robustness,
            "lift": c.lift, "counterexamples": c.counterexamples,
            "contradictions": c.contradictions,
        } for c in sorted(insight.all_claims, key=lambda c: c.robustness, reverse=True)],
    }


def build_payload(force_sample: bool = False) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    order = []
    for key, niche in config.NICHES.items():
        insight = run(key, force_sample=force_sample)
        data[key] = _niche_payload(insight, niche)
        order.append({"key": key, "label": niche["label"],
                      "emoji": niche["emoji"], "tagline": niche["tagline"]})
    return {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "niches": order, "data": data}


def build_webapp(force_sample: bool = False) -> str:
    return _TEMPLATE.replace("__DATA__", json.dumps(build_payload(force_sample)))


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Niche Intelligence</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--ink:#1d1d1f;--sub:#6e6e73;--bg:#fbfbfd;--card:#ffffff;--line:#e8e8ed;
--blue:#0071e3;--blue2:#0066cc;--good:#1d8a4e;--warn:#b25e00;--bad:#c4314b;
--radius:20px;--shadow:0 4px 24px rgba(0,0,0,.06);}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Arial,sans-serif;
line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px}
nav{position:sticky;top:0;z-index:20;background:rgba(251,251,253,.8);
backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;gap:14px;height:52px}
.brand{font-weight:600;font-size:18px;letter-spacing:-.02em;cursor:pointer}
.brand .dot{color:var(--blue)}
.nav-niche{margin-left:auto;font-size:14px;color:var(--sub);display:flex;align-items:center;gap:8px}
.nav-niche button{font:inherit;border:1px solid var(--line);background:var(--card);
border-radius:980px;padding:6px 14px;cursor:pointer;color:var(--blue);font-weight:500}
.hero{text-align:center;padding:72px 0 36px}
.hero h1{font-size:clamp(34px,6vw,60px);line-height:1.05;letter-spacing:-.03em;
font-weight:600;margin:0 0 16px}
.hero p{font-size:clamp(17px,2.4vw,22px);color:var(--sub);max-width:660px;margin:0 auto;font-weight:400}
.eyebrow{color:var(--blue);font-weight:600;font-size:15px;letter-spacing:.01em;margin:0 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:16px;padding:14px 0 80px}
.ncard{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
padding:22px 18px;cursor:pointer;transition:transform .18s ease,box-shadow .18s ease;
text-align:left;display:flex;flex-direction:column;gap:6px;min-height:148px}
.ncard:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.ncard .em{font-size:32px}
.ncard .nm{font-weight:600;font-size:17px;letter-spacing:-.01em}
.ncard .tg{font-size:13px;color:var(--sub);line-height:1.35}
section.view{display:none;padding-bottom:90px}
section.view.active{display:block}
.vhead{padding:40px 0 8px}
.vhead .em{font-size:40px}
.vhead h2{font-size:clamp(28px,5vw,44px);letter-spacing:-.03em;margin:6px 0 6px;font-weight:600}
.vhead p{color:var(--sub);margin:0;font-size:17px}
.pills{margin-top:14px;display:flex;flex-wrap:wrap;gap:7px}
.pill{background:#f0f0f5;color:#3a3a3c;font-size:12.5px;padding:5px 11px;border-radius:980px}
h3{font-size:24px;letter-spacing:-.02em;margin:46px 0 6px;font-weight:600}
.lede{color:var(--sub);margin:0 0 18px;font-size:15px}
.tip{display:flex;gap:10px;align-items:flex-start;background:#f0f6ff;border:1px solid #d6e7ff;
border-radius:14px;padding:13px 15px;margin:14px 0;font-size:14px;color:#1a4480}
.tip .i{flex:none;width:20px;height:20px;border-radius:50%;background:var(--blue);color:#fff;
font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px 18px}
.kpi .n{font-size:32px;font-weight:600;letter-spacing:-.02em}
.kpi .l{font-size:13px;color:var(--sub);margin-top:2px}
.chartbox{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
padding:20px;height:380px;margin-top:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
padding:20px;margin-bottom:14px}
.pat-head{display:flex;justify-content:space-between;align-items:center;gap:12px}
.pat-title{font-weight:600;font-size:16px;letter-spacing:-.01em}
.tag{font-size:11px;font-weight:700;padding:4px 10px;border-radius:980px;white-space:nowrap}
.tag.on{background:#e3f6ec;color:var(--good)} .tag.off{background:#fdecef;color:var(--bad)}
.bar{height:8px;border-radius:980px;background:#eee;overflow:hidden;margin:12px 0}
.bar>span{display:block;height:100%;background:linear-gradient(90deg,var(--blue),#34c759)}
.meta{font-size:13px;color:var(--sub)}
.guid{font-size:15px;margin-top:11px;padding:12px 14px;background:#f5f5f7;border-radius:12px}
.gen{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 4px}
.gen input{flex:1;min-width:230px;padding:14px 16px;border:1px solid var(--line);
border-radius:14px;font-size:16px;background:var(--card);color:var(--ink)}
.gen input:focus{outline:none;border-color:var(--blue);box-shadow:0 0 0 4px rgba(0,113,227,.12)}
.btn{padding:14px 26px;border:none;border-radius:980px;background:var(--blue);color:#fff;
font-size:16px;font-weight:500;cursor:pointer;transition:background .15s}
.btn:hover{background:var(--blue2)}
.chips{margin:6px 0 16px;display:flex;flex-wrap:wrap;gap:8px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:980px;padding:7px 14px;
font-size:13.5px;cursor:pointer;color:var(--blue)}
.chip:hover{background:#f0f6ff}
.brief .t{font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;
color:var(--sub);margin:16px 0 5px}
.brief ol{margin:4px 0;padding-left:22px} .brief li{margin:6px 0;font-size:17px;font-weight:500}
.scorepill{display:inline-block;font-weight:700;padding:4px 12px;border-radius:980px;font-size:13px}
.s-good{background:#e3f6ec;color:var(--good)} .s-mid{background:#fff2dd;color:var(--warn)}
.s-bad{background:#fdecef;color:var(--bad)}
details{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
padding:6px 20px;margin-top:8px}
summary{cursor:pointer;font-weight:600;padding:14px 0;font-size:16px}
table{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--sub)}
td.r,th.r{text-align:right}
.v-supported{color:var(--good);font-weight:600} .v-weak{color:var(--warn)} .v-falsified{color:var(--bad)}
.foot{text-align:center;color:var(--sub);font-size:13px;padding:30px 0 50px;border-top:1px solid var(--line);margin-top:30px}
@media(max-width:600px){.kpis{grid-template-columns:repeat(2,1fr)}.hero{padding:46px 0 24px}
.grid{grid-template-columns:repeat(2,1fr)}.chartbox{height:320px}}
</style></head><body>

<nav><div class="wrap">
  <div class="brand" onclick="goHome()">Niche<span class="dot">.</span>Intelligence</div>
  <div class="nav-niche"><span id="navLabel"></span>
    <button id="changeBtn" onclick="goHome()" style="display:none">Change niche</button></div>
</div></nav>

<div class="wrap">
  <section id="home" class="view active">
    <div class="hero">
      <p class="eyebrow">For creators</p>
      <h1>See what's working in your niche. And why.</h1>
      <p>Pick your lane. We score what's winning, prove which patterns actually
         hold up, and turn them into a brief in your voice.</p>
    </div>
    <div class="grid" id="nicheGrid"></div>
  </section>

  <section id="niche" class="view">
    <div class="vhead">
      <div class="em" id="nEmoji"></div>
      <h2 id="nTitle"></h2>
      <p id="nTagline"></p>
    </div>

    <div class="kpis" id="kpis"></div>

    <h3>What's winning</h3>
    <div class="chartbox"><canvas id="perfChart"></canvas></div>

    <h3>Do more of this</h3>
    <p class="lede">The patterns that held up. Pick one and run with it.</p>
    <div id="survivors"></div>

    <h3>Your next video</h3>
    <div class="gen">
      <input id="topic" placeholder="Type a topic…">
      <button class="btn" onclick="generate()">Generate</button>
    </div>
    <div class="chips" id="chips"></div>
    <div id="briefOut"></div>
    <div class="tip"><span class="i">i</span><div>Aim for alignment
      <b>0.8+</b>. A flag, or a score under 0.5, means the topic fights your
      brand — reframe it before you film.</div></div>

    <details>
      <summary>Details — the numbers & full ledger</summary>
      <div id="offbrand"></div>
      <table><thead><tr><th>Pattern</th><th>Verdict</th><th class="r">Robust.</th>
        <th class="r">Lift</th></tr></thead>
        <tbody id="ledgerRows"></tbody></table>
    </details>
  </section>

  <div class="foot">Niche Intelligence · fuzzy-logic scoring + Popperian
     falsification + a per-niche brand filter. Sample data — add a data source to go live.</div>
</div>

<script>
const DATA = __DATA__;
const STOP = new Set(["the","a","an","of","to","and","for","your","with","in","on"]);
let cur = null, chart = null;

function tc(s){return s.split(" ").map(w=>w?w[0].toUpperCase()+w.slice(1):w).join(" ");}
function clean(s){s=(s||"").trim();while(s.endsWith("."))s=s.slice(0,-1);return s;}
function esc(s){const d=document.createElement("div");d.textContent=s==null?"":s;return d.innerHTML;}

/* ----- brand filter (JS port) ----- */
function words(list){const set=new Set();list.forEach(p=>p.toLowerCase().split(/[^a-z]+/)
  .forEach(w=>{if(w&&!STOP.has(w)&&w.length>2)set.add(w);}));return set;}
function antiFlags(text,anti){const t=text.toLowerCase();const out=[];
  anti.forEach(ap=>{const ws=ap.toLowerCase().split(/[^a-z]+/).filter(w=>w&&!STOP.has(w)&&w.length>2);
    if(ws.length&&ws.every(w=>t.includes(w)))out.push(ap);});return out;}
function alignment(text,pillars,anti){const t=text.toLowerCase();let h=0;
  words(pillars).forEach(w=>{if(t.includes(w))h++;});
  return Math.max(0,Math.min(1,0.5+0.5*Math.min(h/2,1)-0.6*Math.min(antiFlags(text,anti).length,1)));}

/* ----- brief generator (JS port of brand/brief.py) ----- */
function genTitles(topic,feats,meta){const T=tc(clean(topic));const persona=tc((meta.persona.split(" ").length<=2)?meta.persona:"creator");
  const pillar=tc(meta.pillars[0]||"results");const out=[];
  if(feats.has("title.identity"))out.push("Become the Person Who Actually Masters "+T);
  if(feats.has("title.first_person"))out.push("I Tried "+T+" for 30 Days — Here's What Actually Happened");
  if(feats.has("title.specific_system"))out.push("The "+T+" System That Actually Works (Step by Step)");
  if(feats.has("title.curiosity_gap"))out.push("The Truth About "+T+" Nobody Tells You");
  [T+": The "+pillar+" Approach","How I Think About "+T+" as a "+persona,"The Honest Guide to "+T]
    .forEach(d=>{if(out.length<3&&out.indexOf(d)<0)out.push(d);});
  return out.slice(0,3);}
function genThumb(feats){const b=[];
  if(feats.has("thumb.face"))b.push("your face in frame, calm and expressive");
  if(feats.has("thumb.clean"))b.push("one clear subject with lots of empty space");
  if(!b.length)b.push("one clear subject, high contrast, minimal clutter");
  return b.join("; ")+". Keep text overlay minimal or none.";}
function generate(){
  const d=DATA.data[cur],meta=d.meta;
  const topic=document.getElementById("topic").value||meta.topics[0];
  const feats=new Set(d.recommendedFeatures);
  const titles=genTitles(topic,feats,meta);
  const thumb=genThumb(feats);
  const hook="Everything you've been told about "+clean(topic).toLowerCase()+" misses the real point. Here's what actually works.";
  const caption="1) Open with the identity or outcome the viewer wants.\n2) Your lived proof or the specific method.\n3) The one principle they can apply today.\n4) A grounded invitation — no pushy CTA.";
  const blob=titles.join(" ")+" "+hook+" "+caption;
  const al=alignment(blob,meta.pillars,meta.anti_patterns),flags=antiFlags(blob,meta.anti_patterns);
  const cls=al>=0.66?"s-good":al>=0.4?"s-mid":"s-bad";
  document.getElementById("briefOut").innerHTML='<div class="card brief">'+
    '<div class="t">Title options</div><ol>'+titles.map(x=>"<li>"+esc(x)+"</li>").join("")+"</ol>"+
    '<div class="t">Thumbnail direction</div><div>'+esc(thumb)+"</div>"+
    '<div class="t">Hook (first 3 seconds)</div><div>'+esc(hook)+"</div>"+
    '<div class="t">Caption structure</div><div style="white-space:pre-line">'+esc(caption)+"</div>"+
    '<div class="meta" style="margin-top:14px">brand alignment <span class="scorepill '+cls+'">'+al.toFixed(2)+
    "</span> · flags: "+(flags.length?esc(flags.join(", ")):"none")+"</div></div>";}

/* ----- routing + rendering ----- */
function goHome(){cur=null;localStorage.removeItem("ni_niche");
  document.getElementById("home").classList.add("active");
  document.getElementById("niche").classList.remove("active");
  document.getElementById("navLabel").textContent="";
  document.getElementById("changeBtn").style.display="none";
  window.scrollTo(0,0);}
function renderHome(){
  document.getElementById("nicheGrid").innerHTML=DATA.niches.map(n=>
    '<div class="ncard" onclick="openNiche(\''+n.key+'\')"><div class="em">'+n.emoji+
    '</div><div class="nm">'+esc(n.label)+'</div><div class="tg">'+esc(n.tagline)+"</div></div>").join("");}
function openNiche(key){
  cur=key;localStorage.setItem("ni_niche",key);
  const d=DATA.data[key],m=d.meta;
  document.getElementById("home").classList.remove("active");
  document.getElementById("niche").classList.add("active");
  document.getElementById("navLabel").textContent=m.emoji+" "+m.label;
  document.getElementById("changeBtn").style.display="inline-block";
  document.getElementById("nEmoji").textContent=m.emoji;
  document.getElementById("nTitle").textContent=m.label;
  document.getElementById("nTagline").textContent=m.tagline;
  const top=d.topVideos[0]||{score:0};
  document.getElementById("kpis").innerHTML=[
    [m.n_survivors,"validated patterns"],[m.n_videos,"videos analyzed"],
    [Math.round(top.score),"top score"]
  ].map(x=>'<div class="kpi"><div class="n">'+x[0]+'</div><div class="l">'+x[1]+"</div></div>").join("");
  const rec=d.survivors.filter(c=>c.recommended).slice(0,3);
  document.getElementById("survivors").innerHTML=rec.length?rec.map(c=>
    '<div class="card"><div class="pat-title">'+esc(c.statement)+"</div>"+
    '<div class="bar"><span style="width:'+Math.round(c.robustness*100)+'%"></span></div>'+
    '<div class="guid">Steal this → '+esc(c.guidance)+"</div></div>").join("")
    :'<div class="card meta">No strong on-brand pattern this cycle. The tool only shows what holds up.</div>';
  document.getElementById("offbrand").innerHTML=d.offBrand.length?
    ('<p class="lede" style="margin:6px 0">Wins to ignore (off-brand):</p>'+
     d.offBrand.map(c=>'<div class="meta" style="margin:4px 0">• '+esc(c.statement)+"</div>").join("")):"";
  document.getElementById("chips").innerHTML=m.topics.slice(0,5).map(tp=>
    '<span class="chip" onclick="pick(\''+esc(tp).replace(/'/g,"")+'\')">'+esc(tp)+"</span>").join("");
  document.getElementById("topic").value=m.topics[0];
  document.getElementById("ledgerRows").innerHTML=d.ledger.map(c=>
    "<tr><td>"+esc(c.feature)+'</td><td class="v-'+c.verdict+'">'+c.verdict+"</td>"+
    '<td class="r">'+c.robustness.toFixed(2)+'</td><td class="r">'+c.lift.toFixed(2)+"</td></tr>").join("");
  if(chart)chart.destroy();
  chart=new Chart(document.getElementById("perfChart"),{type:"bar",
    data:{labels:d.topVideos.map(v=>v.title.slice(0,42)),
      datasets:[{label:"score",data:d.topVideos.map(v=>v.score),backgroundColor:"#0071e3",borderRadius:6}]},
    options:{indexAxis:"y",plugins:{legend:{display:false}},
      scales:{x:{max:100,grid:{color:"#eee"}},y:{ticks:{font:{size:11}}}},maintainAspectRatio:false}});
  generate();window.scrollTo(0,0);}
function pick(tp){document.getElementById("topic").value=tp;generate();}

renderHome();
const saved=localStorage.getItem("ni_niche");
if(saved&&DATA.data[saved])openNiche(saved);
</script></body></html>"""
