# Cours 08 — Données réelles : collecte, annotation, conformité

**Objectifs** : comprendre pourquoi le modèle DocILE ne suffit pas, comment on
collecte et structure des données réelles marocaines, et quelles sont les règles
légales à respecter (loi 09-08 / CNDP).

---

## 1. Pourquoi le socle DocILE ne suffit pas

Le cours 06 s'est terminé sur la leçon centrale du benchmark : sur des **gabarits
jamais vus**, le F1 chute à 0,438. Or les factures marocaines sont des gabarits
jamais vus — avec en plus des spécificités locales : mentions **ICE**, **IF**,
**RC**, taux de TVA à 10/20 % (7 et 14 % sur les anciennes factures), cachets qui
chevauchent le texte, documents parfois bilingues.

Le raisonnement du projet est donc un **transfert** en deux temps :
1. apprendre la *logique des factures* sur le grand dataset public (fait) ;
2. **spécialiser** sur un petit dataset marocain annoté (à construire).

La valeur du petit dataset : 300 à 500 documents bien choisis valent mieux que
des milliers mal choisis. La diversité (secteurs, qualités, formats) prime sur la
quantité brute.

## 2. D'où viendront les documents réels

Quatre canaux, par ordre d'efficacité :

| Canal | Ce qu'on y gagne |
|---|---|
| **Partenariat fiduciaire** | Des années d'archives de dizaines de clients, tous secteurs — en échange d'une numérisation gratuite et d'un rapport |
| Réseau personnel | Photos de téléphone en conditions réelles (ombres, pliures) |
| Tickets de caisse grand public | Volume facile, peu sensible, idéal pour s'entraîner à annoter |
| Modèles téléchargeables | Complément de variété — **jamais** dans le jeu de test |

La sortie terrain a validé la douleur (saisie manuelle), précisé le périmètre
(factures en français, manuscrites écartées) et révélé une piste v2 (les relevés
bancaires — lecture de tableaux + classement des libellés).

## 3. La conformité : loi 09-08 et CNDP

Les factures contiennent des données d'identification (noms, ICE, adresses, parfois
plus). Au Maroc, le traitement de ces données est encadré par la **loi n° 09-08**
relative à la protection des personnes physiques à l'égard du traitement des
données à caractère personnel, sous le contrôle de la **CNDP** (Commission
Nationale de contrôle de la protection des Données à caractère Personnel).

Les principes appliqués dans le projet :

| Principe | Application concrète |
|---|---|
| **Consentement / base légale** | Un accord écrit d'une page signé pour CHAQUE source de documents |
| **Finalité** | Recherche et développement de l'outil uniquement — pas de revente, pas d'autre usage |
| **Minimisation** | On ne collecte que ce qui est utile (échantillons, pas d'archives complètes sans raison) |
| **Sécurité** | Stockage à accès limité, chiffrement prévu, hébergement au Maroc exigé en production |
| **Anonymisation avant diffusion** | Masquer noms, identifiants, signatures avant toute démonstration ou publication |
| **Droit de retrait** | Restitution ou destruction sécurisée à première demande |

> 💡 Ce n'est pas de la paperasse décorative : un seul incident de confidentialité
> ruinerait la confiance qu'on est en train de construire auprès des cabinets.

## 4. L'anatomie de l'accord d'une page

Le document remis aux cabinets (`docs/Warqa_Accord_Fourniture_Documents.docx`)
est volontairement **asymétrique en notre défaveur** — c'est ce qui le rend
crédible :

- **Article 2 — nos 7 engagements** (le cœur) : confidentialité stricte, usage
  exclusivement technique, aucun partage à un tiers, stockage sécurisé, masquage
  avant diffusion, conformité loi 09-08, restitution/destruction à la première demande ;
- **Article 4 — l'engagement du partenaire tient en une phrase** (fournir des
  documents dont il dispose légalement) ;
- **Article 3 — la contrepartie** : numérisation gratuite + rapport, accès
  prioritaire à l'outil, mention de partenaire pilote ;
- **Article 5 — sortie à tout moment, sans motif ni indemnité** ; aucune somme d'argent.

Le fiduciaire comprend en lisant qu'il ne signe **aucune contrainte** — et que
c'est nous qui nous engageons lourdement.

## 5. Quoi annoter : le schéma des champs

L'annotation, c'est écrire la vérité que le modèle apprendra. Le schéma Warqa
(≈ 20 champs d'en-tête + 6 par ligne) est **aligné sur les classes DocILE** pour
que le transfert soit direct :

| Groupe | Exemples de champs |
|---|---|
| Vendeur | nom, ICE, IF, RC, adresse |
| Client | nom, ICE/IF |
| Document | n° de facture, date d'émission, date d'échéance, référence |
| Montants | total HT, TVA (+taux), TTC, net à payer, devise |

Chaque champ annoté = **où** (boîte normalisée 0-1 + page) + **quoi** (texte
normalisé) — la même structure que DocILE (cours 02).

**Trois conventions à figer avant d'annoter** (sinon, incohérences garanties) :
1. **champ absent ≠ champ non trouvé** : si la facture n'a pas d'ICE, on le note
   explicitement ;
2. les **cachets** ne sont pas annotés, mais leur présence est signalée ;
3. les chiffres sont toujours transcrits en notation occidentale (`1234.56`).

## 6. L'effort réel (à planifier honnêtement)

| Phase | Volume | Effort |
|---|---|---|
| Pilote | 30 documents | ~1 journée — calibre le guide |
| Phase 1 (PoC) | 300–500 factures, en-têtes | 10–15 min/facture → **60 à 90 heures** |
| Phase 2 (lignes) | 100–150 documents | +30 à 40 heures |
| Jeu de test | 10–15 %, **gelé dès le départ** | jamais utilisé pour entraîner |

Outil recommandé : **Label Studio** (gratuit, spécialisé image + rectangles +
étiquettes, export JSON). Contrôle qualité : 10 % du corpus annoté deux fois.

## 7. Les pièges qui tuent une collecte

1. Annoter avant le pilote de 30 documents ;
2. Une seule source de documents (le modèle n'apprendrait qu'un fournisseur) ;
3. Écarter les documents moches — or ce sont eux le terrain réel ;
4. Mélanger test et entraînement (séparer par **source**, pas seulement par document) ;
5. Sous-estimer l'annotation des lignes de produits (commencer par les en-têtes).

## À retenir

- DocILE = la logique des factures ; le petit dataset marocain = la spécialisation.
- Diversité > quantité ; pilote de 30 avant l'effort massif.
- Loi 09-08 : consentement écrit, finalité unique, anonymisation, droit de retrait.
- L'accord est asymétrique volontairement : nos engagements lourds, les siens minimes.

## Exercices

1. Cite les trois conventions d'annotation et explique pourquoi la première
   (absent ≠ non trouvé) change les statistiques d'évaluation.
2. Un cabinet te propose 500 factures d'un seul et même fournisseur. Que réponds-tu ?
3. Pourquoi le jeu de test doit-il être séparé **par source** et pas seulement
   par document ?
