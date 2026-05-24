"""Brand filter + analyzer + brief tests."""
from brand_supertool.brand.brief import generate_brief
from brand_supertool.brand.filter import (anti_pattern_flags, brand_alignment,
                                           translate_pattern)
from brand_supertool.config import BRAND
from brand_supertool.intelligence.analyzer import extract_title_flags
from brand_supertool.models import PatternClaim


def test_on_brand_text_scores_higher_than_off_brand():
    on = "Getting lean the Mediterranean way with sun and freedom"
    off = "Calorie counting and macro tracking for gym-bro hustle"
    assert brand_alignment(on, BRAND) > brand_alignment(off, BRAND)


def test_anti_pattern_detection():
    flags = anti_pattern_flags("My calorie counting and macro tracking plan", BRAND)
    assert "calorie counting" in flags
    assert "macro tracking" in flags


def test_translate_pattern_marks_offbrand():
    fear = PatternClaim(feature="title.fear_clickbait", statement="s",
                        platform="youtube", lift=1.3, support=5, population=10)
    _, recommended = translate_pattern(fear)
    assert recommended is False

    ident = PatternClaim(feature="title.identity_trigger", statement="s",
                         platform="youtube", lift=1.3, support=5, population=10)
    _, recommended = translate_pattern(ident)
    assert recommended is True


def test_title_flag_extraction():
    f = extract_title_flags("I Got Leaner Eating Like a Greek Fisherman (No Scale)")
    assert f["title.identity_trigger"]
    assert f["title.first_person_result"]
    assert f["title.freedom_negation"]


def test_brief_is_on_brand_and_has_three_titles():
    survivors = [
        PatternClaim(feature="title.identity_trigger", statement="s",
                     platform="youtube", lift=1.4, support=6, population=12,
                     robustness=0.8, survived=True),
        PatternClaim(feature="thumb.sunlit", statement="s", platform="youtube",
                     lift=1.3, support=6, population=12, robustness=0.7,
                     survived=True),
    ]
    brief = generate_brief("morning sun training", survivors, BRAND)
    assert len(brief.titles) == 3
    assert brief.anti_pattern_flags == []      # must not produce off-brand copy
    assert brief.brand_alignment >= 0.5
