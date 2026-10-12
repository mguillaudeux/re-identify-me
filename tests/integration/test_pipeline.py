"""De bout en bout : génération → export JSON → relecture → courbe."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from kerdata import export
from kerdata.catalog import QUASI_IDENTIFIERS
from kerdata.cli import main, report
from kerdata.population import generate
from kerdata.scenario import pick_target, stage
from kerdata.uniqueness import (
    age_band,
    coat_to_shade,
    generalize,
    k_anonymity,
    month_to_season,
    suppress_small_classes,
    unique_share,
)

pytestmark = pytest.mark.integration
ORDER = [a.key for a in QUASI_IDENTIFIERS]


@pytest.fixture(scope="module")
def full_colony() -> pd.DataFrame:
    return generate()


def test_export_roundtrip(tmp_path: Path) -> None:
    df = generate(800, seed=11)
    target = pick_target(df, min_suspects=2)
    staged = stage(df, target)
    path = export.write(staged, tmp_path / "kerdata.json", seed=11, target=target)

    back = export.read(path)
    pd.testing.assert_frame_equal(back, staged.reset_index(drop=True), check_dtype=False)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["meta"] == {"n": 800, "seed": 11, "island": "Kerdata"}
    assert back.loc[payload["target"]["row"], "name"] == "Gwen"
    assert [q["key"] for q in payload["questions"]] == ORDER
    assert 0 <= payload["control_match"] < 1


def test_the_game_works(full_colony: pd.DataFrame) -> None:
    """La promesse pédagogique : pas d'identifiant direct, et pourtant…"""
    assert unique_share(full_colony, ORDER[:2]) < 0.01  # lieu + sexe : la foule
    assert 0.2 < unique_share(full_colony, ORDER[:4]) < 0.6  # + âge, mois : ça se gâte
    assert unique_share(full_colony, ORDER) > 0.99  # tout : chacun est unique


def test_scrambling_restores_crowds(full_colony: pd.DataFrame) -> None:
    qis = ["zone", "sex", "age", "birth_month", "coat"]
    coarse = generalize(
        full_colony, {"age": age_band(5), "birth_month": month_to_season, "coat": coat_to_shade}
    )
    assert unique_share(coarse, qis) < unique_share(full_colony, qis) / 4
    kept, dropped = suppress_small_classes(coarse, qis, k=3)
    assert k_anonymity(kept, qis) >= 3
    assert 0 < dropped < len(full_colony) * 0.3  # le prix de la protection


def test_cli_generate_and_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "colony.json"
    assert main(["generate", "-n", "1500", "-s", "29", "-o", str(out)]) == 0
    assert out.exists()
    assert "1500 phoques" in capsys.readouterr().out
    assert "Taille" in report(1500, 29)
