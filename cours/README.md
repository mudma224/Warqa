# Formation Warqa — comprendre tout ce qui a été fait

Bienvenue dans ta formation personnelle. Elle retrace **l'intégralité du chemin parcouru**
depuis le téléchargement du dataset DocILE jusqu'à la démonstration opérationnelle,
en expliquant chaque concept de zéro, comme si tu n'avais jamais vu ce domaine.

## Comment utiliser cette formation

1. Suis les cours **dans l'ordre** — chaque cours s'appuie sur les précédents.
2. Garde le projet ouvert à côté (`<dossier-racine-du-depot>`) :
   chaque cours pointe vers de vrais fichiers, de vraies commandes, de vrais résultats.
3. Fais les petits exercices en fin de cours (10 minutes chacun, sur papier ou terminal).
4. En cas de doute sur un mot, va au glossaire du cours 01 puis reviens.

## L'histoire en résumé (à lire avant tout)

| # | Ce qui s'est passé | Cours |
|---|---|---|
| 1 | Téléchargement du dataset public DocILE (13 Go de factures annotées) | 02 |
| 2 | Mise en place du versionnement Git + GitHub (dépôt `Warqa`) | 03 |
| 3 | Construction de l'environnement d'exécution Docker | 04 |
| 4 | Premier test : charger le dataset et lire ses annotations | 02 |
| 5 | Téléchargement du modèle de référence LayoutLMv3 (1,15 Go) | 05 |
| 6 | Évaluation officielle du modèle (F1 = 0,608 / 0,665) | 06 |
| 7 | Construction de la démonstration Streamlit francophone | 07 |
| 8 | Sorties terrain, accord de confidentialité, conformité | 08 |
| 9 | Prochaine étape : l'adaptation aux factures marocaines | 09 |

## Les cours

| Cours | Titre | Prérequis |
|---|---|---|
| [01](01-fondamentaux-ocr-et-kie.md) | Les fondamentaux : OCR, extraction d'informations, KILE et LIR | aucun |
| [02](02-dataset-docile.md) | Le dataset DocILE : téléchargement, structure, annotations | 01 |
| [03](03-git-github.md) | Versionner son travail : Git, GitHub et bonnes pratiques | aucun |
| [04](04-docker.md) | Docker : exécuter le projet partout, sans casse-tête | aucun |
| [05](05-modele-layoutlmv3.md) | LayoutLMv3 : le modèle qui lit les factures | 01, 02 |
| [06](06-evaluation-metriques.md) | Évaluer un modèle : précision, rappel, F1, AP | 05 |
| [07](07-demo-streamlit.md) | La démonstration : Streamlit, curation et test | 02, 05 |
| [08](08-donnees-reelles-et-conformite.md) | Données réelles : collecte, annotation, conformité | 01 |
| [09](09-vers-l-adaptation-marocaine.md) | La suite : transfert d'apprentissage vers le Maroc | 05, 06 |

## La carte du projet (où est quoi)

```
OCR-Projet/
├── data/docile/          ← le dataset (13 Go, NON versionné)
│   ├── train.json / val.json / test.json / synthetic.json
│   ├── pdfs/  annotations/  ocr/  htmls/
├── models/               ← le modèle LayoutLMv3 (1,15 Go, NON versionné)
│   └── layoutlmv3-ours/  (checkpoints/ et predictions/)
├── src/demo/             ← l'application de démonstration
│   ├── demo_core.py      (logique : fiche, boîtes, export JSON)
│   ├── app.py            (interface Streamlit)
│   └── demo_docs.json    (les 15 factures de la démo)
├── scripts/              ← outils (smoke test, curation, évaluation)
├── reports/              ← rapports de métriques
├── docs/                 ← cahier des charges, accords, script de pitch
├── docker/               ← Dockerfile de la démo
├── docker-compose.yml    ← la définition des conteneurs
└── cours/                ← cette formation
```

**Hors du dépôt** (dans `DeepLearning/docile-upstream/`) : le code source du
benchmark DocILE, cloné à un commit épinglé — voir cours 03 pour l'histoire.
