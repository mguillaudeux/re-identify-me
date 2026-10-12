"""Ligne de commande : ``kerdata generate`` et ``kerdata report``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from kerdata import export
from kerdata.catalog import QUASI_IDENTIFIERS
from kerdata.population import DEFAULT_SEED, DEFAULT_SIZE, generate
from kerdata.scenario import pick_target, stage
from kerdata.uniqueness import uniqueness_curve

DEFAULT_OUT = Path("web/data/kerdata.json")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kerdata", description="Recensement de Kerdata.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_ in (
        ("generate", "génère l'île et l'exporte en JSON"),
        ("report", "affiche la courbe d'unicité"),
    ):
        cmd = sub.add_parser(name, help=help_)
        cmd.add_argument("-n", "--size", type=int, default=DEFAULT_SIZE)
        cmd.add_argument("-s", "--seed", type=int, default=DEFAULT_SEED)
    sub.choices["generate"].add_argument("-o", "--out", type=Path, default=DEFAULT_OUT)
    return parser


def report(size: int, seed: int) -> str:
    """Courbe d'unicité au format texte."""
    df = generate(size, seed)
    lines = [f"Kerdata : {len(df)} phoques (graine {seed})", ""]
    order = [a.key for a in QUASI_IDENTIFIERS]
    labels = {a.key: a.label.fr for a in QUASI_IDENTIFIERS}
    for p in uniqueness_curve(df, order):
        bar = "█" * round(p.unique_share * 40)
        lines.append(f"+ {labels[p.column]:<20} {p.unique_share:6.1%}  {bar}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "generate":
        df = generate(args.size, args.seed)
        target = pick_target(df)
        path = export.write(stage(df, target), args.out, args.seed, target)
        print(f"{len(df)} phoques recensés → {path}")
    else:
        print(report(args.size, args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
