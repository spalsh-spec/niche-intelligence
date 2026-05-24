"""Weekly Niche Intelligence Report — markdown + HTML dashboard."""
from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Dict, List, Optional

from ..brand.filter import translate_pattern
from ..models import BrandProfile, ContentBrief, PatternClaim
from ..pipeline import Insight


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def steal_this(insight: Insight) -> Dict[str, Optional[PatternClaim]]:
    """Top surviving + brand-recommended pattern per platform."""
    out: Dict[str, Optional[PatternClaim]] = {}
    for plat in sorted({v.platform for v in insight.videos}):
        best = None
        for c in insight.survivors:
            if c.platform == plat and translate_pattern(c)[1]:
                best = c
                break
        out[plat] = best
    return out


def off_brand_winners(insight: Insight) -> List[PatternClaim]:
    """Patterns that won the niche but you should NOT chase (off-brand)."""
    seen, out = set(), []
    for c in insight.all_claims:
        if c.lift >= 1.05 and c.support >= 2 and not translate_pattern(c)[1]:
            if c.feature not in seen:
                seen.add(c.feature)
                out.append(c)
    return out


# --------------------------------------------------------------------------- #
# Markdown
# --------------------------------------------------------------------------- #
def build_markdown(insight: Insight, brand: BrandProfile) -> str:
    L: List[str] = []
    L.append("# Weekly Niche Intelligence Report")
    L.append(f"_Generated {datetime.now():%Y-%m-%d %H:%M} · "
             f"{'LIVE' if insight.live_mode else 'SAMPLE'} data · "
             f"{'Claude' if insight.llm_mode else 'heuristic'} analysis_\n")

    L.append("## 1. What is winning (top content by fuzzy performance)\n")
    L.append("| # | Score | Creator | Title | Views | Eng% |")
    L.append("|--:|------:|---------|-------|------:|-----:|")
    for i, v in enumerate(insight.top, 1):
        L.append(f"| {i} | **{v.performance_score:.0f}** | {v.creator} | "
                 f"{v.title} | {v.views:,} | {v.engagement_rate*100:.1f}% |")
    L.append("")

    L.append("## 2. Why it is winning (patterns that SURVIVED falsification)\n")
    if not insight.survivors:
        L.append("_No pattern cleared the falsification bar this cycle._\n")
    for c in insight.survivors:
        guidance, recommended = translate_pattern(c)
        tag = "✅ on-brand" if recommended else "⚠️ off-brand"
        L.append(f"### {c.statement}  ")
        L.append(f"- robustness **{c.robustness:.2f}** · lift **{c.lift:.2f}×** "
                 f"· support {c.support}/{c.population} · {tag}")
        L.append(f"- falsify eval: {c.counterexamples} counterexample(s), "
                 f"{c.contradictions} contradiction(s) "
                 f"(falsification ratio {c.falsification_ratio:.2f})")
        L.append(f"- **steal this →** {guidance}")
        if c.examples:
            L.append(f"- examples: {'; '.join(c.examples)}")
        L.append("")

    L.append("## 3. One \"steal this\" per platform\n")
    for plat, c in steal_this(insight).items():
        if c:
            L.append(f"- **{plat.title()}:** {translate_pattern(c)[0]}")
        else:
            L.append(f"- **{plat.title()}:** no on-brand pattern survived yet.")
    L.append("")

    obw = off_brand_winners(insight)
    L.append("## 4. Wins to IGNORE (off-brand)\n")
    if obw:
        for c in obw:
            L.append(f"- {c.statement} → {translate_pattern(c)[0]}")
    else:
        L.append("_Nothing this cycle — no off-brand pattern is actually "
                 "winning the niche. Stay the course._")
    L.append("")

    L.append("## 5. Falsification ledger (full transparency)\n")
    L.append("| Pattern | Verdict | Robustness | Lift | Counterex. | Contra. |")
    L.append("|---------|---------|-----------:|-----:|-----------:|--------:|")
    for c in sorted(insight.all_claims, key=lambda c: c.robustness, reverse=True):
        L.append(f"| {c.feature} | {c.verdict} | {c.robustness:.2f} | "
                 f"{c.lift:.2f} | {c.counterexamples} | {c.contradictions} |")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# HTML dashboard (self-contained; Chart.js from CDN)
# --------------------------------------------------------------------------- #
_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Niche Intelligence Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--ink:#1b2a36;--sea:#1f6f8b;--olive:#6b7a3b;--sun:#e0a72e;--terra:#c05a3a;
--bg:#f6f2e9;--card:#fffdf8;--muted:#7c8a92;--line:#e7e0d2;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
background:var(--bg);color:var(--ink);line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
h1{font-size:30px;margin:0 0 4px} h2{font-size:19px;margin:34px 0 14px;border-bottom:2px solid var(--line);padding-bottom:6px}
.sub{color:var(--muted);font-size:13px;margin-bottom:8px}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;background:var(--sea);color:#fff;margin-right:6px}
.badge.heur{background:var(--olive)} .badge.sample{background:var(--terra)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.kpi .n{font-size:26px;font-weight:700;color:var(--sea)} .kpi .l{font-size:12px;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:14px}
.pat-head{display:flex;justify-content:space-between;align-items:center;gap:10px}
.pat-title{font-weight:600;font-size:15px}
.tag{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px}
.tag.on{background:#e7f0d8;color:#4d5e22} .tag.off{background:#f6ddd2;color:#9a3d22}
.bar{height:9px;border-radius:5px;background:var(--line);overflow:hidden;margin:8px 0}
.bar>span{display:block;height:100%;background:linear-gradient(90deg,var(--sun),var(--terra))}
.meta{font-size:12px;color:var(--muted);margin:4px 0}
.guid{font-size:14px;margin-top:8px;padding:10px 12px;background:#fbf6ea;border-left:3px solid var(--sun);border-radius:6px}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}
th{background:#efe8da;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#5b6770}
td.r,th.r{text-align:right} tr:last-child td{border-bottom:none}
.verdict{font-weight:600} .v-supported{color:var(--olive)} .v-weak{color:var(--sun)} .v-falsified{color:var(--terra)}
.chartbox{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;height:340px}
.brief .t{font-weight:600;margin:6px 0} .brief li{margin:3px 0}
.foot{margin-top:40px;font-size:12px;color:var(--muted);text-align:center}
.pillars span{display:inline-block;background:#eef1e3;color:#4d5e22;font-size:12px;padding:3px 9px;border-radius:20px;margin:2px}
</style></head><body><div class="wrap">
<h1>🌿 Niche Intelligence Dashboard</h1>
<div class="sub">__SUBTITLE__</div>
<div>__BADGES__</div>
<div class="pillars" style="margin-top:12px">__PILLARS__</div>

<div class="kpis">
  <div class="kpi"><div class="n">__N_VIDEOS__</div><div class="l">videos analyzed</div></div>
  <div class="kpi"><div class="n">__N_SURV__</div><div class="l">patterns survived falsification</div></div>
  <div class="kpi"><div class="n">__N_CLAIMS__</div><div class="l">hypotheses tested</div></div>
  <div class="kpi"><div class="n">__TOP_SCORE__</div><div class="l">top performance score</div></div>
</div>

<h2>What is winning</h2>
<div class="chartbox"><canvas id="perfChart"></canvas></div>

<h2>Why it is winning — survivors of the falsify eval</h2>
__SURVIVORS__

<h2>One "steal this" per platform</h2>
__STEAL__

__OFFBRAND__

<h2>Content brief — your next move</h2>
__BRIEF__

<h2>Falsification ledger</h2>
<table><thead><tr><th>Pattern</th><th>Verdict</th><th class="r">Robustness</th>
<th class="r">Lift</th><th class="r">Counter</th><th class="r">Contra</th></tr></thead>
<tbody>__LEDGER__</tbody></table>

<div class="foot">Generated by Personal Brand Supertool · fuzzy-logic scoring +
Popperian falsification + brand filter. Patterns shown only after surviving an
active attempt to disprove them.</div>
</div>
<script>
const PERF = __PERF_JSON__;
new Chart(document.getElementById('perfChart'),{
 type:'bar',
 data:{labels:PERF.labels,datasets:[{label:'Fuzzy performance score',
   data:PERF.scores,backgroundColor:'#1f6f8b',borderRadius:6}]},
 options:{indexAxis:'y',plugins:{legend:{display:false}},
   scales:{x:{max:100,grid:{color:'#e7e0d2'}},y:{ticks:{font:{size:11}}}},
   maintainAspectRatio:false}});
</script></body></html>"""


def _esc(s: str) -> str:
    return html.escape(str(s))


def _survivor_cards(insight: Insight) -> str:
    if not insight.survivors:
        return ('<div class="card"><div class="meta">No pattern cleared the '
                'falsification bar this cycle. That is a feature, not a bug — '
                'the tool refuses to hand you noise.</div></div>')
    cards = []
    for c in insight.survivors:
        guidance, recommended = translate_pattern(c)
        tag = ('<span class="tag on">ON-BRAND</span>' if recommended
               else '<span class="tag off">OFF-BRAND</span>')
        pct = int(c.robustness * 100)
        cards.append(f"""<div class="card">
 <div class="pat-head"><div class="pat-title">{_esc(c.statement)}</div>{tag}</div>
 <div class="bar"><span style="width:{pct}%"></span></div>
 <div class="meta">robustness {c.robustness:.2f} · lift {c.lift:.2f}× ·
   support {c.support}/{c.population} · falsify ratio {c.falsification_ratio:.2f}
   ({c.counterexamples} counterexamples, {c.contradictions} contradictions)</div>
 <div class="guid">steal this → {_esc(guidance)}</div>
</div>""")
    return "\n".join(cards)


def _steal_html(insight: Insight) -> str:
    rows = []
    for plat, c in steal_this(insight).items():
        msg = translate_pattern(c)[0] if c else "no on-brand pattern survived yet."
        rows.append(f'<div class="card"><b>{_esc(plat.title())}:</b> {_esc(msg)}</div>')
    return "\n".join(rows)


def _offbrand_html(insight: Insight) -> str:
    obw = off_brand_winners(insight)
    if not obw:
        return ""
    rows = "".join(
        f'<div class="card"><b>{_esc(c.statement)}</b><div class="guid">'
        f'{_esc(translate_pattern(c)[0])}</div></div>' for c in obw)
    return f'<h2>Wins to ignore (off-brand)</h2>{rows}'


def _brief_html(brief: Optional[ContentBrief]) -> str:
    if not brief:
        return '<div class="card meta">Run with --topic to generate a brief.</div>'
    titles = "".join(f"<li>{_esc(t)}</li>" for t in brief.titles)
    flags = (", ".join(brief.anti_pattern_flags)
             if brief.anti_pattern_flags else "none")
    return f"""<div class="card brief">
 <div class="t">Topic: {_esc(brief.topic)}</div>
 <div class="t">Title options</div><ul>{titles}</ul>
 <div class="t">Thumbnail direction</div><div>{_esc(brief.thumbnail_direction)}</div>
 <div class="t">Hook (first 3s)</div><div>{_esc(brief.hook)}</div>
 <div class="t">Caption structure</div><div style="white-space:pre-line">{_esc(brief.caption_structure)}</div>
 <div class="meta" style="margin-top:10px">brand alignment
   <b>{brief.brand_alignment:.2f}</b> · anti-pattern flags: {_esc(flags)} ·
   grounded in: {_esc(', '.join(brief.grounded_in) or 'brand defaults')}</div>
</div>"""


def _ledger_html(insight: Insight) -> str:
    rows = []
    for c in sorted(insight.all_claims, key=lambda c: c.robustness, reverse=True):
        rows.append(
            f'<tr><td>{_esc(c.feature)}</td>'
            f'<td class="verdict v-{c.verdict}">{c.verdict}</td>'
            f'<td class="r">{c.robustness:.2f}</td><td class="r">{c.lift:.2f}</td>'
            f'<td class="r">{c.counterexamples}</td><td class="r">{c.contradictions}</td></tr>')
    return "\n".join(rows)


def build_dashboard_html(insight: Insight, brand: BrandProfile,
                         brief: Optional[ContentBrief] = None) -> str:
    top = insight.top
    perf = {"labels": [f"{v.creator}: {v.title[:40]}" for v in top],
            "scores": [v.performance_score for v in top]}
    badges = (f'<span class="badge {"sample" if not insight.live_mode else ""}">'
              f'{"LIVE" if insight.live_mode else "SAMPLE DATA"}</span>'
              f'<span class="badge {"" if insight.llm_mode else "heur"}">'
              f'{"CLAUDE ANALYSIS" if insight.llm_mode else "HEURISTIC MODE"}</span>')
    pillars = "".join(f"<span>{_esc(p)}</span>" for p in brand.pillars)

    out = _TEMPLATE
    repl = {
        "__SUBTITLE__": f"Generated {datetime.now():%Y-%m-%d %H:%M} · "
                        f"{len(insight.videos)} videos across "
                        f"{len({v.creator for v in insight.videos})} creators",
        "__BADGES__": badges,
        "__PILLARS__": pillars,
        "__N_VIDEOS__": str(len(insight.videos)),
        "__N_SURV__": str(len(insight.survivors)),
        "__N_CLAIMS__": str(len(insight.all_claims)),
        "__TOP_SCORE__": f"{top[0].performance_score:.0f}" if top else "0",
        "__SURVIVORS__": _survivor_cards(insight),
        "__STEAL__": _steal_html(insight),
        "__OFFBRAND__": _offbrand_html(insight),
        "__BRIEF__": _brief_html(brief),
        "__LEDGER__": _ledger_html(insight),
        "__PERF_JSON__": json.dumps(perf),
    }
    for k, v in repl.items():
        out = out.replace(k, v)
    return out
