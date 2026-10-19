# Cours 09 — La suite : transfert d'apprentissage vers les factures marocaines

**Objectifs** : comprendre précisément ce qui va se passer quand tes données
réelles arriveront : le fine-tuning, pourquoi la traduction du dataset anglais a
été écartée, quelles cibles viser, et quel est le chemin restant.

---

## 1. Le concept : le transfert d'apprentissage

**Transfert d'apprentissage** (*transfer learning*) = réutiliser ce qu'un modèle a
appris sur une grande source générique pour une cible plus petite et spécifique.

Dans le projet :

```
Étage 1 (fait)     : pré-entraînement général (millions de documents)
                     ↓
Étape 2 (fait)     : fine-tuning sur DocILE → checkpoint layoutlmv3-ours
                     (apprend : "un montant total est en bas à droite, sous
                      les mots total/amount")
Étage 3 (à venir)  : fine-tuning sur TES factures marocaines annotées
                     (apprend : "ICE en en-tête, TVA 10/20 %, formats FR,
                      cachets, gabarits locaux")
```

Pourquoi ça marche : les concepts « montant », « date », « fournisseur » sont
partagés entre les factures du monde entier. Le modèle ne repart pas de zéro — il
**réajuste** ce qu'il sait. D'où le besoin de seulement 300 à 500 documents
annotés, pas de millions.

## 2. Pourquoi on ne traduit PAS DocILE vers le français

Idée séduisante (et abandonnée à juste titre) : « le dataset est en anglais,
traduisons-le ». Le problème est mécanique : sur un document, **le texte, l'image
et les boîtes sont soudés**. Traduire « Total » en « Montant total » allonge le
mot → les positions changent → les milliers de coordonnées d'annotations ne
désignent plus rien. Réafficher le texte traduit déplace aussi la mise en page.

La traduction ne marche que pour du **texte pur** (sans image ni position). Pour
les documents visuels, la bonne voie est : modèles **multilingues pré-entraînés**
(LayoutXLM, LiLT) + fine-tuning sur de vrais documents locaux. Et bonne nouvelle
issue du terrain : les factures B2B marocaines sont déjà en français.

## 3. Le fine-tuning, concrètement

Quand les données annotées seront prêtes, l'entraînement ressemblera à :

1. **Préparer** : découper le corpus (train / val / test gelé, séparés par source) ;
2. **Charger le checkpoint** `layoutlmv3-ours` (repartir de l'existant, pas de zéro) ;
3. **Entraîner quelques époques** sur les factures marocaines — une *époque* = un
   passage complet sur le corpus ; quelques dizaines de minutes à quelques heures
   par époque sur GPU (Colab ou GPU loué) ;
4. **Évaluer après chaque essai** sur le jeu **gelé**, avec l'évaluateur officiel
   (cours 06) ;
5. **Versionner** chaque modèle essayé (registre des modèles, cours à venir en
   production) et ne garder que les non-régressions.

Ce qui demande du GPU, c'est l'étape 3 — l'étape 4 reste légère.

## 4. Les cibles, recalées sur la réalité

Le cahier des charges visait « F1 ≥ 0,85 aligné sur les modèles de référence » pour
le PoC. L'évaluation officielle a révélé que la **baseline réelle est à 0,608
(KILE) / 0,665 (LIR)**. Cibles proposées pour la révision :

| Phase | Jeu d'évaluation | Cible en-têtes | Cible lignes |
|---|---|---:|---:|
| PoC DocILE (fait) | test DocILE | au niveau de la baseline (0,61) | 0,66 |
| Adaptation alpha | 100 factures marocaines gelées | ≥ 0,75 | ≥ 0,60 |
| Bêta / v1 | 200 factures gelées | ≥ 0,85 **sur les champs majeurs** | ≥ 0,70 |

La nuance « champs majeurs » compte : les champs faibles de la baseline
(`payment_reference`, `tax_detail_*`) sont rares dans DocILE mais très structurés
dans une facture marocaine (ICE, IF, TVA) — c'est là que l'adaptation rapportera
le plus.

## 5. Le planning de cette phase (rappel du cahier des charges)

```
M1 (terrain)      : accords signés, 30 premiers documents annotés
M2 (fait)         : environnement + baseline évaluée  ← NOUS SOMMES ICI
M3 (adaptation)   : 300 documents, fine-tuning FR, démo au partenaire
M4 (bêta fermée)  : 3 à 5 cabinets testent, durcissement sécurité
M5 (recette v1)   : recette formelle, documentation, lancement
```

## 6. Après les factures : la piste v2 (relevés bancaires)

La sortie terrain a révélé une douleur peut-être plus forte : la **saisie des
relevés de compte** (30 à 200 lignes par mois, par client). C'est un problème
différent et plutôt favorable :
- l'extraction est plus simple (tableaux uniformes, souvent PDF natifs) ;
- la vraie difficulté est **classer chaque libellé** (« VIR SALAIRE » → quel
  compte ?) : un problème de classification avec validation humaine ligne par
  ligne — l'écran de vérification Warqa est déjà conçu pour ça.

Décision recommandée : factures = cœur v1 ; relevés = fonctionnalité phare v2.
Penser à étendre l'accord de fourniture aux relevés avant d'en collecter.

## 7. La feuille de route restante en cinq étapes

1. **Finir la collecte terrain** (accords, 30 documents pilotes, questions
   quantitatives : part d'arabe, volume des relevés) ;
2. **Annoter** le pilote de 30, corriger le guide, généraliser à 300+ ;
3. **Fine-tuner** dans un conteneur GPU (Colab ou loué), évaluer à chaque
   itération sur le jeu gelé avec l'évaluateur officiel ;
4. **Brancher le vrai modèle** dans la démo Streamlit (remplacer les prédictions
   pré-calculées) — nécessitera une variante du conteneur avec PyTorch ;
5. **Bêta chez les pilotes**, recette, version 1.

## À retenir

- Transfert = réutiliser l'étage général, ne refaire que la spécialisation.
- Pas de traduction de documents : texte, image et boîtes sont soudés.
- Cibles honnêtes : d'abord rattraper la baseline (0,61/0,66), puis dépasser sur
  les champs majeurs marocains.
- GPU nécessaire seulement pour l'entraînement ; l'évaluation reste légère.
- La démo que tu présenteras demain est déjà le pont vers la version finale.

## Exercices

1. Explique à un non-technique pourquoi 300 factures annotées suffisent, alors
   que DocILE en a 6 700.
2. Un fine-tuning fait chuter le F1 KILE de 0,61 à 0,50 sur DocILE mais améliore
   les factures marocaines de 0,44 à 0,70 : bon ou mauvais résultat ? Argumente.
   *(Réponse : bon — DocILE sert de garde-fou contre la « catastrophe oubli »,
   mais l'objectif métier est la performance locale ; on vérifie quand même que
   la régression reste dans les limites du cahier des charges.)*
3. Pourquoi geler le jeu de test **avant** de commencer le fine-tuning ?
