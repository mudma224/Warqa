# Projet Warqa — présentation

## En bref

Warqa est une plateforme web expérimentale qui convertit automatiquement des
factures et documents commerciaux (photos, scans, PDF) en données structurées,
vérifiées et exploitables pour la comptabilité. Son objectif est de supprimer
la saisie manuelle des pièces comptables et de préparer les entreprises à la
facturation électronique au Maroc.

## Problème

- Les factures fournisseurs parviennent aux entreprises et aux cabinets
  comptables sous forme papier ou PDF non structuré.
- Chaque pièce est saisie manuellement dans le logiciel comptable : plusieurs
  minutes par facture, des risques d'erreur, un travail récurrent.
- Le cadre réglementaire marocain évolue vers la facturation électronique
  obligatoire (réforme portée par la Direction Générale des Impôts), ce qui
  rend la numérisation du stock documentaire incontournable.

Constats de terrain intégrés au périmètre : les factures commerciales
marocaines sont rédigées en français ; les documents manuscrits sont écartés
du circuit comptable par les cabinets ; la saisie manuelle demeure la norme ;
le traitement des relevés bancaires constitue une douleur complémentaire
majeure.

## Solution

Parcours en six étapes :

1. Dépôt des documents par lots (photos, scans, PDF).
2. Classification automatique du type de document (facture, ticket, avoir,
   bon de livraison).
3. Lecture du texte (OCR).
4. Extraction des champs avec score de confiance.
5. Vérification humaine assistée : fiche remplie affichée à côté du document
   d'origine, zones reconnues surlignées, correction en un clic.
6. Export structuré (JSON, tableur, format d'échange de facturation) et
   archivage recherchable.

## Données extraites

- **Vendeur** : dénomination, ICE, identifiant fiscal, registre de commerce,
  adresse.
- **Client** : dénomination, ICE, identifiant fiscal.
- **Document** : numéro, date d'émission, date d'échéance, références de
  commande et de paiement.
- **Montants** : total HT, total TVA, total TTC, net à payer, devise.
- **Lignes de produits** : désignation, quantité, prix unitaire, montants,
  taux de TVA.

## Approche technique

1. **Socle** : apprentissage sur DocILE, jeu de données public de référence
   pour l'extraction d'informations de documents commerciaux (tâches KILE et
   LIR), accompagné d'OCR pré-calculé.
2. **Adaptation** : ré-entraînement sur un corpus de factures marocaines
   annotées en français, avec un schéma de champs aligné sur les classes
   DocILE pour permettre le transfert.
3. **Modèles** : transformateurs multimodaux pré-entraînés (famille
   LayoutXLM / LiLT), évaluation systématique sur des jeux de test gelés
   (F1 par champ, par type de document).
4. **Gouvernance** : score de confiance par champ, validation humaine
   obligatoire avant export, versions de modèles tracées et réversibles.

## Utilisateurs cibles

- **Principal** : cabinets comptables et fiduciaires.
- **Secondaire** : PME disposant d'une comptabilité interne.
- **Perspectives** : traitement des relevés bancaires et des tickets de
  caisse, extension à d'autres langues et à d'autres pays engagés dans la
  facturation électronique.

## Périmètre de la version 1

**Inclus** : factures fournisseurs imprimées en français (photos, scans,
PDF natifs), vérification humaine, export, archivage, gestion multi-dossiers
cloisonnée.

**Exclus** : factures manuscrites (hors circuit comptable), documents en
arabe (extension future), émission directe vers la plateforme de la DGI,
application mobile native, connecteurs temps réel vers les logiciels
comptables.

## Documentation associée

- Cahier des charges : `docs/Warqa_Cahier_des_Charges_v1.0.docx`
- Accord type de fourniture de données : `docs/Warqa_Accord_Fourniture_Documents.docx`
- Dataset DocILE : `data/docile/`
- Structure du dépôt et environnement d'exécution : `README.md`
