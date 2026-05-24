"""Fuzzy-logic engine tests: membership funcs, monotonicity, defuzzification."""
from datetime import datetime, timedelta, timezone

from brand_supertool.intelligence import fuzzy
from brand_supertool.models import Video


def test_membership_partition_of_unity_at_extremes():
    assert fuzzy.mf_low(0.0) == 1.0
    assert fuzzy.mf_high(1.0) == 1.0
    assert fuzzy.mf_med(0.5) == 1.0


def test_membership_bounded_0_1():
    for x in [i / 20 for i in range(21)]:
        for mf in (fuzzy.mf_low, fuzzy.mf_med, fuzzy.mf_high):
            assert 0.0 <= mf(x) <= 1.0


def test_infer_monotonic_in_engagement():
    """Higher signals must never lower the crisp score."""
    prev = -1
    for x in [0.0, 0.25, 0.5, 0.75, 1.0]:
        s = fuzzy.infer(x, x, x, x)
        assert s >= prev - 1e-9, f"score dropped at {x}"
        prev = s


def test_infer_bounds():
    lo = fuzzy.infer(0, 0, 0, 0)
    hi = fuzzy.infer(1, 1, 1, 1)
    assert 0 <= lo < hi <= 100


def test_rank_norm_basic():
    assert fuzzy._rank_norm([10, 20, 30]) == [0.0, 0.5, 1.0]
    assert fuzzy._rank_norm([5]) == [1.0]
    assert fuzzy._rank_norm([]) == []


def _vid(i, views, likes, comments, days=7):
    now = datetime.now(timezone.utc)
    return Video(id=str(i), creator="c", platform="youtube", title=f"t{i}",
                 url="", published_at=now - timedelta(days=days),
                 views=views, likes=likes, comments=comments)


def test_score_corpus_orders_winners_high():
    vids = [
        _vid(1, 500000, 60000, 4000),   # strong everything
        _vid(2, 5000, 50, 2),           # weak everything
        _vid(3, 80000, 6000, 300),      # middling
    ]
    fuzzy.score_corpus(vids)
    # sorted descending; strongest first, weakest last
    assert vids[0].id == "1"
    assert vids[-1].id == "2"
    assert vids[0].performance_score > vids[-1].performance_score
    for v in vids:
        assert 0 <= v.performance_score <= 100
        assert 0 <= v.winner_membership <= 1
