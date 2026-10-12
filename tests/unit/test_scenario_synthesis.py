from __future__ import annotations

import pandas as pd
import pytest

from kerdata.scenario import KNOWN_FIRST, TARGET_NAME, pick_target, stage
from kerdata.synthesis import (
    ATTACK_COLUMNS,
    control_match_share,
    correlation_gap,
    exact_match_share,
    synthesize,
)
from kerdata.uniqueness import candidates

QIS = list(ATTACK_COLUMNS)


def test_target_is_ambiguous_then_unique(colony: pd.DataFrame) -> None:
    target = pick_target(colony, min_suspects=2)
    first_three = {k: target.known[k] for k in KNOWN_FIRST}
    assert len(candidates(colony, first_three)) == target.suspects_after_three >= 2
    assert candidates(colony, target.known).index.tolist() == [target.index]
    assert target.known["mark"] != "aucun"
    assert colony.loc[target.index, "sex"] == "F"


def test_pick_target_fails_cleanly(colony: pd.DataFrame) -> None:
    with pytest.raises(LookupError):
        pick_target(colony, min_suspects=10_000)


def test_only_the_target_is_called_gwen(colony: pd.DataFrame) -> None:
    target = pick_target(colony, min_suspects=2)
    staged = stage(colony, target)
    assert staged.index[staged["name"] == TARGET_NAME].tolist() == [target.index]


def test_synthetic_keeps_sex_profiles(colony: pd.DataFrame) -> None:
    synth = synthesize(colony, [*QIS, "weight_kg"], seed=3)
    assert len(synth) == len(colony)
    real = colony.groupby("sex")["weight_kg"].median()
    fake = synth.groupby("sex")["weight_kg"].median()
    assert (fake / real).between(0.85, 1.15).all()


def test_synthetic_lookalikes_are_coincidences(colony: pd.DataFrame) -> None:
    """Les sosies du synthétique ne sont pas plus fréquents que ceux d'une colonie témoin."""
    synth = synthesize(colony, QIS, seed=3)
    assert exact_match_share(colony, synth, QIS) <= 1.3 * control_match_share(colony, QIS, 8)


def test_synthetic_breaks_age_weight_link(colony: pd.DataFrame) -> None:
    synth = synthesize(colony, ["sex", "age", "weight_kg"], seed=3)
    assert correlation_gap(colony, synth, "age", "weight_kg") > 0.3


def test_attack_columns_exist(colony: pd.DataFrame) -> None:
    assert set(ATTACK_COLUMNS) <= set(colony.columns)
