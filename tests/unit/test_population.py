from __future__ import annotations

import pandas as pd
import pytest

from kerdata.catalog import DARK_COATS, ZONES
from kerdata.population import COLUMNS, MAX_AGE, generate, month_label


def test_same_seed_same_colony() -> None:
    pd.testing.assert_frame_equal(generate(300, seed=1), generate(300, seed=1))


def test_different_seed_different_colony() -> None:
    assert not generate(300, seed=1).equals(generate(300, seed=2))


def test_size_and_columns(colony: pd.DataFrame) -> None:
    assert len(colony) == 1_500
    assert tuple(colony.columns) == COLUMNS


def test_rejects_empty_colony() -> None:
    with pytest.raises(ValueError):
        generate(0)


def test_pseudonyms_are_unique(colony: pd.DataFrame) -> None:
    assert colony["pseudo"].is_unique
    assert colony["pseudo"].str.fullmatch(r"KD-[0-9A-F]{5}").all()


def test_values_in_plausible_ranges(colony: pd.DataFrame) -> None:
    assert colony["age"].between(0, MAX_AGE).all()
    assert colony["birth_month"].between(1, 12).all()
    assert colony["weight_kg"].between(12, 450).all()
    assert colony["length_cm"].between(70, 300).all()
    assert set(colony["zone"]) <= set(ZONES)


def test_males_are_heavier(colony: pd.DataFrame) -> None:
    adults = colony[colony["age"] >= 6]
    mean = adults.groupby("sex")["weight_kg"].mean()
    assert mean["M"] > 1.3 * mean["F"]


def test_males_are_darker(colony: pd.DataFrame) -> None:
    dark = colony["coat"].isin(DARK_COATS).groupby(colony["sex"]).mean()
    assert dark["M"] > dark["F"]


def test_pups_are_lighter_than_adults(colony: pd.DataFrame) -> None:
    pups = colony.loc[colony["age"] == 0, "weight_kg"].mean()
    adults = colony.loc[colony["age"] >= 6, "weight_kg"].mean()
    assert pups < adults / 2


def test_pups_are_born_in_autumn(colony: pd.DataFrame) -> None:
    autumn = colony["birth_month"].isin([9, 10, 11]).mean()
    assert autumn > 0.5


def test_the_lighthouse_is_less_crowded_than_the_islet(colony: pd.DataFrame) -> None:
    counts = colony["zone"].value_counts()
    assert counts["ilot"] > counts["port"]


def test_month_label() -> None:
    assert month_label(1) == "janvier"
    assert month_label(12, "en") == "December"
