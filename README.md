# Warqa — lecture automatique des factures

Plateforme expérimentale d'extraction structurée de données de factures pour la
transition vers la facturation électronique au Maroc. Voir `docs/Warqa_Cahier_des_Charges_v1.0.docx`
pour le cahier des charges complet.

## Structure du dépôt

```
data/            Dataset DocILE et données terrain (non versionné — voir .gitignore)
docs/            Cahier des charges, accords, scripts de génération de documents
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

## Standards

- Python : PEP 8 (Ruff), typage (mypy), docstrings style Google
- Commits : Conventional Commits ; versions : Semantic Versioning
- Aucune donnée réelle non anonymisée dans le dépôt ni dans l'historique
