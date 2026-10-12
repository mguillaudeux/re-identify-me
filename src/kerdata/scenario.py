"""Scénario de l'acte II : le registre « anonyme » résiste-t-il à quatre indices publics ?

Gwen est la chouchoute du soigneur, qui poste régulièrement des photos d'elle sur les
réseaux sociaux. On y voit où elle se repose, la couleur de son pelage et son signe
particulier ; une légende d'anniversaire donne son âge. Ces informations viennent d'une
source extérieure et publique ; la question est de savoir si elles suffisent à
retrouver sa ligne dans le registre pseudonymisé.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from kerdata.uniqueness import class_sizes

TARGET_NAME = "Gwen"
KNOWN_FIRST: tuple[str, ...] = ("zone", "coat", "mark")
KNOWN_LAST = "age"


@dataclass(frozen=True)
class Target:
    """La cible et ce que l'enquêteur sait d'elle."""

    index: int
    known: dict[str, object]
    suspects_after_three: int


def pick_target(df: pd.DataFrame, min_suspects: int = 3) -> Target:
    """Choisit une cible encore ambiguë après 3 indices mais unique avec le 4ᵉ.

    Lève ``LookupError`` si la colonie ne contient pas de candidate convenable.
    """
    first = class_sizes(df, KNOWN_FIRST)
    full = class_sizes(df, (*KNOWN_FIRST, KNOWN_LAST))
    ok = (
        (df["sex"] == "F")  # Gwen est une femelle
        & (df["mark"] != "aucun")
        & (df["age"] > 0)
        & (first >= min_suspects)
        & (full == 1)
    )
    pool = df.index[ok]
    if len(pool) == 0:
        raise LookupError("Aucune cible convenable : change de graine ou de taille de colonie.")
    # La cible la plus « difficile » : celle qui a le plus de sosies après 3 indices.
    index = int(first.loc[pool].sort_values(ascending=False, kind="stable").index[0])
    row = df.loc[index]
    known = {
        c: row[c].item() if hasattr(row[c], "item") else row[c] for c in (*KNOWN_FIRST, KNOWN_LAST)
    }
    return Target(index=index, known=known, suspects_after_three=int(first.loc[index]))


def stage(df: pd.DataFrame, target: Target) -> pd.DataFrame:
    """Renomme la cible « Gwen » (et personne d'autre) pour la mise en scène."""
    out = df.copy()
    others = (out["name"] == TARGET_NAME) & (out.index != target.index)
    out.loc[others, "name"] = "Gwenaëlle"
    out.loc[target.index, "name"] = TARGET_NAME
    return out
