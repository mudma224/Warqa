# Warqa — lecture automatique des factures

Plateforme expérimentale d'extraction structurée de données de factures pour la
transition vers la facturation électronique au Maroc. Présentation du projet :
`docs/PROJET.md`.

## Structure du dépôt

```
docs/            Présentation du projet
notebooks/       Cahiers d'exploration (dataset, évaluations)
scripts/         Scripts d'exploitation (tests de fumée, préparation des données)
src/             Code source du projet (moteur, démo)
```

Le code du benchmark DocILE (bibliothèque + baselines) vit **hors du dépôt**,
dans `../docile-upstream`, à un commit épinglé. Pour le récupérer :
`bash scripts/fetch_docile.sh`. Motif : code tiers de recherche, maintenu en
dehors du périmètre de ce projet.

## Environnement Docker

L'environnement d'exécution est le conteneur officiel du benchmark DocILE
(Python 3.14, poppler, dépendances verrouillées par `uv`).

```bash
docker compose build                 # construire l'image (~quelques minutes)
docker compose up -d                 # démarrer le conteneur en arrière-plan
docker compose exec docile uv run python scripts/smoke_test.py
```

Le dataset doit être présent dans `data/docile/` (téléchargé via le script
officiel du benchmark, avec token personnel — ne jamais le versionner).

## Démonstration (présentation aux cabinets pilotes)

```bash
docker compose up -d demo            # construit si besoin et démarre la démo
# puis ouvrir http://localhost:8501
```

Le jeu de factures de démonstration est régénérable via
`docker compose exec docile uv run python scripts/prepare_demo.py`
(sélection automatique de 15 documents à une page, riches en champs clés,
parmi les meilleures prédictions du checkpoint officiel LayoutLMv3).

## Standards

- Python : PEP 8 (Ruff), typage (mypy), docstrings style Google
- Commits : Conventional Commits ; versions : Semantic Versioning
- Aucune donnée réelle non anonymisée dans le dépôt ni dans l'historique
