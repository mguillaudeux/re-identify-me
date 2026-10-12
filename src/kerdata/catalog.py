"""Catalogue de la colonie de phoques de Kerdata : lieux, pelages, signes, secrets.

Toutes les valeurs sont inventées mais restent plausibles. Aucune donnée réelle
n'est utilisée : la colonie est entièrement synthétique.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Label:
    """Libellé bilingue."""

    fr: str
    en: str


@dataclass(frozen=True)
class Attribute:
    """Un attribut du registre, vu comme une question du jeu."""

    key: str
    label: Label  # nom de la colonne
    question: Label  # la question posée sur le plateau
    human: Label  # l'équivalent chez les humains


# Les lieux de repos de la colonie, avec leur popularité relative.
ZONES: dict[str, tuple[Label, float]] = {
    "ilot": (Label("Îlot du Nord", "North islet"), 5.0),
    "roches": (Label("Roches plates", "Flat rocks"), 4.0),
    "greve": (Label("Grève de sable", "Sandy shore"), 3.0),
    "phare": (Label("Pointe du phare", "Lighthouse point"), 2.5),
    "chenal": (Label("Chenal", "Channel"), 2.0),
    "recif": (Label("Récif sud", "South reef"), 2.0),
    "anse": (Label("Anse des pêcheurs", "Fishermen's cove"), 1.5),
    "port": (Label("Petit port", "Little harbour"), 1.0),
}

# Côté de l'île de chaque lieu (pour la généralisation, comme code postal → département).
SIDES: dict[str, str] = {
    "ilot": "large",
    "phare": "large",
    "recif": "large",
    "chenal": "large",
    "roches": "abri",
    "greve": "abri",
    "anse": "abri",
    "port": "abri",
}

SEXES: dict[str, Label] = {
    "F": Label("Femelle", "Female"),
    "M": Label("Mâle", "Male"),
}

MONTHS: tuple[Label, ...] = (
    Label("janvier", "January"),
    Label("février", "February"),
    Label("mars", "March"),
    Label("avril", "April"),
    Label("mai", "May"),
    Label("juin", "June"),
    Label("juillet", "July"),
    Label("août", "August"),
    Label("septembre", "September"),
    Label("octobre", "October"),
    Label("novembre", "November"),
    Label("décembre", "December"),
)

# Pelage : (libellé, poids chez les femelles, poids chez les mâles). Les mâles sont plus foncés.
COATS: dict[str, tuple[Label, float, float]] = {
    "clair": (Label("Gris clair", "Light grey"), 0.30, 0.10),
    "argent": (Label("Gris argenté", "Silver grey"), 0.25, 0.15),
    "tachete": (Label("Gris tacheté", "Spotted grey"), 0.25, 0.25),
    "fonce": (Label("Gris foncé", "Dark grey"), 0.12, 0.30),
    "brun": (Label("Brun", "Brown"), 0.08, 0.20),
}
DARK_COATS: frozenset[str] = frozenset({"fonce", "brun"})

# Signe particulier : la plupart des phoques n'en ont pas.
MARKS: dict[str, tuple[Label, float]] = {
    "aucun": (Label("Aucun", "None"), 0.55),
    "cicatrice": (Label("Cicatrice", "Scar"), 0.10),
    "nageoire": (Label("Nageoire fendue", "Split flipper"), 0.07),
    "tache": (Label("Tache blanche", "White patch"), 0.08),
    "bague": (Label("Bague de suivi", "Tracking tag"), 0.06),
    "moustache": (Label("Moustaches courtes", "Short whiskers"), 0.06),
    "oeil": (Label("Œil voilé", "Cloudy eye"), 0.04),
    "boiterie": (Label("Rampe de travers", "Crooked crawl"), 0.04),
}

TEMPERS: dict[str, Label] = {
    "curieux": Label("Curieux", "Curious"),
    "timide": Label("Timide", "Shy"),
    "bagarreur": Label("Bagarreur", "Scrappy"),
    "paresseux": Label("Paresseux", "Lazy"),
    "joueur": Label("Joueur", "Playful"),
    "solitaire": Label("Solitaire", "Loner"),
}

# Le « petit secret » du registre du soigneur (l'information sensible de l'acte II).
SECRETS: tuple[Label, ...] = (
    Label("Ronfle très fort", "Snores loudly"),
    Label("A peur des goélands", "Is scared of gulls"),
    Label("Vole les lunettes des plongeurs", "Steals divers' goggles"),
    Label("Allergique aux algues", "Allergic to seaweed"),
    Label("Collectionne les bouchons de bouteille", "Collects bottle caps"),
    Label("Fait semblant de dormir pendant les recensements", "Fakes sleep during the census"),
    Label("Fouille en cachette la poubelle du port", "Secretly raids the harbour bin"),
    Label("Danse quand il pleut", "Dances in the rain"),
    Label("A déjà mordu le soigneur", "Once bit the keeper"),
    Label("Boude depuis trois semaines", "Has been sulking for three weeks"),
    Label("Est amoureux du phare", "Is in love with the lighthouse"),
    Label("Nage très mal (et le cache)", "Swims badly (and hides it)"),
    Label("Chante faux à l'aube", "Sings off-key at dawn"),
    Label("Se prend pour une pieuvre", "Thinks it is an octopus"),
    Label("Vient de perdre au poker", "Just lost at poker"),
    Label("A peur de l'eau froide", "Is afraid of cold water"),
)

# Prénoms bretons pour les fiches du plateau (affichage uniquement, jamais dans le registre).
NAMES: tuple[str, ...] = (
    "Gwen",
    "Yann",
    "Maël",
    "Nolwenn",
    "Erwan",
    "Soizic",
    "Loïc",
    "Tanguy",
    "Katell",
    "Morgane",
    "Ronan",
    "Enora",
    "Gaïd",
    "Brieuc",
    "Azilis",
    "Corentin",
    "Rozenn",
    "Goulven",
    "Annaïg",
    "Malo",
    "Tifenn",
    "Jakez",
    "Gwenola",
    "Paol",
    "Klervi",
    "Riwal",
    "Lena",
    "Alan",
)

# Les attributs dans l'ordre des « questions » du jeu, avec l'équivalent humain.
QUASI_IDENTIFIERS: tuple[Attribute, ...] = (
    Attribute(
        "zone",
        Label("Lieu de repos", "Resting spot"),
        Label("Où se repose-t-il ?", "Where does it rest?"),
        Label("adresse", "address"),
    ),
    Attribute(
        "sex",
        Label("Sexe", "Sex"),
        Label("Mâle ou femelle ?", "Male or female?"),
        Label("sexe", "sex"),
    ),
    Attribute(
        "age",
        Label("Âge", "Age"),
        Label("Quel âge a-t-il ?", "How old is it?"),
        Label("âge", "age"),
    ),
    Attribute(
        "birth_month",
        Label("Mois de naissance", "Birth month"),
        Label("Né en quel mois ?", "Born in which month?"),
        Label("date de naissance", "date of birth"),
    ),
    Attribute(
        "coat",
        Label("Pelage", "Coat"),
        Label("De quelle couleur ?", "What colour?"),
        Label("couleur des cheveux", "hair colour"),
    ),
    Attribute(
        "mark",
        Label("Signe particulier", "Distinctive mark"),
        Label("Un signe particulier ?", "Any distinctive mark?"),
        Label("tatouage, cicatrice", "tattoo, scar"),
    ),
    Attribute(
        "temper",
        Label("Caractère", "Temper"),
        Label("Quel caractère ?", "What temper?"),
        Label("profil comportemental", "behaviour profile"),
    ),
    Attribute(
        "weight_kg",
        Label("Poids", "Weight"),
        Label("Combien pèse-t-il ?", "How heavy?"),
        Label("poids", "weight"),
    ),
    Attribute(
        "length_cm",
        Label("Taille", "Length"),
        Label("Combien mesure-t-il ?", "How long?"),
        Label("taille", "height"),
    ),
)
