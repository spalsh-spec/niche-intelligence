"""Falsification eval tests — the firewall against noise."""
from datetime import datetime, timezone

from brand_supertool.intelligence import falsify
from brand_supertool.models import PatternClaim, Video


def _v(i, score, flag):
    v = Video(id=str(i), creator="c", platform="youtube", title=f"t{i}", url="",
              published_at=datetime.now(timezone.utc), views=1, likes=0, comments=0)
    v.performance_score = score
    v.feature_flags = {"f": flag}
    return v


def _claim(lift, support, population):
    return PatternClaim(feature="f", statement="s", platform="youtube",
                        support=support, population=population, lift=lift)


def test_clean_pattern_survives():
    # every F video wins, every non-F loses -> unfalsifiable
    vids = [_v(i, 90, True) for i in range(5)] + [_v(i + 5, 20, False) for i in range(5)]
    claim = _claim(lift=2.0, support=5, population=10)
    falsify.evaluate_claim(claim, vids, threshold=55)
    assert claim.falsification_ratio == 0.0
    assert claim.survived is True
    assert claim.verdict == "supported"


def test_noisy_pattern_is_falsified():
    # F videos are a coin flip; winning happens without F too
    vids = [_v(0, 90, True), _v(1, 20, True), _v(2, 85, True), _v(3, 25, True),
            _v(4, 92, False), _v(5, 88, False), _v(6, 30, False), _v(7, 22, False)]
    claim = _claim(lift=1.05, support=4, population=8)
    falsify.evaluate_claim(claim, vids, threshold=55)
    assert claim.counterexamples >= 1
    assert claim.contradictions >= 1
    assert claim.survived is False
    assert claim.verdict in ("weak", "falsified")


def test_low_support_cannot_survive():
    vids = [_v(0, 95, True), _v(1, 20, False), _v(2, 22, False)]
    claim = _claim(lift=3.0, support=1, population=3)  # support below MIN
    falsify.evaluate_claim(claim, vids, threshold=55)
    assert claim.survived is False


def test_evaluate_all_returns_sorted_survivors():
    vids = [_v(i, 90, True) for i in range(5)] + [_v(i + 5, 15, False) for i in range(5)]
    strong = _claim(2.0, 5, 10)
    survivors, evaluated = falsify.evaluate_all([strong], vids)
    assert len(evaluated) == 1
    assert all(s.robustness >= survivors[-1].robustness for s in survivors)
