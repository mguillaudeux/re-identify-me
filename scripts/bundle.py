"""Assemble l'appli web en un seul fichier HTML autonome (CSS, JS, données et images inline).

Usage : ``uv run python scripts/bundle.py [--fragment] [-o dist/re-identify-me.html]``
``--fragment`` produit seulement le contenu de <body> (pour un hébergeur qui ajoute
lui-même le squelette HTML).
"""

from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
MIME = {".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png"}


def _inline_images(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        path = WEB / match.group(1)
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src="data:{MIME[path.suffix]};base64,{data}"'

    return re.sub(r'src="(assets/[^"]+)"', repl, html)


def bundle(fragment: bool = False) -> str:
    index = (WEB / "index.html").read_text(encoding="utf-8")
    body = index.split("<!--BODY-START-->")[1].split("<!--BODY-END-->")[0]
    head = re.search(r"<title>.*?</title>", index, re.S)
    fonts = re.findall(r'<link rel="(?:preconnect|stylesheet)" href="https://fonts[^>]*>', index)
    css = (WEB / "style.css").read_text(encoding="utf-8")
    js = (WEB / "app.js").read_text(encoding="utf-8")
    data = (WEB / "data" / "kerdata.json").read_text(encoding="utf-8")
    parts = [
        head.group(0) if head else "",
        *fonts,
        f"<style>\n{css}</style>",
        _inline_images(body),
        f"<script>window.KERDATA = {data};</script>",
        f"<script>\n{js}</script>",
    ]
    inner = "\n".join(parts)
    if fragment:
        return inner
    return (
        '<!doctype html>\n<html lang="fr" data-lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f"</head>\n<body>\n{inner}\n</body>\n</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fragment", action="store_true")
    parser.add_argument("-o", "--out", type=Path, default=Path("dist/re-identify-me.html"))
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(bundle(args.fragment), encoding="utf-8")
    print(f"→ {args.out} ({args.out.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
