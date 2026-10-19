# Cours 01 — Les fondamentaux : OCR, extraction d'informations, KILE et LIR

**Objectifs** : à la fin de ce cours, tu sauras expliquer à quelqu'un de non technique
ce que fait Warqa, et tu connaîtras le vocabulaire de base utilisé dans tout le projet.

---

## 1. Le problème de départ

Un cabinet comptable reçoit des centaines de factures papier ou PDF. Pour les
comptabiliser, une personne doit **lire** chaque facture et **taper** les informations
dans un logiciel : le nom du fournisseur, la date, le numéro de facture, les montants.

C'est lent (5 à 10 minutes par facture), fatigant, et source d'erreurs de frappe.

**La question du projet** : peut-on faire lire et comprendre ces factures par un
programme, avec un humain qui vérifie avant d'exporter ?

## 2. OCR : transformer une image en texte

Une facture scannée n'est, pour un ordinateur, qu'une **image** : une grille de
millions de points colorés (pixels). Rien ne distingue le mot « Total » d'une tache.

L'**OCR** (*Optical Character Recognition*, reconnaissance optique de caractères)
est la technologie qui regarde l'image et en extrait du **texte** :

```
Image de facture  ────[ OCR ]────►  "Total TTC : 1 234,56 MAD"
```

Un bon OCR donne aussi, pour chaque mot :
- sa **boîte englobante** (*bounding box*, ou « bbox ») : le rectangle qui l'entoure,
- parfois un **score de confiance** : à quel point il est sûr de sa lecture.

> 💡 **Analogie** : l'OCR, c'est les *yeux*. Il sait **quoi** est écrit et **où**,
> mais pas ce que ça **veut dire**.

## 3. Pourquoi l'OCR ne suffit pas : l'extraction d'informations

Après l'OCR, on a une pile de mots avec leurs positions. Mais il manque
**l'intelligence** : lequel de ces mots est le *nom du fournisseur* ? Lequel est
le *total* ? Lequel est juste une publicité ?

C'est le travail de l'**extraction d'informations clés** — en anglais
*Key Information Extraction* (**KIE**) :

```
Texte + positions  ────[ KIE ]────►  fournisseur : "Marjane"
                                     date        : 2026-03-14
                                     total TTC   : 1 234,56 MAD
```

Le modèle d'extraction est donc le **cerveau**, posé après les yeux.

## 4. Les deux tâches du benchmark DocILE

Le dataset DocILE (cours 02) structure le problème en deux tâches officielles :

| Tâche | Nom complet | Ce que ça veut dire | Exemple |
|---|---|---|---|
| **KILE** | Key Information Localization and Extraction | Trouver les **champs globaux** du document et les **localiser** | « le total TTC est *ici*, il vaut 1 234,56 » |
| **LIR** | Line Item Recognition | Reconnaître les **lignes du tableau** de produits | « ligne 3 : 2 claviers à 150, total 300 » |

- **Localization** (localisation) : on ne se contente pas de dire la valeur,
  on donne aussi **où elle se trouve** sur la page (le rectangle).
- La tâche KILE est le cœur de Warqa ; la tâche LIR (les lignes de produits)
  est la deuxième brique, plus difficile.

## 5. Le vocabulaire du projet (à connaître par cœur)

| Terme | Définition simple |
|---|---|
| **Document** | Une facture (ou un bon de commande…), fichier PDF |
| **Page** | Une image du document ; une facture peut avoir plusieurs pages |
| **Champ** (*field*) | Une information typée : `date_issue`, `amount_total_gross`… |
| **Type de champ** (*fieldtype*) | L'étiquette du champ : `vendor_name` = « nom du fournisseur » |
| **Boîte englobante** (*bbox*) | Rectangle [gauche, haut, droite, bas] en coordonnées **normalisées entre 0 et 1** (0 = bord gauche/haut de la page, 1 = bord droit/bas) |
| **Annotation** | La vérité : le champ + sa bbox + son texte, écrit par un humain |
| **Prédiction** | Ce que le modèle propose (à comparer à l'annotation) |
| **Gabarit** (*layout*) | La mise en page d'un type de facture ; deux factures du même fournisseur ont le même gabarit |
| **Score de confiance** | Un nombre entre 0 et 1 : à quel point le modèle est sûr |
| **Split** | Un sous-ensemble du dataset : *train* (entraîner), *val* (régler), *test* (examen final) |

> ⚠️ **Pourquoi des coordonnées entre 0 et 1 ?** Pour que les positions restent
> valables quelle que soit la taille de l'image (un PDF peut être rendu en petit
> ou en grand). On multiplie par la largeur/hauteur réelle au moment de dessiner.

## 6. Le pipeline complet de Warqa

Tout le projet tient dans ce schéma — tu rencontreras chaque brique dans la formation :

```
┌───────────┐   ┌──────────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────────┐   ┌────────┐
│ Ingestion │ → │ Classification│ → │    OCR    │ → │  Extraction │ → │ Vérification  │ → │ Export │
│  (M1)     │   │    (M2)       │   │   (M3)    │   │    (M4)     │   │ humaine (M5)  │   │  (M6)  │
└───────────┘   └──────────────┘   └───────────┘   └─────────────┘   └───────────────┘   └────────┘
  photos,       facture, ticket,   texte + boîtes   champs + valeurs   un humain valide    JSON,
  scans, PDF    avoir…             par mot          + confiance        chaque fiche        Excel
```

Ce qui a été construit jusqu'ici couvre M3 + M4 (via le modèle DocILE) et une
première version de M5 + M6 (l'interface de vérification et l'export JSON de la démo).

## 7. La grande leçon du terrain (à garder en tête)

Les sorties chez les fiduciaires de Béni Mellal ont appris trois choses qui
**simplifient** le projet :
1. Les factures B2B marocaines sont **en français** (pas d'arabe à gérer en v1) ;
2. Les factures manuscrites sont refusées par les cabinets (donc jamais à lire) ;
3. La douleur n° 1 confirmée : **la saisie manuelle** — et les relevés bancaires
   (lecture de tableaux + classement) sont une piste pour la version 2.

## À retenir

- OCR = les yeux (image → mots + positions) ; KIE = le cerveau (mots → champs structurés).
- KILE = champs globaux localisés ; LIR = lignes du tableau.
- Une bbox normalisée entre 0 et 1 indique où se trouve une information, quelle
  que soit la résolution.
- Pas d'export sans validation humaine : c'est le principe directeur du produit.

## Exercices

1. Explique en deux phrases à un ami la différence entre OCR et KIE.
2. Une bbox est `[0.72, 0.88, 0.94, 0.91]` sur une page rendue en 1000 × 1400 pixels.
   Donne le rectangle en pixels. *(Réponse : de (720, 1232) à (940, 1274).)*
3. Quelle est la différence entre `vendor_name` et `customer_billing_name` ?
   *(Réponse : le vendeur = celui qui émet la facture ; le client = celui qui la reçoit.)*
