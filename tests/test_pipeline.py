"""End-to-end pipeline + reporting smoke tests on the sample corpus."""
from brand_supertool.brand.brief import generate_brief
from brand_supertool.config import BRAND
from brand_supertool.pipeline import run
from brand_supertool.reporting.report import (build_dashboard_html,
                                              build_markdown)


def test_pipeline_runs_and_scores_everything():
    ins = run(force_sample=True)
    assert len(ins.videos) == 18
    assert all(0 <= v.performance_score <= 100 for v in ins.videos)
    # corpus is sorted descending by score
    scores = [v.performance_score for v in ins.videos]
    assert scores == sorted(scores, reverse=True)


def test_identity_pattern_survives_on_sample_data():
    """The sample corpus is tuned so identity titles genuinely win.
    The falsify eval should let that through."""
    ins = run(force_sample=True)
    feats = {c.feature for c in ins.survivors}
    assert "title.identity_trigger" in feats


def test_fear_clickbait_does_not_get_recommended():
    """Even if shouty titles appear, they must never be an on-brand survivor."""
    from brand_supertool.brand.filter import translate_pattern
    ins = run(force_sample=True)
    for c in ins.survivors:
        if c.feature == "title.fear_clickbait":
            assert translate_pattern(c)[1] is False


def test_webapp_builds_self_contained():
    from brand_supertool.reporting.webapp import build_payload, build_webapp
    ins = run(force_sample=True)
    payload = build_payload(ins, BRAND)
    assert payload["recommendedFeatures"]            # brief generator has inputs
    assert payload["survivors"]
    assert payload["brand"]["pillars"]
    html = build_webapp(ins, BRAND)
    assert "__DATA__" not in html                    # payload injected
    assert "const DATA =" in html
    assert "function generate()" in html             # client-side brief gen
    assert html.count('data-t="') == 4               # all tabs present


def test_reports_render_without_error():
    ins = run(force_sample=True)
    brief = generate_brief("eating like a greek fisherman", ins.survivors, BRAND)
    md = build_markdown(ins, BRAND)
    html = build_dashboard_html(ins, BRAND, brief=brief)
    assert "Weekly Niche Intelligence Report" in md
    assert "<canvas id=\"perfChart\">" in html
    assert "__" not in html.split("<script>")[0]  # all placeholders replaced
    assert brief.titles  # brief produced
