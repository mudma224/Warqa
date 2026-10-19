# Baseline officiel LayoutLMv3 (Rossum) — réévaluation sur le split val

**Date** : 19/10/2026 — **Évaluateur** : `docile.cli.evaluate` officiel (conteneur `warqa/docile`)
**Prédictions** : checkpoint officiel `layoutlmv3-ours` fourni par Rossum (prédictions val incluses)
**Commande** : `python -m docile.cli.evaluate -t KILE|LIR -d /app/data/docile -s val -p <predictions> --evaluate-fieldtypes`

## Résultats globaux (IoU = 1,0 après alignement sur les lignes de texte)

| Tâche | Métrique principale | F1 | Précision | Rappel | VP | FP | FN |
|---|---|---:|---:|---:|---:|---:|---:|
| KILE | AP 0,453 | **0,608** | 0,611 | 0,605 | 3 545 | 2 254 | 2 317 |
| LIR | F1 = métrique principale | **0,665** | 0,692 | 0,639 | 6 801 | 3 021 | 3 842 |

Recoupement avec le tableau officiel des baselines (README, 2023) : LIR val-F1 0,665 vs 0,666 publié ✓ ;
KILE val-F1 0,608 vs 0,657 publié (écart attendu — l'évaluateur et les dépendances ont évolué depuis 2023,
écart documenté par l'avertissement en tête du README des baselines).

## Généralisation KILE par nombre de documents de même gabarit vus à l'entraînement

| Sous-ensemble | AP | F1 | Précision | Rappel |
|---|---:|---:|---:|---:|
| val complet | 0,453 | 0,608 | 0,611 | 0,605 |
| 0-shot (gabarits jamais vus) | 0,278 | 0,438 | 0,432 | 0,444 |
| 1-3-shot | 0,421 | 0,584 | 0,598 | 0,571 |
| 4+-shot | 0,534 | 0,685 | 0,689 | 0,681 |

## Champs KILE — points marquants

| Champ | F1 | Lecture |
|---|---:|---|
| date_due | 0,926 | excellent |
| date_issue | 0,867 | excellent |
| document_id | 0,857 | excellent |
| amount_due | 0,881 | excellent |
| customer_billing_name | 0,770 | bon |
| vendor_name | 0,737 | bon |
| vendor_address | 0,664 | moyen |
| customer_billing_address | 0,565 | moyen |
| vendor_tax_id | 0,473 | faible |
| currency_code_amount_due | 0,065 | très faible |
| payment_reference / payment_terms / tax_detail_* / iban / bic | 0,000 | non appris |

## Implications pour Warqa

1. **Le socle est réaliste** : un modèle entraîné par l'éditeur du benchmark atteint ~0,61/0,66 — nos cibles
   d'adaptation doivent se situer par rapport à cette base, pas à 0,85.
2. **Cibles PoC révisées** (proposition de révision du tableau 24 du cahier des charges) : PoC DocILE
   « au niveau de la baseline » (KILE F1 ≥ 0,60, LIR F1 ≥ 0,66) plutôt que « ≥ 0,85 ».
3. **Les champs faibles sont connus et instructifs** : `payment_reference`, `payment_terms`, `tax_detail_*`
   sont rares ou ambigus dans DocILE — plusieurs correspondent à des champs où la facture marocaine est
   très structurée (ICE, IF, TVA 10/20 %) : notre adaptation a une vraie marge de progression à offrir.
4. **L'effet 0-shot (F1 0,438 → 0,685) confirme la stratégie** : sans adaptation sur des gabarits similaires,
   la performance chute — exactement ce que la collecte de factures marocaines viendra corriger.

## Rapports bruts

Les rapports complets de l'évaluateur (détail par type de champ, sous-ensembles) sont dans
`reports/eval_kile.txt` et `reports/eval_lir.txt`. Résultats JSON : dans `models/` (non versionné).
