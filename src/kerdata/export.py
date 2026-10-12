"""Export de l'île au format JSON colonne, consommé par l'application web.

Les colonnes catégorielles sont codées en entiers ; les dictionnaires bilingues
permettent à l'interface d'afficher les libellés en français ou en anglais.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from kerdata.catalog import (
    COATS,
    MARKS,
    MONTHS,
    QUASI_IDENTIFIERS,
    SECRETS,
    SEXES,
    SIDES,
    TEMPERS,
    ZONES,
    Label,
)
from kerdata.scenario import Target
from kerdata.synthesis import ATTACK_COLUMNS, control_match_share
from kerdata.uniqueness import uniqueness_curve

SCHEMA_VERSION = 1


def _labels(mapping: dict[str, Label]) -> list[dict[str, str]]:
    return [{"key": k, "fr": v.fr, "en": v.en} for k, v in mapping.items()]


def dictionaries() -> dict[str, list[dict[str, str]]]:
    """Dictionnaires bilingues, dans l'ordre des codes."""
    return {
        "zone": _labels({k: lab for k, (lab, _) in ZONES.items()}),
        "coat": _labels({k: lab for k, (lab, _, _) in COATS.items()}),
        "sex": _labels(SEXES),
        "mark": _labels({k: lab for k, (lab, _) in MARKS.items()}),
        "temper": _labels(TEMPERS),
        "birth_month": [{"key": str(i + 1), "fr": m.fr, "en": m.en} for i, m in enumerate(MONTHS)],
        "secret": [{"key": str(i), "fr": s.fr, "en": s.en} for i, s in enumerate(SECRETS)],
    }


CATEGORICAL = ("zone", "sex", "coat", "mark", "temper")


def to_payload(df: pd.DataFrame, seed: int, target: Target | None = None) -> dict[str, Any]:
    """Construit la structure JSON (codes + dictionnaires + courbe d'unicité)."""
    dicts = dictionaries()
    columns: dict[str, list[Any]] = {}
    for column in df.columns:
        if column in CATEGORICAL:
            index = {entry["key"]: i for i, entry in enumerate(dicts[column])}
            columns[column] = [index[v] for v in df[column]]
        elif column == "birth_month":
            columns[column] = [int(v) - 1 for v in df[column]]
        else:
            columns[column] = df[column].tolist()

    order = [a.key for a in QUASI_IDENTIFIERS]
    curve = [
        {
            "column": p.column,
            "unique": round(p.unique_share, 4),
            "mean_class": round(p.mean_class_size, 2),
        }
        for p in uniqueness_curve(df, order)
    ]
    questions = [
        {
            "key": a.key,
            "fr": a.label.fr,
            "en": a.label.en,
            "ask_fr": a.question.fr,
            "ask_en": a.question.en,
            "human_fr": a.human.fr,
            "human_en": a.human.en,
        }
        for a in QUASI_IDENTIFIERS
    ]
    return {
        "schema": SCHEMA_VERSION,
        "meta": {"n": len(df), "seed": seed, "island": "Kerdata"},
        "target": None
        if target is None
        else {
            "row": int(np.flatnonzero(df.index == target.index)[0]),
            "known": target.known,
            "suspects_after_three": target.suspects_after_three,
        },
        "dict": dicts,
        "questions": questions,
        "columns": columns,
        "curve": curve,
        "attack_columns": list(ATTACK_COLUMNS),
        "sides": SIDES,
        "control_match": round(control_match_share(df, ATTACK_COLUMNS, seed + 1), 4),
    }


def write(df: pd.DataFrame, path: Path, seed: int, target: Target | None = None) -> Path:
    """Écrit le JSON (compact) et renvoie son chemin."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = to_payload(df, seed, target)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    return path


def read(path: Path) -> pd.DataFrame:
    """Relit un export et reconstruit le DataFrame avec les clés d'origine."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    dicts = payload["dict"]
    data: dict[str, list[Any]] = {}
    for column, values in payload["columns"].items():
        if column in CATEGORICAL:
            keys = [entry["key"] for entry in dicts[column]]
            data[column] = [keys[v] for v in values]
        elif column == "birth_month":
            data[column] = [v + 1 for v in values]
        else:
            data[column] = values
    return pd.DataFrame(data)
