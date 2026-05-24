"""Command-line entrypoint (multi-niche).

    python -m brand_supertool webapp                      # build the shareable app (all niches)
    python -m brand_supertool report --niche finance
    python -m brand_supertool report --niche fitness --topic "fat loss"
    python -m brand_supertool brief  --niche philosophy --topic "dealing with death"
    python -m brand_supertool niches                      # list available niches
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config
from .brand.brief import generate_brief
from .pipeline import run
from .reporting.report import build_dashboard_html, build_markdown
from .reporting.webapp import build_webapp


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def cmd_niches(args) -> int:
    for k, n in config.NICHES.items():
        print(f"  {n['emoji']}  {k:<14} {n['label']} — {n['tagline']}")
    return 0


def cmd_report(args) -> int:
    insight = run(args.niche, force_sample=args.sample)
    brand = config.get_brand(args.niche)
    brief = (generate_brief(args.topic, insight.survivors, args.niche)
             if args.topic else None)
    out = config.OUTPUT_DIR
    md_path = _write(out / "report.md", build_markdown(insight, brand))
    html_path = _write(out / "dashboard.html",
                       build_dashboard_html(insight, brand, brief=brief))
    print(f"Niche: {args.niche} · {'LIVE' if insight.live_mode else 'SAMPLE'} data")
    print(f"Analyzed {len(insight.videos)} videos · "
          f"{len(insight.survivors)}/{len(insight.all_claims)} survived falsification")
    print(f"Markdown : {md_path}")
    print(f"Dashboard: {html_path}")
    return 0


def cmd_webapp(args) -> int:
    html = build_webapp(force_sample=args.sample)
    path = _write(config.OUTPUT_DIR / "index.html", html)
    print(f"Shareable webapp ({len(config.NICHES)} niches): {path}")
    return 0


def cmd_brief(args) -> int:
    insight = run(args.niche, force_sample=args.sample)
    brief = generate_brief(args.topic, insight.survivors, args.niche)
    lines = [f"# Content Brief — {brief.topic}  ({args.niche})\n", "## Title options"]
    lines += [f"- {t}" for t in brief.titles]
    lines += [f"\n## Thumbnail direction\n{brief.thumbnail_direction}",
              f"\n## Hook (first 3s)\n{brief.hook}",
              f"\n## Caption structure\n{brief.caption_structure}",
              f"\n_brand alignment {brief.brand_alignment:.2f} · "
              f"flags: {', '.join(brief.anti_pattern_flags) or 'none'}_"]
    path = _write(config.OUTPUT_DIR / "brief.md", "\n".join(lines))
    print("\n".join(lines))
    print(f"\nSaved: {path}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="brand_supertool",
                                description="Personal Brand Supertool (multi-niche)")
    p.add_argument("--sample", action="store_true",
                   help="force bundled sample data even if API keys exist")
    p.add_argument("--niche", default=config.DEFAULT_NICHE,
                   choices=list(config.NICHES.keys()),
                   help="creator niche to analyze")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("niches", help="list available niches").set_defaults(func=cmd_niches)

    rp = sub.add_parser("report", help="intelligence report + dashboard")
    rp.add_argument("--topic", help="also generate a content brief")
    rp.set_defaults(func=cmd_report)

    sub.add_parser("webapp", help="build the shareable app (all niches)").set_defaults(func=cmd_webapp)

    bp = sub.add_parser("brief", help="generate a content brief")
    bp.add_argument("--topic", required=True)
    bp.set_defaults(func=cmd_brief)

    args = p.parse_args(argv)
    if not args.cmd:
        args = p.parse_args((argv or []) + ["report"])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
