# Re-identify me! — recettes du projet. `just` sans argument liste tout.
set shell := ["bash", "-cu"]

default:
    @just --list

# Installe l'environnement (dépendances + outils de dev)
setup:
    uv sync

# Génère l'île de Kerdata et l'exporte pour l'appli web
generate size="2000" seed="29":
    uv run kerdata generate --size {{size}} --seed {{seed}}

# Affiche la courbe d'unicité dans le terminal
report size="2000" seed="29":
    uv run kerdata report --size {{size}} --seed {{seed}}

# Tous les tests, avec couverture
test:
    uv run pytest --cov=kerdata --cov-report=term-missing

# Tests unitaires seulement (rapides)
test-unit:
    uv run pytest tests/unit

# Tests d'intégration seulement
test-integration:
    uv run pytest tests/integration -m integration

# Lint + formatage vérifié
lint:
    uv run ruff check .
    uv run ruff format --check .

# Formate le code
fmt:
    uv run ruff check --fix .
    uv run ruff format .

# Vérification de types (mypy strict)
typecheck:
    uv run mypy

# Tout ce que vérifie la CI
check: lint typecheck test

# Sert l'appli web en local sur http://localhost:8000
serve: generate
    cd web && uv run python -m http.server 8000

# Ouvre le carnet Jupyter « sous le capot »
notebook:
    uv run --with jupyterlab --with matplotlib jupyter lab notebooks/

# Assemble l'appli en un seul fichier HTML autonome (dist/)
bundle: generate
    uv run python scripts/bundle.py

# Ré-exécute le carnet pour mettre à jour ses sorties
notebook-run:
    uv run --with jupyterlab --with matplotlib jupyter nbconvert --to notebook --execute --inplace notebooks/sous-le-capot.ipynb
