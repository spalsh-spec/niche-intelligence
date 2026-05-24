"""Brand filter + analyzer + brief tests (multi-niche)."""
from brand_supertool import config
from brand_supertool.brand.brief import generate_brief
from brand_supertool.brand.filter import (anti_pattern_flags, brand_alignment,
                                           translate_pattern)
from brand_supertool.intelligence.analyzer import extract_title_flags
from brand_supertool.models import PatternClaim

FIT = config.get_brand("fitness")


def test_on_brand_text_scores_higher_than_off_brand():
    on = "Discipline, strength, and energy for real movement"
    off = "A crash diet and fear-based clickbait to get shredded quick"
    assert brand_alignment(on, FIT) > brand_alignment(off, FIT)


def test_anti_pattern_detection():
    flags = anti_pattern_flags("My crash diet plan with fear-based clickbait", FIT)
    assert "crash diet" in flags
    assert "fear-based clickbait" in flags


def test_translate_pattern_marks_offbrand():
    fear = PatternClaim(feature="title.fear_clickbait", statement="s",
                        platform="youtube", lift=1.3, support=5, population=10)
    assert translate_pattern(fear)[1] is False
    ident = PatternClaim(feature="title.identity", statement="s",
                         platform="youtube", lift=1.3, support=5, population=10)
    assert translate_pattern(ident)[1] is True


def test_title_flag_extraction():
    assert extract_title_flags("Become the Person Who Mastered Fat Loss")["title.identity"]
    assert extract_title_flags("I Tried Cold Plunges for 30 Days")["title.first_person"]
    assert extract_title_flags("The Sleep System That Actually Works")["title.specific_system"]


def test_brief_is_on_brand_across_niches():
    survivors = [
        PatternClaim(feature="title.identity", statement="s", platform="youtube",
                     lift=1.4, support=6, population=12, robustness=0.8, survived=True),
        PatternClaim(feature="thumb.clean", statement="s", platform="youtube",
                     lift=1.3, support=6, population=12, robustness=0.7, survived=True),
    ]
    for niche in ["fitness", "finance", "philosophy", "gaming", "branding"]:
        brief = generate_brief("getting started", survivors, niche)
        assert len(brief.titles) == 3
        assert brief.anti_pattern_flags == []
        assert brief.brand_alignment >= 0.5
