# Cours 03 — Versionner son travail : Git, GitHub et bonnes pratiques

**Objectifs** : comprendre à quoi sert Git, savoir ce qui a été fait sur le dépôt
Warqa, et connaître les règles appliquées (et pourquoi).

---

## 1. Le problème que Git résout

Sans Git, on travaille avec `rapport_v1.docx`, `rapport_v2_final.docx`,
`rapport_v2_final_VRAIMENT_final.docx`… Git remplace ce chaos par :

- un **historique complet** : chaque état du projet est archivé (un « commit ») ;
- le **retour arrière** : revenir à n'importe quel état ;
- la **collaboration** : plusieurs personnes, plusieurs machines, sans écrasement ;
- la **preuve de sérieux** : un historique propre est un argument dans un rapport.

## 2. Vocabulaire essentiel

| Terme | Définition |
|---|---|
| **Dépôt** (*repository*, repo) | Le dossier du projet + tout son historique |
| **Commit** | Un instantané du projet, avec un message décrivant le changement |
| **Branche** | Une ligne de travail parallèle ; `main` est la branche principale |
| **Remote** | Une copie du dépôt sur un serveur (ici GitHub : `git@github.com:mudma224/Warqa.git`) |
| **Push / Pull** | Envoyer / récupérer les commits vers/depuis le remote |
| **`.gitignore`** | La liste des fichiers à ne JAMAIS versionner |

## 3. Ce qui a été fait sur le dépôt Warqa

Séquence réelle (visible avec `git log --oneline`) :

1. **Initialisation** par toi + connexion du remote GitHub (clé SSH).
2. **`.gitignore` créé AVANT le premier commit** — décision la plus importante :
   ```
   data/        # 13 Go de dataset : pas dans Git !
   models/      # les checkpoints (1 Go+)
   node_modules/  .mimosa/  __pycache__/  .env  *.token ...
   ```
   Pourquoi ? Git est fait pour le **code et les documents**. Les données
   volumineuses y seraient un désastre (dépôt de 13 Go impossible à cloner) ;
   les tokens et mots de passe y seraient un **risque de fuite définitif**
   (même supprimés ensuite, ils restent dans l'historique).
3. **Commits réguliers** avec des messages normalisés (voir §5).
4. **Push** vers GitHub après chaque commit (`git push`).

## 4. L'histoire du sous-module (une leçon à elle seule)

Il fallait le **code source** du benchmark DocILE (bibliothèque + scripts de
baselines). Trois approches existent :

| Approche | Principe | Avantage / inconvénient |
|---|---|---|
| **Copier-coller** le code dans le dépôt | Vendu | Simple mais figé, difficile à mettre à jour |
| **Sous-module Git** (*submodule*) | Un pointeur vers un autre dépôt | Propre… mais le code vit physiquement dans ton arborescence |
| **Clone externe + script** | Le code vit HORS du dépôt, un script le télécharge à une version épinglée | Le dépôt reste léger et net |

Nous avons commencé par un sous-module (`third_party/docile`), puis l'outil de
scan de sécurité du projet bloquait chaque commit à cause d'alertes sur **ce code
tiers** (des scripts de recherche de Rossum, jamais exécutés par notre produit).
Plutôt que de modifier du code qui ne nous appartient pas, nous avons opté pour
la troisième approche :

- le clone vit dans `../docile-upstream` (à côté du projet, hors du dépôt) ;
- il est **épinglé** à un commit précis (`45f1f00…`) pour la reproductibilité ;
- `scripts/fetch_docile.sh` permet de le récupérer à l'identique n'importe quand.

> 💡 **Leçons** : (1) le code tiers ne doit pas polluer l'audit de TON code ;
> (2) « épingler » une version tierce = pouvoir reproduire exactement ton
> environnement des années plus tard.

## 5. Conventional Commits : nos messages décryptés

Chaque message suit le format `type: résumé`. Types utilisés dans le projet :

| Type | Quand | Exemple réel du dépôt |
|---|---|---|
| `chore` | Tâches d'entretien, initialisation | `chore: initialisation du projet Warqa` |
| `build` | Environnement, construction | `build: environnement Docker du projet (conteneur docile officiel)` |
| `feat` | Nouvelle fonctionnalité | `feat: application de demo Warqa (phase 3)` |
| `fix` | Correction de bug | `fix: aligne le test de fumee sur l'API docile reelle` |
| `docs` | Documentation | `docs: evaluation officielle du baseline LayoutLMv3` |

Les versions du logiciel suivent le **Semantic Versioning** : `majeur.mineur.correctif`
(2.1.3 = 2e version majeure, 1re fonctionnalité, 3e correction).

## 6. Les commandes du quotidien

```bash
git status                 # qu'est-ce qui a changé ?
git add <fichier>          # préparer un fichier au commit
git commit -m "feat: ..."  # archiver avec un message
git push                   # envoyer vers GitHub
git log --oneline          # voir l'historique condensé
git diff                   # voir les modifications en cours
```

Règle appliquée dans le projet : **commit fréquent, push systématique** — un
travail non poussé est un travail qui peut disparaître.

## 7. Les vérifications avant chaque commit

Le projet utilise un **contrôle de sécurité** qui examine le code avant chaque
commit. Deux rencontres marquantes :
1. un script avec un chemin de sortie « non borné » a été refusé → réécrit avec un
   motif standard (sortie sur stdout, redirection à l'extérieur) ;
2. le code tiers a déclenché des alertes → résolu en le sortant du périmètre (§4).

> 💡 Ces contrôles sont des alliés : ils t'apprennent à écrire du code que des
> outils (et des relecteurs) considèrent comme sûr par construction.

## À retenir

- `.gitignore` AVANT le premier commit ; jamais de données massives ni de secrets.
- Commits petits, fréquents, messages `type: résumé`.
- Code tiers : clone externe épinglé par script, pas de copie sauvage.
- Un historique propre = un rapport de projet qui se raconte tout seul.

## Exercices

1. Lance `git log --oneline` et raconte l'histoire du projet à voix haute en
   60 secondes à partir des messages.
2. Simule : que se passerait-il si `data/` n'était pas dans `.gitignore` ?
   Quelle commande l'aurait révélé avant le commit ? *(Réponse : `git status`.)*
3. À quoi sert `scripts/fetch_docile.sh` si tu changes d'ordinateur ?
