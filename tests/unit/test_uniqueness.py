from __future__ import annotations

import pandas as pd
import pytest

from kerdata.uniqueness import (
    age_band,
    candidates,
    class_sizes,
    coat_to_shade,
    distinct_loss,
    generalize,
    k_anonymity,
    month_to_season,
    present_or_not,
    rows_kept,
    suppress_columns,
    suppress_small_classes,
    unique_share,
    uniqueness_curve,
    zone_to_side,
)


def test_class_sizes_by_hand(toy: pd.DataFrame) -> None:
    assert class_sizes(toy, ["zone"]).tolist() == [3, 3, 3, 2, 2]
    assert class_sizes(toy, ["zone", "coat"]).tolist() == [2, 2, 1, 2, 2]
    assert class_sizes(toy, []).tolist() == [5] * 5


def test_unique_share_and_k(toy: pd.DataFrame) -> None:
    assert unique_share(toy, ["zone"]) == 0.0
    assert unique_share(toy, ["zone", "coat"]) == pytest.approx(0.2)
    assert unique_share(toy, ["zone", "coat", "age"]) == pytest.approx(0.6)
    assert k_anonymity(toy, ["zone"]) == 2
    assert k_anonymity(toy, ["zone", "coat", "age"]) == 1


def test_empty_frame() -> None:
    empty = pd.DataFrame({"a": []})
    assert unique_share(empty, ["a"]) == 0.0
    assert k_anonymity(empty, ["a"]) == 0


def test_curve_is_monotonic(toy: pd.DataFrame) -> None:
    curve = uniqueness_curve(toy, ["zone", "coat", "age", "birth_month"])
    shares = [p.unique_share for p in curve]
    assert shares == sorted(shares)
    assert shares[-1] == 1.0
    assert [p.n_columns for p in curve] == [1, 2, 3, 4]


def test_candidates(toy: pd.DataFrame) -> None:
    assert len(candidates(toy, {"zone": "ilot"})) == 3
    assert len(candidates(toy, {"zone": "ilot", "coat": "clair", "age": 4})) == 1


def test_age_band() -> None:
    assert age_band(3)(pd.Series([0, 2, 3, 7])).tolist() == ["0-2", "0-2", "3-5", "6-8"]
    with pytest.raises(ValueError):
        age_band(0)


def test_simple_generalizations() -> None:
    assert month_to_season(pd.Series([1, 4, 7, 10])).tolist() == [
        "hiver",
        "printemps",
        "ete",
        "automne",
    ]
    assert zone_to_side(pd.Series(["phare", "port"])).tolist() == ["large", "abri"]
    assert coat_to_shade(pd.Series(["brun", "tachete"])).tolist() == ["fonce", "clair"]
    assert present_or_not(pd.Series(["aucun", "tache"])).tolist() == ["non", "oui"]


def test_generalization_never_decreases_k(toy: pd.DataFrame) -> None:
    cols = ["zone", "coat", "age", "birth_month"]
    coarse = generalize(
        toy,
        {
            "age": age_band(5),
            "birth_month": month_to_season,
            "zone": zone_to_side,
            "coat": coat_to_shade,
        },
    )
    assert k_anonymity(coarse, cols) >= k_anonymity(toy, cols)
    assert toy["zone"].tolist()[0] == "ilot"  # l'original n'est pas modifié


def test_suppress_small_classes(toy: pd.DataFrame) -> None:
    kept, dropped = suppress_small_classes(toy, ["zone", "coat"], k=2)
    assert dropped == 1
    assert k_anonymity(kept, ["zone", "coat"]) >= 2
    assert rows_kept(toy, kept) == pytest.approx(0.8)


def test_distinct_loss(toy: pd.DataFrame) -> None:
    assert distinct_loss(toy, toy, ["coat"]) == 0.0
    coarse = generalize(toy, {"coat": coat_to_shade})
    assert distinct_loss(toy, coarse, ["coat"]) == pytest.approx(1 - 2 / 3)
    assert distinct_loss(toy, suppress_columns(toy, ["coat"]), ["coat"]) == 1.0
