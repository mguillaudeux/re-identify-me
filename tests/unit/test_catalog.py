from __future__ import annotations

import pytest

from kerdata.catalog import COATS, MARKS, NAMES, QUASI_IDENTIFIERS, SIDES, ZONES


def test_mark_probabilities_sum_to_one() -> None:
    assert sum(p for _, p in MARKS.values()) == pytest.approx(1.0)


def test_coat_weights_are_valid() -> None:
    assert sum(f for _, f, _ in COATS.values()) == pytest.approx(1.0)
    assert sum(m for _, _, m in COATS.values()) == pytest.approx(1.0)


def test_every_zone_has_a_side() -> None:
    assert set(SIDES) == set(ZONES)
    assert set(SIDES.values()) == {"large", "abri"}


def test_names_are_unique_and_include_gwen() -> None:
    assert len(NAMES) == len(set(NAMES))
    assert "Gwen" in NAMES


def test_every_question_is_bilingual_with_a_human_equivalent() -> None:
    keys = [a.key for a in QUASI_IDENTIFIERS]
    assert len(keys) == len(set(keys))
    for a in QUASI_IDENTIFIERS:
        for label in (a.label, a.question, a.human):
            assert label.fr and label.en
