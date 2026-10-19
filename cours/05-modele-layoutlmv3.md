# Cours 05 — LayoutLMv3 : le modèle qui lit les factures

**Objectifs** : comprendre, sans mathématiques, ce qu'est un modèle d'IA
supervisée, ce qu'est un Transformer multimodal, ce que contient exactement le
checkpoint téléchargé, et pourquoi les prédictions pré-calculées nous ont fait
gagner un temps précieux.

---

## 1. L'apprentissage supervisé en une page

L'idée de l'apprentissage **supervisé** tient en trois temps :

1. Montrer des **exemples corrigés** à la machine : « voici une facture, voici
   où est le fournisseur, voici la date… » (ce sont les *annotations*, cours 02) ;
2. La machine ajuste des millions de **paramètres internes** (ses « molettes »)
   pour passer de l'image à la bonne réponse ;
3. Une fois entraînée, elle généralise : elle prédit sur des factures **jamais vues**.

Un **modèle** = cette machine à paramètres. Un **checkpoint** = la photo de la
machine à un instant donné : ses paramètres sauvegardés dans un fichier.

> 💡 Analogie : entraîner = faire passer 10 000 exercices corrigés ; le
> checkpoint = le cahier final de l'élève, celui qu'on photographie pour
> qu'il puisse répondre à l'examen sans re-réviser.

## 2. Le problème des factures : trois informations à la fois

Pour comprendre une facture, il faut combiner :
- **le texte** (« Total TTC », « 1 234,56 ») ;
- **la position** (le total est en bas à droite, pas au milieu du titre) ;
- **l'image** (polices, cadres de tableaux, cachets).

Un modèle de texte classique (type ChatGPT d'origine) ne voit ni la position ni
l'image. **LayoutLMv3** est un modèle entraîné pour les trois à la fois : on dit
qu'il est **multimodal** (plusieurs « modes » d'information).

## 3. Un Transformer, c'est quoi (version honnête et simple)

Les modèles modernes sont des **Transformers**. Leur idée centrale s'appelle
l'**attention** : chaque mot « regarde » tous les autres mots (et toutes les zones
de l'image) et décide lesquels sont pertinents pour le comprendre.

Exemple sur une facture : pour décider que `1 234,56` est le `Total TTC`, le modèle
combine :
- la proximité du mot « Total » au-dessus du nombre ;
- l'alignement des boîtes (le nombre est aligné à droite comme les autres montants) ;
- le fait que « TTC » apparaît rarement ailleurs qu'à côté d'un montant.

Personne n'écrit ces règles : le modèle les **apprend** des milliers d'exemples
annotés. C'est tout l'intérêt de DocILE.

> 💡 Tu n'as pas besoin des mathématiques de l'attention pour ce projet. Ce qu'il
> faut retenir : **le modèle apprend des régularités entre texte, positions et
> image, à partir d'exemples annotés.**

## 4. Pré-entraînement puis spécialisation

LayoutLMv3 n'a pas été entraîné directement sur les factures. Deux étages :

1. **Pré-entraînement** : le modèle a « lu » des millions de documents génériques
   avec des exercices auto-générés (deviner un mot masqué, apparier des régions
   d'image et de texte). Il ressort **généraliste des documents**. C'est le
   checkpoint public `microsoft/layoutlmv3-base`.
2. **Fine-tuning** (spécialisation) : on le ré-entraîne sur une tâche précise avec
   des annotations humaines — ici, DocILE et ses 55 types de champs. Résultat :
   le checkpoint **`layoutlmv3_ours_320587`** (« ours » = entraîné par Rossum).

> 💡 Analogie : un étudiant qui a lu toute la bibliothèque (pré-entraînement),
> puis suit un stage de spécialisation factures (fine-tuning). C'est pourquoi
> notre stratégie s'appelle **transfert** : réutiliser l'étage 1, refaire l'étage 2
> avec des données marocaines (cours 09).

## 5. Ce que contient notre archive (extraction réelle)

`models/layoutlmv3-ours/checkpoints/layoutlmv3_ours_320587/` :

| Fichier | Taille | Rôle |
|---|---:|---|
| `pytorch_model.bin` | 481 Mo | **Les paramètres du modèle** — le cœur |
| `config.json` | quelques Ko | L'architecture (nombre de couches, etc.) |
| `tokenizer.json`, `vocab.json`, `merges.txt` | ~3 Mo | Le « dictionnaire » qui découpe le texte en morceaux (*tokens*) |
| `optimizer.pt` | 961 Mo | L'état de l'optimiseur — utile pour **continuer** l'entraînement, inutile pour répondre |
| `trainer_state.json` | 13 Mo | Le journal d'entraînement (courbes de perte) |

> ⚠️ Pour **utiliser** le modèle, seul `pytorch_model.bin` + `config` + tokenizer
> sont nécessaires. L'optimizer explique pourquoi l'archive fait 1,15 Go pour un
> modèle de 481 Mo.

## 6. Inférence vs entraînement : le sujet GPU

- **Inférence** (faire des prédictions) : léger. Quelques secondes par page sur un
  simple processeur.
- **Entraînement / fine-tuning** : lourd. Il faut un GPU (la puce graphique qui
  fait des milliers de calculs en parallèle) — d'où la stratégie prévue : Colab ou
  GPU loué à la demande pour la phase d'adaptation.

## 7. Le jackpot : des prédictions pré-calculées

L'archive téléchargée contenait aussi le dossier `predictions/` :

- `val_predictions_KILE.json` : les prédictions du modèle sur les **500 documents
  de validation** (champ, boîte, texte, score) ;
- `val_results_KILE.json` / `val_results_LIR.json` : les **appariements**
  prédiction/vérité document par document ;
- `log_inference.txt` : la commande exacte utilisée par Rossum.

Conséquences majeures :
1. **L'évaluation officielle** a pu être refaite en quelques minutes, sans GPU
   (cours 06) ;
2. **La démonstration** fonctionne sans jamais lancer le modèle : elle affiche les
   prédictions pré-calculées des 15 factures curated (cours 07) ;
3. Le GPU ne devient nécessaire qu'à l'étape d'adaptation (cours 09).

> 💡 Leçon de méthode : avant de lancer un gros calcul, vérifier si quelqu'un n'a
> pas déjà publié le résultat. Ici, 1,15 Go téléchargés ont économisé des heures
> de GPU.

## 8. Les autres baselines du benchmark (pour ta culture)

| Baseline | Idée | Résultat val (F1 KILE) |
|---|---|---:|
| `roberta_base` | Transformeur **texte seul** (pas d'image ni de position 2D) | 0,688 |
| `roberta_ours` | idem, pré-entraîné par Rossum | 0,671 |
| `layoutlmv3_ours` | multimodal (notre choix) | 0,657 |
| `…_with_synthetic_pretraining` | spécialisés après pré-entraînement sur les 100 k synthétiques | 0,674–0,689 |

Leçon étonnante : sur ce benchmark, le texte seul était compétitif — mais pour
**localiser** les champs (notre besoin visuel des boîtes surlignées) et pour
l'adaptation marocaine, le multimodal reste le bon choix.

## À retenir

- Supervisé = exemples corrigés → paramètres → généralisation.
- LayoutLMv3 combine texte + positions + image ; pré-entraîné puis spécialisé.
- Checkpoint = paramètres + config + tokenizer (+ optimizer pour reprendre l'entraînement).
- Inférence légère, entraînement lourd — et les prédictions pré-calculées de
  Rossum nous ont dispensés des deux pour l'instant.

## Exercices

1. Explique la différence entre pré-entraînement et fine-tuning avec l'analogie
   de ton choix.
2. Que faut-il au minimum pour faire des prédictions avec le checkpoint ?
   *(Réponse : pytorch_model.bin + config.json + les fichiers de tokenizer.)*
3. Pourquoi la démo fonctionne-t-elle sans GPU ?
