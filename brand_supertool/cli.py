"""Command-line entrypoint.

    python -m brand_supertool report                  # weekly report + dashboard
    python -m brand_supertool report --topic "morning sun routine"
    python -m brand_supertool brief --topic "fasted beach training"
    python -m brand_supertool --sample report          # force sample data
"""
from __future__ import annotations

import argparse
import json
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


def cmd_report(args) -> int:
    insight = run(force_sample=args.sample)
    brief = (generate_brief(args.topic, insight.survivors, config.BRAND)
             if args.topic else None)

    md = build_markdown(insight, config.BRAND)
    html = build_dashboard_html(insight, config.BRAND, brief=brief)

    out = config.OUTPUT_DIR
    md_path = _write(out / "report.md", md)
    html_path = _write(out / "dashboard.html", html)
    _write(out / "insight.json", json.dumps(
        {"videos": [v.to_dict() for v in insight.videos],
         "survivors": [c.to_dict() for c in insight.survivors],
         "all_claims": [c.to_dict() for c in insight.all_claims]},
        indent=2, default=str))

    print(f"Mode: {'LIVE' if insight.live_mode else 'SAMPLE'} data · "
          f"{'Claude' if insight.llm_mode else 'heuristic'} analysis")
    print(f"Analyzed {len(insight.videos)} videos · "
          f"{len(insight.survivors)}/{len(insight.all_claims)} patterns survived "
          f"falsification")
    print(f"\nMarkdown : {md_path}")
    print(f"Dashboard: {html_path}")
    if brief:
        print(f"\nTop title: {brief.titles[0]}")
    return 0


def cmd_webapp(args) -> int:
    insight = run(force_sample=args.sample)
    html = build_webapp(insight, config.BRAND)
    path = _write(config.OUTPUT_DIR / "index.html", html)
    print(f"Mode: {'LIVE' if insight.live_mode else 'SAMPLE'} data · "
          f"{'Claude' if insight.llm_mode else 'heuristic'} analysis")
    print(f"Shareable webapp: {path}")
    print("Open it in any browser, or host it (see README -> 'Share it').")
    return 0


def cmd_brief(args) -> int:
    insight = run(force_sample=args.sample)
    brief = generate_brief(args.topic, insight.survivors, config.BRAND)
    out = config.OUTPUT_DIR
    lines = [f"# Content Brief — {brief.topic}\n",
             "## Title options"]
    lines += [f"- {t}" for t in brief.titles]
    lines += [f"\n## Thumbnail direction\n{brief.thumbnail_direction}",
              f"\n## Hook (first 3s)\n{brief.hook}",
              f"\n## Caption structure\n{brief.caption_structure}",
              f"\n## Rationale\n{brief.rationale}",
              f"\n_brand alignment {brief.brand_alignment:.2f} · "
              f"flags: {', '.join(brief.anti_pattern_flags) or 'none'} · "
              f"grounded in: {', '.join(brief.grounded_in) or 'brand defaults'}_"]
    path = _write(out / "brief.md", "\n".join(lines))
    print("\n".join(lines))
    print(f"\nSaved: {path}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="brand_supertool",
                                description="Personal Brand Supertool")
    p.add_argument("--sample", action="store_true",
                   help="force bundled sample data even if API keys exist")
    sub = p.add_subparsers(dest="cmd")

    rp = sub.add_parser("report", help="weekly intelligence report + dashboard")
    rp.add_argument("--topic", help="also generate a content brief for this topic")
    rp.set_defaults(func=cmd_report)

    wp = sub.add_parser("webapp", help="build the shareable single-file webapp")
    wp.set_defaults(func=cmd_webapp)

    bp = sub.add_parser("brief", help="generate a content brief")
    bp.add_argument("--topic", required=True)
    bp.set_defaults(func=cmd_brief)

    args = p.parse_args(argv)
    if not args.cmd:
        args = p.parse_args((argv or []) + ["report"])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
