# Niche Intelligence — Personal Brand Supertool

Turns *what is winning in your niche* into *what to make next* — and throws away the lucky coincidences.

It scores creator content by **fuzzy logic**, mines the patterns behind the winners, then **actively tries to disprove each pattern** (a Popperian falsification eval) before trusting it. Surviving patterns are translated through **your brand** into ready-to-shoot content briefs.

## 🌐 Live web app

Once GitHub Pages finishes its first deploy, the interactive app is live at:

**https://spalsh-spec.github.io/niche-intelligence/**

Dashboard + an in-browser content-brief generator. No server, no API keys — share the link with anyone.

## Run it locally

```bash
python3 -m brand_supertool report                 # report + dashboard
python3 -m brand_supertool report --topic "..."   # + a content brief
python3 -m brand_supertool webapp                  # build the shareable index.html
python3 -m brand_supertool brief  --topic "..."    # brief only
python3 -m pytest -q                               # 20 tests
```

Runs end-to-end with **zero API keys** on a bundled sample corpus.

## The three differentiators

- **Fuzzy-logic scoring** — "is this a winner?" is a matter of degree (velocity + engagement), not a view threshold.
- **Falsification eval** — for every pattern it hunts counterexamples and contradictions; only survivors are reported. Spurious correlations are filtered out.
- **Brand filter** — every output is scored for brand alignment and screened for anti-patterns; off-brand "wins" are never recommended.

## Architecture

```
ingest → analyze → fuzzy score → mine patterns → falsify → brand filter → report
```

| Layer | Module | Responsibility |
|---|---|---|
| Ingestion | `brand_supertool/ingestion/` | YouTube Data API v3 + sample fallback |
| Intelligence | `brand_supertool/intelligence/` | fuzzy scoring, analysis, pattern mining, falsify eval |
| Brand filter | `brand_supertool/brand/` | alignment scoring, anti-patterns, brief generator |
| Reporting | `brand_supertool/reporting/` | markdown report, HTML dashboard, shareable web app |

## Make it yours

Everything personal lives in `brand_supertool/config.py`: brand pillars, tone, anti-patterns, tracked creators, and the falsification thresholds.

## Going live

Copy `.env.example` to `.env` and add `YOUTUBE_API_KEY` (real data) and/or `ANTHROPIC_API_KEY` (Claude-written briefs). Without them, deterministic heuristics keep everything working; any live failure falls back to the sample corpus.

---

_MVP. Pattern robustness on a small sample is directional, not statistically powered — enable the live pull and track 150+ videos for trustworthy conclusions._
