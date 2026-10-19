# Cours 06 — Évaluer un modèle : précision, rappel, F1, AP

**Objectifs** : maîtriser les métriques du projet (précision, rappel, F1, AP, IoU),
comprendre comment l'évaluation officielle de DocILE fonctionne, et tirer la leçon
des deux erreurs de calcul que j'ai faites devant toi — parce qu'elles enseignent
exactement les pièges classiques.

---

## 1. Évaluer, c'est comparer aux bonnes réponses

Évaluer un modèle d'extraction, c'est : donner au modèle des documents **dont on
connaît les annotations** (la vérité, écrite par des humains), collecter ses
**prédictions**, et compter à quel point elles coïncident.

Règle d'or : on n'évalue JAMAIS sur les documents d'entraînement (il les a
mémorisés). On utilise le split **val** (pendant le développement) et le split
**test** (l'examen final, caché).

## 2. VP, FP, FN : les trois compteurs

Pour chaque prédiction, on la compare à la vérité :

| Compteur | Nom | Signification | Exemple sur une facture |
|---|---|---|---|
| **VP** | Vrai positif | Le modèle annonce un champ, et il est correct | il annonce `date_issue : 3/4/2020` → vrai |
| **FP** | Faux positif | Il annonce un champ… à tort | il annonce `total` là où il n'y a qu'un sous-total |
| **FN** | Faux négatif | Il **rate** un champ qui existe | le vrai `date_due` existe, lui n'a rien dit |

De ces compteurs découlent tout :

```
Précision = VP / (VP + FP)      « Parmi ce que j'annonce, combien est correct ? »
Rappel    = VP / (VP + FN)      « Parmi ce qui existe, combien ai-je trouvé ? »
F1        = 2 × P × R / (P + R) « La moyenne harmonique : pénalise les déséquilibres »
```

> 💡 Intuitions : la **précision** répond au fear du comptable « est-ce que ce
> qu'il me remplit est fiable ? » ; le **rappel** répond à « est-ce qu'il m'oublie
> des choses ? ». Un modèle qui annonce tout à tout le monde a 100 % de rappel et
> une précision minable. Le F1 équilibre les deux.

## 3. Et les boîtes ? Le rôle de l'IoU

Une prédiction est correcte si le **texte** ET **l'endroit** sont bons. Pour
comparer deux rectangles, on calcule l'**IoU** (*Intersection over Union*) :
l'aire du chevauchement divisée par l'aire de la réunion.

- IoU = 1,0 : rectangles parfaitement superposés ;
- IoU = 0 : aucun chevauchement.

L'évaluation DocILE exige un IoU au-dessus d'un seuil pour valider un VP. Et un
détail malin : les boîtes (prédictions et annotations) sont **« claquées » sur les
lignes de texte de l'OCR** (*snapping*) — donc quand le modèle choisit les bons
mots, sa boîte alignée devient **exactement** celle de la vérité. L'IoU = 1,0 est
alors atteignable, ce qui explique le seuil utilisé.

## 4. L'histoire vraie : mes deux erreurs de calcul

Les fichiers de résultats téléchargés avec le checkpoint contenaient les
appariements prédiction/vérité par document. J'ai voulu recalculer les métriques
moi-même — et je me suis trompé deux fois. Ce récit vaut tous les cours :

**Tentative 1 — « Rappel = 100 % »** : j'ai compté comme vérité seulement les
champs appariés dans la liste `ordered_predictions_with_match`… qui, par
construction, ne contient QUE des prédictions (appariées ou non). Résultat : mes
vérités étaient en réalité les VP → rappel absurde à 100 %.

**Tentative 2 — « Rappel = 153 % »** : j'ai corrigé en comptant la clé
`false_negatives`… mais j'avais retiré les VP du compte des vérités. Rappel > 100 %
: mathématiquement impossible. Un rappel de 153 % doit faire sonner l'alarme
immédiatement — **aucune métrique ne dépasse 100 %**.

**La résolution** : lire le code source de l'évaluation upstream
(`pcc_field_matching.py`), dont la docstring dit tout :

```
ordered_predictions_with_match : TOUTES les prédictions, chacune appariée
                                 à sa vérité, ou à None si non appariée.
matches (vérité non nulle)      = les VRAIS POSITIFS
gold is None                    = les FAUX POSITIFS
false_negatives                 = les vérités JAMAIS retrouvées
annotations (total vérité)      = VP + FN
```

**Bilan final correct** (split val, 500 documents) :

| | VP | FP | FN | Précision | Rappel | F1 |
|---|---:|---:|---:|---:|---:|---:|
| KILE | 3 545 | 2 254 | 2 317 | 0,611 | 0,605 | **0,608** |
| LIR | 6 801 | 3 021 | 3 842 | 0,692 | 0,639 | **0,665** |

> ⚠️ **Réflexes à graver** : (1) une métrique > 100 % = erreur de parsing ;
> (2) avant de réinventer une formule, **chercher la définition dans le code
> officiel** ; (3) recouper avec des chiffres publiés (le README des baselines).

## 5. La solution retenue : l'évaluateur officiel

Plutôt que de réimplémenter, on utilise l'outil de DocILE lui-même :

```bash
python -m docile.cli.evaluate -t KILE \
  -d /app/data/docile -s val \
  -p /app/models/layoutlmv3-ours/predictions/layoutlmv3_ours/val_predictions_KILE.json \
  --evaluate-fieldtypes
```

Recoupement avec le tableau publié en 2023 : LIR F1 **0,665 vs 0,666** publié ✓
(écart quasi nul) ; KILE 0,608 vs 0,657 (écart documenté : l'évaluateur et les
dépendances ont évolué depuis). Le rapport complet est dans `reports/`.

## 6. AP : la métrique principale de la tâche KILE

La précision et le rappel dépendent d'un réglage : **à partir de quel score de
confiance accepte-t-on une prédiction ?** Baisser le seuil augmente le rappel mais
baisse la précision.

L'**AP** (*Average Precision*) résume **toute la courbe** précision/rappel en un
seul nombre : c'est l'aire sous cette courbe. C'est la métrique principale de la
tâche KILE (AP = 0,453 pour notre baseline). Pour la tâche LIR, la métrique
principale est le F1 (0,665).

> 💡 AP élevé = le modèle classe bien ses propres prédictions : en ne gardant que
> ses annonces les plus sûres, on obtient d'excellentes précisions.

## 7. x-shot : la leçon de généralisation

DocILE classe les documents par **gabarits** (mises en page) et évalue séparément
selon le nombre d'exemplaires du gabarit vus à l'entraînement :

| Sous-ensemble | Signification | F1 KILE |
|---|---|---:|
| 0-shot | gabarits **jamais vus** à l'entraînement | 0,438 |
| 1-3-shot | 1 à 3 exemples vus | 0,584 |
| 4+-shot | 4 exemples ou plus vus | 0,685 |

La leçon est brutale et précieuse : **sur un gabarit inconnu, la performance
chute de 37 points**. C'est expérimentalement exactement notre cas (factures
marocaines = gabarits jamais vus) — et c'est ce que l'adaptation par fine-tuning
sur tes données réelles viendra corriger.

## 8. Lire le détail par type de champ

L'évaluation par champ révèle des profils très différents :

- ** Excellents** (F1 ≥ 0,86) : `date_due`, `date_issue`, `document_id`,
  `amount_due` — champs présents, bien positionnés, vocabulaire stable ;
- **Bons** (0,70–0,78) : `vendor_name`, `customer_billing_name` ;
- **Faibles** : `vendor_tax_id` (0,47), `customer_billing_address` (0,56) ;
- **Nuls** (0,00) : `payment_reference`, `payment_terms`, `tax_detail_*`, `iban`,
  `bic` — rares, ambigus ou jamais appris.

Pour Warqa, c'est doublement bon à savoir : nos cibles doivent être réalistes, et
les champs faibles de DocILE (TVA, références de paiement) sont précisément là où
la facture marocaine est structurée — la marge de progression de notre adaptation.

## À retenir

- Précision = fiabilité de ce qui est annoncé ; Rappel = capacité à tout trouver ;
  F1 = l'équilibre des deux ; AP = le résumé de toute la courbe.
- Aucune métrique ne peut dépasser 100 % — sinon, erreur de comptage.
- L'IoU compare les boîtes ; l'alignement sur les lignes de texte rend l'appariement
  exact possible.
- Toujours évaluer avec l'outil officiel et recouper avec les chiffres publiés.
- 0-shot ≠ 4+-shot : sans adaptation, un gabarit nouveau fait chuter la performance.

## Exercices

1. Un modèle annonce 10 montants : 7 corrects. La facture contenait 9 montants.
   Donne VP, FP, FN, précision, rappel, F1.
   *(Réponse : VP 7, FP 3, FN 2 ; P = 0,70 ; R = 0,78 ; F1 ≈ 0,74.)*
2. Quel compteur augmente si le modèle devient trop bavard (seuil de confiance
   baissé) ? *(Réponse : FP, donc la précision baisse, le rappel monte.)*
3. Pourquoi le 0-shot est-il le sous-ensemble le plus important pour Warqa ?
