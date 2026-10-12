"""Un synthétiseur volontairement naïf, pour l'acte 3.

Méthode : on tire le sexe selon sa fréquence, puis chaque autre attribut
indépendamment *selon sa distribution chez les phoques de ce sexe*. On conserve donc
les profils mâles / femelles, mais on casse les liens fins entre attributs
(âge ↔ poids, âge ↔ cicatrices, etc.).

C'est un modèle d'école, choisi pour sa lisibilité : il montre à la fois l'intérêt
(aucune ligne ne correspond à un vrai phoque) et la limite (certaines corrélations
disparaissent) des données synthétiques. Ce n'est pas un générateur de production.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from kerdata.population import generate

GROUP = "sex"

# Ce qu'un attaquant peut raisonnablement connaître d'un animal (acte 3).
ATTACK_COLUMNS: tuple[str, ...] = ("zone", "sex", "age", "birth_month", "coat", "mark")


def synthesize(
    df: pd.DataFrame, columns: Sequence[str], n: int | None = None, seed: int = 0
) -> pd.DataFrame:
    """Produit ``n`` phoques synthétiques à partir des colonnes de ``df``."""
    rng = np.random.default_rng(seed)
    size = len(df) if n is None else n
    shares = df[GROUP].value_counts(normalize=True)
    groups = rng.choice(shares.index.to_numpy(), size=size, p=shares.to_numpy())

    out = pd.DataFrame({GROUP: groups})
    others = [c for c in columns if c != GROUP]
    for key, block in df.groupby(GROUP, observed=True):
        where = np.flatnonzero(groups == key)
        for column in others:
            values = block[column].to_numpy()
            out.loc[where, column] = values[rng.integers(0, len(values), size=len(where))]
    for column in others:
        out[column] = out[column].astype(df[column].dtype)
    return out.loc[:, [GROUP, *others]]


def exact_match_share(real: pd.DataFrame, synthetic: pd.DataFrame, columns: Sequence[str]) -> float:
    """Part des lignes synthétiques qui recopient *exactement* une ligne réelle unique.

    Seules les lignes réelles uniques comptent : une copie d'un profil partagé par
    dix animaux ne trahit personne.

    Attention à l'interprétation : des sosies apparaissent aussi *par hasard*. Il faut
    donc comparer ce chiffre à celui d'une île témoin, indépendante, tirée de la même
    loi. Un synthétique qui ne fait pas mieux que le hasard n'a rien recopié.
    """
    cols = list(columns)
    counts = real.groupby(cols, observed=True).size()
    unique_profiles = counts[counts == 1].reset_index()[cols]
    if synthetic.empty or unique_profiles.empty:
        return 0.0
    merged = synthetic[cols].merge(unique_profiles, on=cols, how="inner")
    return len(merged) / len(synthetic)


def correlation_gap(real: pd.DataFrame, synthetic: pd.DataFrame, x: str, y: str) -> float:
    """Écart de corrélation (Spearman, moyenné par sexe) entre réel et synthétique."""

    def _mean_corr(frame: pd.DataFrame) -> float:
        corrs = [
            block[x].rank().corr(block[y].rank())  # Spearman sans SciPy
            for _, block in frame.groupby(GROUP, observed=True)
            if len(block) > 2
        ]
        return float(np.nanmean(corrs))

    return abs(_mean_corr(real) - _mean_corr(synthetic))


def control_match_share(real: pd.DataFrame, columns: Sequence[str], seed: int) -> float:
    """Taux de sosies « par hasard » : celui d'une île témoin indépendante."""
    return exact_match_share(real, generate(len(real), seed), columns)
