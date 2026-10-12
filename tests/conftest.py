"""Fixtures partagées."""

from __future__ import annotations

import pandas as pd
import pytest

from kerdata import generate


@pytest.fixture(scope="session")
def colony() -> pd.DataFrame:
    """Une petite colonie déterministe, réutilisée par tous les tests."""
    return generate(n=1_500, seed=7)


@pytest.fixture
def toy() -> pd.DataFrame:
    """Cinq phoques dont on connaît les classes d'équivalence à la main."""
    return pd.DataFrame(
        {
            "zone": ["ilot", "ilot", "ilot", "port", "port"],
            "coat": ["clair", "clair", "brun", "fonce", "fonce"],
            "age": [3, 4, 3, 10, 10],
            "birth_month": [1, 2, 7, 10, 11],
        }
    )
