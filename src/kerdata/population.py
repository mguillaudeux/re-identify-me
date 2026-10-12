"""Génération de la colonie synthétique de phoques de Kerdata.

Chaque ligne est un phoque recensé par le soigneur. Les attributs sont corrélés
(les mâles sont plus lourds et plus foncés, les jeunes plus petits, les vieux
phoques ont plus de cicatrices), comme dans un vrai jeu de données : c'est
précisément ce qui rend la ré-identification possible.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from kerdata.catalog import COATS, MARKS, MONTHS, NAMES, SECRETS, TEMPERS, ZONES

DEFAULT_SIZE = 2_000
DEFAULT_SEED = 29  # le Finistère, évidemment
MAX_AGE = 30

COLUMNS: tuple[str, ...] = (
    "pseudo",
    "name",
    "zone",
    "sex",
    "age",
    "birth_month",
    "coat",
    "mark",
    "temper",
    "weight_kg",
    "length_cm",
    "secret",
)

# (poids adulte moyen en kg, écart-type, longueur adulte moyenne en cm, écart-type)
_ADULT: dict[str, tuple[float, float, float, float]] = {
    "F": (155.0, 25.0, 185.0, 12.0),
    "M": (240.0, 40.0, 215.0, 14.0),
}
_BIRTH_PEAK = 10  # les petits naissent surtout en automne


def _month_weights(peak: int) -> np.ndarray:
    """Distribution circulaire des mois de naissance autour d'un pic (1-12)."""
    months = np.arange(1, 13)
    distance = np.minimum(np.abs(months - peak), 12 - np.abs(months - peak))
    weights = np.exp(-(distance**2) / 5.0) + 0.06
    return np.asarray(weights / weights.sum())


def _weights(values: list[float]) -> np.ndarray:
    w = np.asarray(values, dtype=float)
    return np.asarray(w / w.sum())


def _growth(ages: np.ndarray) -> np.ndarray:
    """Facteur de croissance : un petit fait ~30 % du poids adulte, adulte vers 5 ans."""
    return np.asarray(0.3 + 0.7 * (1 - np.exp(-(ages + 0.3) / 2.0)))


def _pseudonyms(rng: np.random.Generator, n: int) -> list[str]:
    """Pseudonymes du registre : uniques, sans lien avec le phoque."""
    codes = rng.choice(16**5, size=n, replace=False)
    return [f"KD-{int(c):05X}" for c in codes]


def generate(n: int = DEFAULT_SIZE, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Recense ``n`` phoques de Kerdata. Même graine ⇒ même colonie."""
    if n <= 0:
        raise ValueError("Il faut au moins un phoque dans la colonie.")
    rng = np.random.default_rng(seed)

    sex = rng.choice(np.array(["F", "M"]), size=n, p=[0.55, 0.45])
    age = np.minimum(rng.geometric(0.12, size=n) - 1, MAX_AGE)
    zone = rng.choice(np.array(list(ZONES)), size=n, p=_weights([w for _, w in ZONES.values()]))
    month = rng.choice(np.arange(1, 13), size=n, p=_month_weights(_BIRTH_PEAK))

    coat_keys = np.array(list(COATS))
    coat = np.where(
        sex == "F",
        rng.choice(coat_keys, size=n, p=_weights([f for _, f, _ in COATS.values()])),
        rng.choice(coat_keys, size=n, p=_weights([m for _, _, m in COATS.values()])),
    )

    mark_keys = np.array(list(MARKS))
    mark_p = np.array([p for _, p in MARKS.values()])
    mark = rng.choice(mark_keys, size=n, p=mark_p / mark_p.sum())
    # Les vieux phoques accumulent les signes particuliers.
    remark = rng.choice(mark_keys[1:], size=n, p=mark_p[1:] / mark_p[1:].sum())
    old = (age >= 10) & (mark == "aucun") & (rng.random(n) < 0.35)
    mark = np.where(old, remark, mark)

    adult = np.array([_ADULT[s] for s in sex])
    growth = _growth(age)
    weight = rng.normal(adult[:, 0], adult[:, 1]) * growth
    length = rng.normal(adult[:, 2], adult[:, 3]) * np.sqrt(growth)

    df = pd.DataFrame(
        {
            "pseudo": _pseudonyms(rng, n),
            "name": rng.choice(np.array(NAMES), size=n),
            "zone": zone,
            "sex": sex,
            "age": age.astype(int),
            "birth_month": month.astype(int),
            "coat": coat,
            "mark": mark,
            "temper": rng.choice(np.array(list(TEMPERS)), size=n),
            "weight_kg": np.round(np.clip(weight, 12, None)).astype(int),
            "length_cm": np.round(np.clip(length, 70, None)).astype(int),
            "secret": rng.integers(0, len(SECRETS), size=n),
        }
    )
    return df.loc[:, list(COLUMNS)]


def month_label(month: int, lang: str = "fr") -> str:
    """Libellé d'un mois (1-12)."""
    label = MONTHS[month - 1]
    return label.fr if lang == "fr" else label.en
