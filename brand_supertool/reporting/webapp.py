"""Single-file shareable webapp builder.

Bakes the (Python-computed) analysis into a self-contained index.html. The
dashboard is rendered from that data; the content-brief generator is ported to
client-side JS so the page works with NO server and NO API keys — double-click
it, or drop it on any static host, and anyone you send it to can use it.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from ..brand.brief import _survivor_features  # recommended-only feature set
from ..brand.filter import translate_pattern
from ..models import BrandProfile
from ..pipeline import Insight
from .report import off_brand_winners, steal_this


def build_payload(insight: Insight, brand: BrandProfile) -> Dict[str, Any]:
    survivors = []
    for c in insight.survivors:
        guidance, recommended = translate_pattern(c)
        survivors.append({
            "feature": c.feature, "statement": c.statement,
            "robustness": c.robustness, "lift": c.lift,
            "support": c.support, "population": c.population,
            "counterexamples": c.counterexamples,
            "contradictions": c.contradictions,
            "falsification_ratio": c.falsification_ratio,
            "guidance": guidance, "recommended": recommended,
            "examples": c.examples,
        })

    return {
        "meta": {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "live": insight.live_mode, "llm": insight.llm_mode,
            "n_videos": len(insight.videos),
            "n_creators": len({v.creator for v in insight.videos}),
            "n_survivors": len(insight.survivors),
            "n_claims": len(insight.all_claims),
        },
        "brand": {
            "pillars": brand.pillars, "tone": brand.tone,
            "anti_patterns": brand.anti_patterns,
            "audience_psychology": brand.audience_psychology,
        },
        "topVideos": [{
            "creator": v.creator, "title": v.title, "url": v.url,
            "views": v.views, "score": v.performance_score,
            "engagement": round(v.engagement_rate * 100, 1),
            "platform": v.platform,
        } for v in insight.top],
        "survivors": survivors,
        "recommendedFeatures": sorted(_survivor_features(insight.survivors)),
        "stealThis": {p: (translate_pattern(c)[0] if c else None)
                      for p, c in steal_this(insight).items()},
        "offBrand": [{"statement": c.statement,
                      "guidance": translate_pattern(c)[0]}
                     for c in off_brand_winners(insight)],
        "ledger": [{
            "feature": c.feature, "verdict": c.verdict,
            "robustness": c.robustness, "lift": c.lift,
            "counterexamples": c.counterexamples,
            "contradictions": c.contradictions,
        } for c in sorted(insight.all_claims,
                          key=lambda c: c.robustness, reverse=True)],
    }


def build_webapp(insight: Insight, brand: BrandProfile) -> str:
    payload = json.dumps(build_payload(insight, brand))
    return _TEMPLATE.replace("__DATA__", payload)


# --------------------------------------------------------------------------- #
# The page. All dynamic content is rendered by JS from DATA, so this template
# is a plain string (no f-string brace pitfalls).
# --------------------------------------------------------------------------- #
_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Niche Intelligence · Personal Brand Supertool</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--ink:#1b2a36;--sea:#1f6f8b;--sea2:#2a8aa8;--olive:#6b7a3b;--sun:#e0a72e;
--terra:#c05a3a;--bg:#f6f2e9;--card:#fffdf8;--muted:#7c8a92;--line:#e7e0d2;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;
background:var(--bg);color:var(--ink);line-height:1.55}
a{color:var(--sea)}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px 90px}
header.hero{background:linear-gradient(135deg,#16404f,#1f6f8b 55%,#2a8aa8);
color:#fff;padding:46px 0 40px;margin-bottom:8px}
.hero .wrap{padding-bottom:0}
.hero h1{font-size:33px;margin:0 0 6px;letter-spacing:-.5px}
.hero p{margin:0;opacity:.92;font-size:15px;max-width:680px}
.badges{margin-top:16px}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:4px 11px;border-radius:20px;
background:rgba(255,255,255,.18);color:#fff;margin-right:7px;backdrop-filter:blur(4px)}
.pillars{margin-top:14px}
.pillars span{display:inline-block;background:rgba(255,255,255,.14);color:#fff;font-size:12px;
padding:3px 10px;border-radius:20px;margin:2px 3px 0 0}
nav.tabs{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
padding:10px 0;margin-bottom:22px}
nav.tabs .wrap{display:flex;gap:8px;flex-wrap:wrap;padding-bottom:0}
.tab{border:1px solid var(--line);background:var(--card);border-radius:22px;padding:7px 16px;
font-size:13px;font-weight:600;cursor:pointer;color:var(--ink)}
.tab.active{background:var(--sea);color:#fff;border-color:var(--sea)}
section{display:none} section.active{display:block}
h2{font-size:20px;margin:8px 0 16px;border-bottom:2px solid var(--line);padding-bottom:7px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.kpi .n{font-size:27px;font-weight:800;color:var(--sea)} .kpi .l{font-size:12px;color:var(--muted)}
.chartbox{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;height:360px;margin-bottom:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:14px}
.pat-head{display:flex;justify-content:space-between;align-items:center;gap:10px}
.pat-title{font-weight:650;font-size:15px}
.tag{font-size:10.5px;font-weight:800;padding:3px 9px;border-radius:6px;white-space:nowrap}
.tag.on{background:#e7f0d8;color:#4d5e22} .tag.off{background:#f6ddd2;color:#9a3d22}
.bar{height:9px;border-radius:5px;background:var(--line);overflow:hidden;margin:9px 0}
.bar>span{display:block;height:100%;background:linear-gradient(90deg,var(--sun),var(--terra))}
.meta{font-size:12px;color:var(--muted);margin:4px 0}
.guid{font-size:14px;margin-top:9px;padding:10px 13px;background:#fbf6ea;border-left:3px solid var(--sun);border-radius:6px}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}
th{background:#efe8da;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:#5b6770}
td.r,th.r{text-align:right} tr:last-child td{border-bottom:none}
.verdict{font-weight:700} .v-supported{color:var(--olive)} .v-weak{color:#b8860b} .v-falsified{color:var(--terra)}
.gen{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.gen input{flex:1;min-width:240px;padding:13px 15px;border:1px solid var(--line);border-radius:11px;font-size:15px;background:var(--card)}
.gen button{padding:13px 24px;border:none;border-radius:11px;background:var(--sea);color:#fff;font-size:15px;font-weight:700;cursor:pointer}
.gen button:hover{background:var(--sea2)}
.chips{margin:2px 0 18px} .chip{display:inline-block;background:var(--card);border:1px solid var(--line);
border-radius:18px;padding:5px 12px;font-size:12.5px;margin:3px 4px 0 0;cursor:pointer;color:var(--sea)}
.brief .t{font-weight:700;margin:14px 0 4px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:#5b6770}
.brief ol{margin:4px 0;padding-left:20px} .brief li{margin:5px 0;font-size:15px;font-weight:600}
.score-pill{display:inline-block;font-weight:800;padding:3px 11px;border-radius:20px;font-size:13px}
.s-good{background:#e7f0d8;color:#4d5e22} .s-mid{background:#fbeccb;color:#8a6400} .s-bad{background:#f6ddd2;color:#9a3d22}
.foot{margin-top:42px;font-size:12px;color:var(--muted);text-align:center}
@media(max-width:640px){.kpis{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:26px}}
</style></head><body>

<header class="hero"><div class="wrap">
  <h1>🌿 Niche Intelligence</h1>
  <p id="heroSub"></p>
  <div class="badges" id="badges"></div>
  <div class="pillars" id="pillars"></div>
</div></header>

<nav class="tabs"><div class="wrap">
  <button class="tab active" data-t="dash">Dashboard</button>
  <button class="tab" data-t="why">Why it wins</button>
  <button class="tab" data-t="brief">Brief generator</button>
  <button class="tab" data-t="ledger">Falsify ledger</button>
</div></nav>

<div class="wrap">
  <section id="dash" class="active">
    <div class="kpis" id="kpis"></div>
    <h2>What is winning</h2>
    <div class="chartbox"><canvas id="perfChart"></canvas></div>
    <h2>One "steal this" per platform</h2>
    <div id="steal"></div>
  </section>

  <section id="why">
    <h2>Patterns that survived falsification</h2>
    <p class="meta">Every claim below was actively attacked — we searched for
      videos that have the trait but lost (counterexamples) and videos that won
      without it (contradictions). Only survivors are shown. Noise is filtered out.</p>
    <div id="survivors"></div>
    <div id="offbrandWrap"></div>
  </section>

  <section id="brief">
    <h2>Content brief generator</h2>
    <p class="meta">Grounded in the surviving patterns, filtered through your
      brand. Runs entirely in your browser — no keys, no server.</p>
    <div class="gen">
      <input id="topic" placeholder="e.g. fasted beach training in the morning sun"
             value="eating like a Greek fisherman">
      <button onclick="generate()">Generate brief</button>
    </div>
    <div class="chips" id="chips"></div>
    <div id="briefOut"></div>
  </section>

  <section id="ledger">
    <h2>Falsification ledger — full transparency</h2>
    <p class="meta">Nothing hidden. Every hypothesis tested, its verdict, and the
      evidence for and against it.</p>
    <table><thead><tr><th>Pattern</th><th>Verdict</th><th class="r">Robustness</th>
      <th class="r">Lift</th><th class="r">Counter</th><th class="r">Contra</th></tr></thead>
      <tbody id="ledgerRows"></tbody></table>
  </section>

  <div class="foot">Personal Brand Supertool · fuzzy-logic scoring + Popperian
    falsification + brand filter. Patterns shown only after surviving an active
    attempt to disprove them.</div>
</div>

<script>
const DATA = __DATA__;
const STOP = new Set(["the","a","an","of","to","and","without","your","getting"]);

/* ---------- brand filter (JS port, identical logic to Python) ---------- */
function pillarWords(){const s=new Set();DATA.brand.pillars.forEach(p=>
  p.toLowerCase().split(/[^a-z]+/).forEach(w=>{if(w&&!STOP.has(w)&&w.length>2)s.add(w);}));return s;}
function antiFlags(text){const t=text.toLowerCase();const out=[];
  DATA.brand.anti_patterns.forEach(ap=>{const ws=ap.toLowerCase().split(/[^a-z]+/)
    .filter(w=>w&&!STOP.has(w)&&w.length>2);
    if(ws.length&&ws.every(w=>t.includes(w)))out.push(ap);});return out;}
function brandAlignment(text){const t=text.toLowerCase();let hits=0;
  pillarWords().forEach(w=>{if(t.includes(w))hits++;});
  const anti=antiFlags(text).length;
  const ps=Math.min(hits/2,1),as=Math.min(anti/1,1);
  return Math.max(0,Math.min(1,0.5+0.5*ps-0.6*as));}

/* ---------- brief generator (JS port of brand/brief.py heuristic) ---------- */
function titleCase(s){return s.replace(/\w\S*/g,w=>w.charAt(0).toUpperCase()+w.slice(1));}
function genTitles(topic,feats){const t=titleCase(topic.trim().replace(/\.$/,""));const out=[];
  if(feats.has("title.identity_trigger"))out.push(`Become the Man Who Mastered ${t} (No App, No Scale)`);
  if(feats.has("title.first_person_result"))out.push(`I Tried ${t} for 30 Days Eating Like a Greek Fisherman`);
  if(feats.has("title.freedom_negation"))out.push(`${t} — Without the Scale, the App, or the Gym`);
  if(feats.has("title.curiosity_gap"))out.push(`The Truth About ${t} Nobody in the Gym Will Tell You`);
  const defaults=[`${t} the Mediterranean Way`,`How I Stay Lean Year-Round: ${t} in the Sun`,`The Old-World Approach to ${t}`];
  for(const d of defaults){if(out.length>=3)break;if(!out.includes(d))out.push(d);}
  return out.slice(0,3);}
function genThumb(feats){const b=[];
  if(feats.has("thumb.outdoor"))b.push("outdoor coast or mountain backdrop");
  if(feats.has("thumb.sunlit"))b.push("warm low-angle sunlight");
  if(feats.has("thumb.shirtless"))b.push("natural earned physique (not posed)");
  if(feats.has("thumb.face"))b.push("calm stoic face in frame");
  if(!b.length)b.push("outdoor, sunlit, grounded — old-world living, no gym wall");
  return b.join("; ")+". Keep text overlay minimal or none.";}
function generate(){
  const topic=document.getElementById("topic").value||"your topic";
  const feats=new Set(DATA.recommendedFeatures);
  const titles=genTitles(topic,feats);
  const thumb=genThumb(feats);
  const hook=`Everything you were told about ${topic.toLowerCase().replace(/\.$/,"")} is upside down. Here's the old-world way.`;
  const caption=`1) Polarizing one-liner that names the identity.
2) The lived proof (what you did, no tracking).
3) The simple principle the audience can copy today.
4) One line of freedom/aspiration. Invite, don't sell — no pushy CTA.`;
  const blob=titles.join(" ")+" "+hook+" "+caption;
  const al=brandAlignment(blob), flags=antiFlags(blob);
  const cls=al>=0.66?"s-good":al>=0.4?"s-mid":"s-bad";
  const grounded=DATA.recommendedFeatures.length?DATA.recommendedFeatures.join(", "):"brand defaults";
  document.getElementById("briefOut").innerHTML=`<div class="card brief">
    <div class="t">Title options</div>
    <ol>${titles.map(x=>`<li>${esc(x)}</li>`).join("")}</ol>
    <div class="t">Thumbnail direction</div><div>${esc(thumb)}</div>
    <div class="t">Hook (first 3 seconds)</div><div>${esc(hook)}</div>
    <div class="t">Caption structure</div><div style="white-space:pre-line">${esc(caption)}</div>
    <div class="meta" style="margin-top:14px">brand alignment
      <span class="score-pill ${cls}">${al.toFixed(2)}</span>
      · anti-pattern flags: ${flags.length?esc(flags.join(", ")):"none"}
      · grounded in: ${esc(grounded)}</div></div>`;}

/* ---------- rendering ---------- */
function esc(s){const d=document.createElement("div");d.textContent=s==null?"":s;return d.innerHTML;}
function render(){
  const m=DATA.meta;
  document.getElementById("heroSub").textContent=
    `Generated ${m.generated} · ${m.n_videos} videos across ${m.n_creators} creators · `+
    `${m.n_survivors} of ${m.n_claims} patterns survived falsification`;
  document.getElementById("badges").innerHTML=
    `<span class="badge">${m.live?"LIVE DATA":"SAMPLE DATA"}</span>`+
    `<span class="badge">${m.llm?"CLAUDE ANALYSIS":"HEURISTIC MODE"}</span>`;
  document.getElementById("pillars").innerHTML=DATA.brand.pillars.map(p=>`<span>${esc(p)}</span>`).join("");

  const top=DATA.topVideos[0]||{score:0};
  document.getElementById("kpis").innerHTML=[
    [m.n_videos,"videos analyzed"],[m.n_survivors,"patterns survived"],
    [m.n_claims,"hypotheses tested"],[Math.round(top.score),"top performance score"]
  ].map(([n,l])=>`<div class="kpi"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");

  document.getElementById("steal").innerHTML=Object.entries(DATA.stealThis).map(([p,g])=>
    `<div class="card"><b>${esc(p[0].toUpperCase()+p.slice(1))}:</b> ${esc(g||"no on-brand pattern survived yet.")}</div>`).join("");

  document.getElementById("survivors").innerHTML=DATA.survivors.length?DATA.survivors.map(c=>{
    const tag=c.recommended?'<span class="tag on">ON-BRAND</span>':'<span class="tag off">OFF-BRAND</span>';
    const pct=Math.round(c.robustness*100);
    return `<div class="card"><div class="pat-head"><div class="pat-title">${esc(c.statement)}</div>${tag}</div>
      <div class="bar"><span style="width:${pct}%"></span></div>
      <div class="meta">robustness ${c.robustness.toFixed(2)} · lift ${c.lift.toFixed(2)}× ·
        support ${c.support}/${c.population} · falsify ratio ${c.falsification_ratio.toFixed(2)}
        (${c.counterexamples} counterexamples, ${c.contradictions} contradictions)</div>
      <div class="guid">steal this → ${esc(c.guidance)}</div></div>`;}).join("")
    :'<div class="card meta">No pattern cleared the bar this cycle — the tool refuses to hand you noise.</div>';

  document.getElementById("offbrandWrap").innerHTML=DATA.offBrand.length?
    '<h2>Wins to ignore (off-brand)</h2>'+DATA.offBrand.map(c=>
      `<div class="card"><b>${esc(c.statement)}</b><div class="guid">${esc(c.guidance)}</div></div>`).join(""):'';

  document.getElementById("ledgerRows").innerHTML=DATA.ledger.map(c=>
    `<tr><td>${esc(c.feature)}</td><td class="verdict v-${c.verdict}">${c.verdict}</td>
     <td class="r">${c.robustness.toFixed(2)}</td><td class="r">${c.lift.toFixed(2)}</td>
     <td class="r">${c.counterexamples}</td><td class="r">${c.contradictions}</td></tr>`).join("");

  document.getElementById("chips").innerHTML=
    ["morning sun routine","fasted beach training","olive oil protocol","quitting the gym for 90 days"]
    .map(c=>`<span class="chip" onclick="document.getElementById('topic').value='${c}';generate();">${c}</span>`).join("");

  new Chart(document.getElementById("perfChart"),{type:"bar",
    data:{labels:DATA.topVideos.map(v=>v.creator+": "+v.title.slice(0,38)),
      datasets:[{label:"Fuzzy performance score",data:DATA.topVideos.map(v=>v.score),
        backgroundColor:"#1f6f8b",borderRadius:6}]},
    options:{indexAxis:"y",plugins:{legend:{display:false}},
      scales:{x:{max:100,grid:{color:"#e7e0d2"}},y:{ticks:{font:{size:11}}}},
      maintainAspectRatio:false}});
}
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
  document.querySelectorAll("section").forEach(x=>x.classList.remove("active"));
  t.classList.add("active");document.getElementById(t.dataset.t).classList.add("active");});
render();generate();
</script></body></html>"""
