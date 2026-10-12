# 🐙 Re-identify me!

> **Laisse-moi te montrer pourquoi retirer ton nom ne suffit pas à te rendre anonyme.** Un jeu d'enquête en trois actes sur une colonie de phoques (fictive).
> *Let me show you why removing your name isn't enough to make you anonymous. A three-act investigation game on a (fictional) seal colony.*

**▶ Jouer / Play : [mguillaudeux.github.io/re-identify-me](https://mguillaudeux.github.io/re-identify-me)**

<p align="center"><img src="web/assets/colonie.webp" width="560" alt="Croquis d'une colonie de phoques gris sur un îlot de Kerdata"></p>

## L'histoire

Sur l'île de Kerdata, le soigneur tient le registre de ses 2 000 phoques : lieu de repos, âge, pelage, signe particulier… et le petit secret de chacun. Pour le partager avec des scientifiques, il enlève les noms. « Comme ça, c'est anonyme. » L'inspecteur Poulpe a des doutes.

| Acte | Ce que tu fais | Question du CEPD |
| --- | --- | --- |
| I · **Devine qui** | Un Qui est-ce : une fiche = un phoque du registre, une question = un attribut. Puis la courbe d'unicité sur toute la colonie. | Individualisation |
| II · **Le test du registre** | Le registre pseudonymisé résiste-t-il à 4 informations publiées sur les réseaux sociaux à propos de Gwen, la chouchoute du soigneur ? | Corrélation |
| III · **À toi de protéger** | Une mission en 3 objectifs : plus aucun phoque unique, le secret de Gwen à l'abri, et 2 questions sur 3 des scientifiques encore justes. Bonus : les données synthétiques. | Inférence |
| **Le rapport** | L'inspecteur Poulpe rassemble tes preuves, une par question du CEPD (avis 05/2014). | |

Ça s'appuie sur [Rocher, Hendrickx & de Montjoye (2019)](https://www.nature.com/articles/s41467-019-10933-3) (99,98 % des Américains ré-identifiables avec 15 attributs démographiques) et sur les travaux de Latanya Sweeney (87 % uniques avec code postal + sexe + date de naissance).

Les phoques remplacent les humains exprès : un thème léger, sans risque de stéréotype, avec des attributs qui ont tous un équivalent humain (lieu de repos → adresse, mois de naissance → date de naissance, pelage → couleur des cheveux…).

## La courbe d'unicité de la colonie

```
$ just report
+ Lieu de repos          0.0%
+ Sexe                   0.0%
+ Âge                    4.5%  ██
+ Mois de naissance     37.9%  ███████████████
+ Pelage                72.2%  █████████████████████████████
+ Signe particulier     89.3%  ████████████████████████████████████
+ Caractère             97.7%  ███████████████████████████████████████
+ Poids                 99.9%  ████████████████████████████████████████
+ Taille               100.0%  ████████████████████████████████████████
```

## Sous le capot

```
src/kerdata/
  catalog.py      lieux, pelages, signes, secrets… (bilingue)
  population.py   génération de la colonie (attributs corrélés)
  uniqueness.py   classes d'équivalence, unicité, k-anonymat, généralisations
  synthesis.py    un synthétiseur volontairement naïf + colonie témoin
  scenario.py     le choix de Gwen pour l'acte II
  export.py       JSON colonne pour l'appli web
  cli.py          `kerdata generate` / `kerdata report`
tests/unit/         tests unitaires
tests/integration/  de bout en bout (génération → export → relecture)
notebooks/          le carnet d'exploration
web/                appli statique (HTML/CSS/JS sans dépendance)
```

Prérequis : [uv](https://docs.astral.sh/uv/) et [just](https://just.systems).

```bash
just setup              # uv sync
just report             # courbe d'unicité dans le terminal
just generate           # web/data/kerdata.json (taille et graine : just generate 3000 42)
just serve              # http://localhost:8000
just check              # ruff + mypy --strict + pytest (couverture)
just test-unit          # ou just test-integration
just bundle             # tout le jeu dans un seul fichier HTML (dist/)
just notebook           # JupyterLab
```

Tout est déterministe : même graine, même colonie.

## English

Kerdata's keeper wants to share the register of his 2,000 seals with scientists, so he removes the names. In three acts you recognise a seal from a few attributes (Guess Who), test whether the pseudonymised register survives four public clues about Gwen found on social media, then become the keeper and protect the register with generalisation, suppression, k-anonymity and synthetic data, while keeping it useful. Inspector Octo's final report maps your evidence to the three EDPB criteria (Opinion 05/2014). The whole site is bilingual (FR/EN toggle).

---

Kerdata et ses phoques sont fictifs. Aucune donnée réelle n'a été maltraitée. · MIT · [Morgan Guillaudeux](https://mguillaudeux.github.io)
