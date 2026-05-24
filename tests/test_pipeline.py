"""End-to-end multi-niche pipeline + Apple web-app build tests."""
from brand_supertool import config
from brand_supertool.brand.brief import generate_brief
from brand_supertool.brand.filter import translate_pattern
from brand_supertool.pipeline import run
from brand_supertool.reporting.report import build_dashboard_html, build_markdown
from brand_supertool.reporting.webapp import build_payload, build_webapp


def test_every_niche_runs_and_scores():
    for key in config.NICHES:
        ins = run(key, force_sample=True)
        assert len(ins.videos) == 15
        assert all(0 <= v.performance_score <= 100 for v in ins.videos)
        scores = [v.performance_score for v in ins.videos]
        assert scores == sorted(scores, reverse=True)


def test_identity_pattern_survives_each_niche():
    """Sample corpora are tuned so identity/first-person/system patterns win."""
    for key in ["fitness", "finance", "philosophy", "gaming"]:
        ins = run(key, force_sample=True)
        feats = {c.feature for c in ins.survivors}
        assert feats & {"title.identity", "title.first_person", "title.specific_system"}


def test_fear_clickbait_never_recommended():
    for key in config.NICHES:
        ins = run(key, force_sample=True)
        for c in ins.survivors:
            if c.feature in ("title.fear_clickbait", "hook.fear"):
                assert translate_pattern(c)[1] is False


def test_webapp_bakes_all_niches():
    payload = build_payload(force_sample=True)
    assert len(payload["niches"]) == len(config.NICHES)
    assert set(payload["data"]) == set(config.NICHES)
    fit = payload["data"]["fitness"]
    assert fit["recommendedFeatures"] and fit["survivors"]
    assert fit["meta"]["pillars"] and fit["meta"]["anti_patterns"]
    html = build_webapp(force_sample=True)
    assert "__DATA__" not in html
    assert "const DATA =" in html
    assert "function generate()" in html
    assert 'id="nicheGrid"' in html


def test_report_renders():
    ins = run("finance", force_sample=True)
    brand = config.get_brand("finance")
    brief = generate_brief("index funds", ins.survivors, "finance")
    assert "Weekly Niche Intelligence Report" in build_markdown(ins, brand)
    assert "perfChart" in build_dashboard_html(ins, brand, brief=brief)
    assert brief.titles
