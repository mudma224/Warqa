# Cours 02 — Le dataset DocILE : téléchargement, structure, annotations

**Objectifs** : comprendre d'où viennent les données du projet, comment elles ont
été téléchargées, comment elles sont rangées sur le disque, et ce que contient
exactement un fichier d'annotation.

---

## 1. Qu'est-ce que DocILE ?

**DocILE** (*Document Information Localization and Extraction*) est un benchmark
public créé par l'entreprise Rossum en 2023 pour la recherche sur la lecture de
documents commerciaux. Un « benchmark » est un jeu de données + des règles
d'évaluation partagées par toute la communauté scientifique.

Pourquoi ce choix pour Warqa :
- le plus grand dataset public de documents commerciaux annotés (≈ 6 700 documents) ;
- des annotations exactement au format de notre tâche (champs + boîtes) ;
- l'OCR déjà calculé (on n'a pas à le refaire) ;
- licence MIT (utilisation libre, y compris commerciale).

## 2. L'accès protégé par token

Les données sont sur un serveur **S3 d'Amazon** (un service de stockage de fichiers
sur internet). L'accès se fait par des URL de la forme :

```
https://docile-dataset-rossum.s3.eu-west-1.amazonaws.com/<TOKEN>/<fichier>.zip
```

Le `<TOKEN>` est un code personnel obtenu en remplissant un formulaire sur
docile.rossum.ai. Il sert à Rossum pour savoir qui télécharge (et pour rendre les
données « semi-publiques » : accessibles à tous, mais traçables).

> ⚠️ **Règle de sécurité** : un token ne se partage pas, ne se met jamais dans le
> code versionné. Dans nos commandes il était passé par une variable d'environnement
> (`TOKEN=... curl ...`), jamais écrit dans un fichier du dépôt.

## 3. Les composants et leurs tailles (mesurées avant téléchargement)

Avant de télécharger, on a interrogé le serveur avec des requêtes **HEAD**
(« donne-moi juste les informations du fichier, pas son contenu ») via `curl -I`.
Résultat :

| Composant | Contenu | Taille | Téléchargé ? |
|---|---|---:|---|
| `annotated-trainval.zip` | Documents annotés train + val | 1,06 Go | ✅ |
| `test.zip` | Documents annotés test | 0,20 Go | ✅ |
| `synthetic.zip` | ~100 000 documents artificiels | 3,19 Go | ✅ |
| `unlabeled` (94 archives) | ~960 000 documents SANS annotations | **≈ 310 Go** | ❌ hors budget |
| `unlabeled` OCR seul | OCR sans les PDF | ≈ 48 Go | ❌ inutile pour l'instant |

> 💡 **Leçon de méthode** : mesurer avant de télécharger. Les 310 Go du volet
> *unlabeled* ne servent qu'au pré-entraînement massif — pas nécessaires pour
> notre usage supervisé.

Téléchargement effectué avec `curl -O <url>` (curl = outil en ligne de commande
pour transférer des fichiers ; `-O` garde le nom du fichier distant).

## 4. Structure sur le disque après extraction

L'extraction des trois archives (avec le module `zipfile` de Python) donne :

```
data/docile/
├── train.json        ← liste des 5 180 identifiants du split train
├── val.json          ← liste des 500 identifiants du split val
├── trainval.json     ← 5 680 (train + val)
├── test.json         ← 1 000 identifiants du split test
├── synthetic.json    ← 100 000 identifiants synthétiques
├── pdfs/             ← 106 680 fichiers PDF (un par document)
├── annotations/      ← 106 680 fichiers JSON (un par document)
├── ocr/              ← 106 680 fichiers d'OCR pré-calculé
└── htmls/            ← 100 000 sources HTML (documents synthétiques seulement)
```

Vérification faite à l'époque : **5 680 + 1 000 + 100 000 = 106 680** — le nombre
de fichiers de chaque dossier correspond exactement aux index. Rien ne manquait.

> 💡 **Le rôle des splits** : *train* sert à entraîner, *val* à régler et comparer,
> *test* à l'examen final — jamais regardé pendant le développement. C'est comme
> réviser avec des annales, puis passer un examen avec des questions nouvelles.
> Le split *test* de DocILE est d'ailleurs **caché** : l'évaluation officielle se
> fait en soumettant ses prédictions sur un site dédié.

## 5. Ce que contient un fichier d'annotation

Chaque document a son fichier JSON (format texte structuré par clés). Exemple réel
du document `00134dd365a24343b35b78c6` :

```json
{
 "field_extractions":   [ ... champs KILE ... ],
 "line_item_extractions": [ ... champs LIR ... ],
 "line_item_headers":   [ ... ],
 "metadata":            { ... }
}
```

Un champ KILE extrait ressemble à ceci :

```json
{
 "bbox": [0.7825, 0.3495, 0.8833, 0.3607],
 "fieldtype": "document_id",
 "page": 0,
 "text": "990304502"
}
```

Lecture : *sur la page 0, dans le rectangle qui va de 78 % à 88 % de la largeur et
35 % à 36 % de la hauteur, se trouve le numéro de facture, et il vaut « 990304502 »*.

Ce document avait **17 champs KILE** et **6 extractions de lignes**, avec des types
tels que : `vendor_name`, `customer_billing_name`, `date_issue`, `amount_due`,
`amount_total_gross`, `document_id`, `account_num`…

**En échantillonnant 300 documents**, nous avons trouvé **35 types de champs
différents** — couvrant exactement « noms, dates, totaux, identifiants ».

## 6. L'OCR pré-calculé

Chaque document a aussi son fichier OCR : pour **chaque mot de la page**, il donne
le texte reconnu, sa boîte, et le numéro de ligne. C'est un gain de temps énorme :
toute la chaîne (OCR puis extraction) peut être développée et évaluée sans jamais
avoir à relancer la lecture optique.

## 7. Le test de fumée (smoke test)

Premier réflexe après l'installation : un **test de fumée** — un tout petit
programme qui vérifie que la chaîne de base fonctionne (« est-ce que ça fume ? »).
Le nôtre (`scripts/smoke_test.py`) fait quatre choses :

```python
val = Dataset("val", "/app/data/docile")       # 1. charger le split val
doc = val[0]                                   # 2. prendre le 1er document
ann = doc.annotation                           # 3. lire ses métadonnées
print(ann.page_count, ann.document_type,
      ann.language, ann.currency)               #    pages, type, langue, devise
fields = ann.fields                            # 4. lire ses champs annotés
ocr_words = doc.ocr.get_all_words(page=0)      #    et l'OCR de la page 0
```

Résultat obtenu : 500 documents chargés, le premier a 10 champs annotés et
198 mots d'OCR. **Chaîne validée de bout en bout.**

> 💡 **Leçon vécue** : nos deux premières tentatives ont échoué
> (`doc.pages` n'existe pas, puis `doc.ocr.get_all_words()` exige `page=0`).
> Normal : on découvrait l'API. La méthode : **lire le code source** du projet
> (`docile/dataset/document.py`) pour connaître les vrais noms. Un test de fumée
> sert exactement à découvrir ce genre de choses en 2 minutes au lieu de 2 heures.

## 8. Les métadonnées bonus

Chaque annotation contient aussi :
- `document_type` : `invoice`, `order`, `tax_invoice`…
- `language` : `eng`, `fra`…
- `currency` : `usd`, `eur`…

Ces métadonnées nous ont servi pour **curater la démo** (cours 07) : choisir des
factures d'une page, riches en champs, visuellement propres.

## À retenir

- DocILE = ~6 700 documents annotés (trainval 5 680 + test 1 000) + 100 000 synthétiques.
- L'index des splits est dans des JSON à la racine ; chaque document a PDF + annotation + OCR.
- Une annotation = champ typé + boîte normalisée + texte, écrit par un humain.
- Toujours valider une installation par un test de fumée minimal.
- Token jamais versionné ; tailles mesurées avant téléchargement.

## Exercices

1. Pourquoi n'avons-nous pas téléchargé les 960 000 documents *unlabeled* ?
2. Ouvre `data/docile/annotations/` et trouve l'annotation du premier docid de
   `val.json` ; combien de champs `field_extractions` contient-elle ?
3. Une bbox `[0.10, 0.10, 0.50, 0.20]` sur une page de 2000 px de large : donne
   le rectangle en pixels. *(Réponse : de (200, ?) — la hauteur dépend de la page.)*
