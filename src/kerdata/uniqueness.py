"""Mesures d'unicité et de k-anonymat, et transformations de « brouillage ».

Vocabulaire :
- une *classe d'équivalence* regroupe les lignes qui partagent exactement les mêmes
  valeurs sur un ensemble de quasi-identifiants ;
- une ligne est *unique* si sa classe ne contient qu'elle : quiconque connaît ces
  attributs la retrouve à coup sûr ;
- un jeu est *k-anonyme* si toutes ses classes contiennent au moins ``k`` lignes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from kerdata.catalog import DARK_COATS, SIDES

Transform = Callable[[pd.Series], pd.Series]


@dataclass(frozen=True)
class CurvePoint:
    """Un point de la courbe d'unicité : après avoir ajouté ``column``."""

    column: str
    n_columns: int
    unique_share: float
    mean_class_size: float
    k: int


def class_sizes(df: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Taille de la classe d'équivalence de chaque ligne."""
    cols = list(columns)
    if not cols:
        return pd.Series(len(df), index=df.index, dtype="int64")
    sizes = df.groupby(cols, dropna=False, observed=True)[cols[0]].transform("size")
    return sizes.astype("int64")


def unique_share(df: pd.DataFrame, columns: Sequence[str]) -> float:
    """Part des lignes uniques (ré-identifiables avec certitude)."""
    if df.empty:
        return 0.0
    return float((class_sizes(df, columns) == 1).mean())


def k_anonymity(df: pd.DataFrame, columns: Sequence[str]) -> int:
    """Le ``k`` du jeu : taille de la plus petite classe d'équivalence."""
    if df.empty:
        return 0
    return int(class_sizes(df, columns).min())


def uniqueness_curve(df: pd.DataFrame, order: Sequence[str]) -> list[CurvePoint]:
    """Ajoute les colonnes une à une et mesure l'unicité à chaque étape."""
    points: list[CurvePoint] = []
    for i, column in enumerate(order, start=1):
        sizes = class_sizes(df, order[:i])
        points.append(
            CurvePoint(
                column=column,
                n_columns=i,
                unique_share=float((sizes == 1).mean()),
                mean_class_size=float(sizes.mean()),
                k=int(sizes.min()),
            )
        )
    return points


def candidates(df: pd.DataFrame, known: Mapping[str, object]) -> pd.DataFrame:
    """Les lignes compatibles avec ce que l'attaquant sait de sa cible."""
    mask = np.ones(len(df), dtype=bool)
    for column, value in known.items():
        mask &= (df[column] == value).to_numpy()
    return df.loc[mask]


# --- Brouillage : généralisation, suppression ------------------------------------------


def age_band(width: int) -> Transform:
    """Regroupe l'âge par tranches (« 0-2 ans », « 3-5 ans »…)."""
    if width < 1:
        raise ValueError("La largeur d'une tranche doit être positive.")

    def _apply(s: pd.Series) -> pd.Series:
        low = (s // width) * width
        return low.astype(str) + "-" + (low + width - 1).astype(str)

    return _apply


SEASONS: dict[int, str] = {
    12: "hiver",
    1: "hiver",
    2: "hiver",
    3: "printemps",
    4: "printemps",
    5: "printemps",
    6: "ete",
    7: "ete",
    8: "ete",
    9: "automne",
    10: "automne",
    11: "automne",
}


def month_to_season(s: pd.Series) -> pd.Series:
    """Mois de naissance → saison."""
    return s.map(SEASONS)


def zone_to_side(s: pd.Series) -> pd.Series:
    """Lieu précis → côté de l'île (comme passer de l'adresse au département)."""
    return s.map(SIDES)


def coat_to_shade(s: pd.Series) -> pd.Series:
    """Pelage précis → clair / foncé."""
    return s.map(lambda c: "fonce" if c in DARK_COATS else "clair")


def present_or_not(s: pd.Series) -> pd.Series:
    """Signe particulier → « oui / non »."""
    return (s != "aucun").map({True: "oui", False: "non"})


def generalize(df: pd.DataFrame, rules: Mapping[str, Transform]) -> pd.DataFrame:
    """Applique une règle de généralisation par colonne (les autres restent intactes)."""
    out = df.copy()
    for column, rule in rules.items():
        out[column] = rule(out[column])
    return out


def suppress_columns(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Supprime des colonnes entières."""
    return df.drop(columns=list(columns))


def suppress_small_classes(
    df: pd.DataFrame, columns: Sequence[str], k: int
) -> tuple[pd.DataFrame, int]:
    """Retire les lignes dont la classe compte moins de ``k`` membres.

    Renvoie le jeu filtré et le nombre de lignes sacrifiées : c'est le coût visible
    du k-anonymat.
    """
    sizes = class_sizes(df, columns)
    keep = sizes >= k
    return df.loc[keep].copy(), int((~keep).sum())


# --- Coût en utilité -----------------------------------------------------------------


def distinct_loss(
    original: pd.DataFrame, transformed: pd.DataFrame, columns: Sequence[str]
) -> float:
    """Perte moyenne de précision : 1 - (#valeurs distinctes après / avant), colonne
    supprimée = perte totale."""
    losses: list[float] = []
    for column in columns:
        before = original[column].nunique()
        after = transformed[column].nunique() if column in transformed else 0
        losses.append(1.0 - after / before if before else 0.0)
    return float(np.mean(losses)) if losses else 0.0


def rows_kept(original: pd.DataFrame, transformed: pd.DataFrame) -> float:
    """Part des lignes conservées."""
    return len(transformed) / len(original) if len(original) else 0.0
