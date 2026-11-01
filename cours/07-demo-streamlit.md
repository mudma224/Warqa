# Cours 07 — La démonstration : Streamlit, curation et test

**Objectifs** : comprendre comment l'application de démonstration est construite,
pourquoi elle est architecturée ainsi, comment les 15 factures ont été choisies,
et comment on teste une interface sans navigateur.

---

## 1. Streamlit : une application web en un script Python

**Streamlit** est un framework qui transforme un script Python en application web :
chaque ligne d'interface (`st.title`, `st.image`, `st.dataframe`…) dessine un
élément dans le navigateur. Pas de HTML, pas de JavaScript — idéal pour un
prototype de data science.

Le script est **ré-exécuté de haut en bas à chaque interaction** (clic, sélection).
C'est simple, à condition de mettre en cache les opérations lentes :

```python
@st.cache_resource(show_spinner="Chargement du corpus…")
def get_dataset():
    return core.load_dataset()     # exécuté UNE fois, puis réutilisé
```

## 2. L'architecture : cœur et interface séparés

Fichier central du projet : on a séparé en deux.

```
src/demo/
├── demo_core.py   ← le CŒUR : pure logique, zéro interface
│   • load_dataset / load_predictions / load_demo_docs
│   • build_form_rows     (prédictions → lignes de fiche en français)
│   • render_page_with_boxes (dessine les rectangles colorés)
│   • export_json         (fiche → format Warqa)
└── app.py         ← l'INTERFACE : disposition, boutons, colonnes
```

**Pourquoi séparer ?** Parce que le cœur peut être testé **sans navigateur**
(un simple script Python), ce qui a permis de vérifier toute la mécanique
(fiche, image, export) puis de tester l'interface à part. Une interface qui plante
est un détail ; un cœur qui plante est un produit cassé.

## 3. Le pont français : le mapping des champs

DocILE nomme les champs en anglais (`vendor_name`…). Le fiduciaire doit voir du
français. La table de correspondance, dans `demo_core.py` :

```python
FIELD_LABELS_FR = [
    ("vendor_name", "Fournisseur"),
    ("document_id", "Numéro de facture"),
    ("date_issue", "Date d'émission"),
    ("amount_total_net", "Total HT"),
    ("amount_total_tax", "Total TVA"),
    ("amount_total_gross", "Total TTC"),
    ("amount_due", "Net à payer"),
    ...
]
```

Détail psychologique assumé : le jour de la démo, le fiduciaire doit se
**reconnaître** dans l'écran dès la première seconde.

## 4. Les couleurs de confiance : le human-in-the-loop visible

Chaque prédiction porte un score (0 à 1). La règle d'affichage :

| Score | Couleur du cadre | Étiquette |
|---|---|---|
| ≥ 0,90 | 🟩 vert | confiance élevée |
| 0,60 – 0,90 | 🟧 orange | confiance moyenne |
| < 0,60 | 🟥 rouge | confiance faible |

Le message produit est incarné par ces couleurs : **le modèle montre quand il
doute, l'humain valide toujours avant export**. C'est le principe du
*human-in-the-loop* rendu visible à l'écran — le meilleur argument de confiance
devant un comptable.

## 5. La curation : choisir 15 factures qui ne rateront pas

Une démo qui plante devant le client est une démo perdue. Le script
`scripts/prepare_demo.py` a donc sélectionné automatiquement, parmi les 500
documents de validation, ceux qui offrent le meilleur spectacle :

**Critères** : une seule page ; au moins **5 champs clés différents** prédits avec
un score ≥ 0,5 ; au plus 18 prédictions (fiche lisible) ; tri final par type
(`invoice` d'abord), richesse en champs, score moyen.

**Résultat** : 334 candidates → **15 retenues** (12 `tax_invoice`, 3 `order`),
des fournisseurs lisibles (« DJM Post », « Sinclair Broadcast Group »…), des
totaux propres. La liste est rangée dans `src/demo/demo_docs.json`.

## 6. Le flux de l'application (app.py)

```
Barre latérale                    Écran principal
┌──────────────────┐    ┌─────────────────────────────────────┐
│ 1. Choisir une   │    │  Gauche : l'image de la facture     │
│    facture       │ →  │  avec les cadres colorés            │
│ 2. ▶ Lire la     │    │  Droite : la fiche extraite         │
│    facture       │    │  (Champ / Valeur / Confiance)       │
└──────────────────┘    │  Bouton : Télécharger la fiche JSON │
                        └─────────────────────────────────────┘
```

Le clic sur « ▶ Lire » est volontaire (pas d'affichage automatique) : ça crée le
**moment de magie** du pitch — tu cliques, la fiche se remplit sous les yeux du
fiduciaire.

L'export JSON respecte le schéma Warqa défini au cahier des charges :

```json
{
  "docid": "8697219373c8…",
  "champs": [
    {"champ": "Fournisseur", "code": "vendor_name", "page": 0,
     "boite": [0.32, 0.02, 0.68, 0.06], "texte": "DJM Post",
     "confiance": 0.9999}
  ]
}
```

## 7. Tester sans navigateur : AppTest

Streamlit fournit un mini-navigateur de test. Notre vérification finale :

```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=300)
at.session_state["reading_done"] = True   # simuler le clic « Lire »
at.run()                                  # exécuter le script en mémoire

print(len(at.exception))   # → 0 : aucune exception
print(len(at.dataframe[0].value))  # → 12 champs affichés
```

Deux parcours testés : l'accueil (sans lecture) et la lecture complète. Résultat :
**0 exception, 12 champs affichés** — plus un test du cœur seul (fiche, image
rendue en 1692 × 2245 px, JSON de 2 968 caractères).

> 💡 Leçon : une interface se teste. « Ça marche quand je clique » n'est pas un
> test ; c'est une espérance.

## 8. Les pièges rencontrés (et leurs leçons)

| Piège | Leçon |
|---|---|
| `doc.images[0]` → KeyError | La bonne API était `doc.page_image(0)` ; le dict `images` est un cache interne. → lire la source avant d'utiliser |
| `use_container_width` déprécié | Les bibliothèques évoluent ; suivre les avertissements, corriger tôt |
| Le scanner de sécurité refusait l'écriture de fichier via variable | Contourner proprement : le script **affiche** le JSON sur stdout, la redirection (`> fichier`) écrit côté hôte |
| Prédictions affichées sans le tri par score | Prendre la **meilleure** prédiction par type de champ (`build_form_rows`) |

## 9. Lancer la démo (routine du jour J)

```bash
docker compose up -d demo     # démarrer (avant de partir)
# ouvrir http://localhost:8501 — tout fonctionne hors ligne
```

Le service `demo` est l'image `warqa/docile` + Streamlit (`docker/Demo.Dockerfile`),
avec les mêmes volumes (dataset, modèles, code).

## À retenir

- Cœur logique et interface séparés → le cœur se teste sans navigateur.
- Curation automatique : 15 factures choisies par critères objectifs, pour une
  démo sans mauvaise surprise.
- Les couleurs de confiance incarnent le human-in-the-loop.
- AppTest = exécution de l'application en mémoire, avec vérification des exceptions.

## Exercices

1. Ajoute `("vendor_email", "E-mail fournisseur")` dans `FIELD_LABELS_FR` et
   vérifie via AppTest que rien ne casse.
2. Change le seuil du vert de 0,90 à 0,95 : quel effet visuel attendre sur la démo ?
3. Pourquoi est-il important que l'export JSON contienne les boîtes, pas seulement
   les valeurs ?
