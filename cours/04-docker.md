# Cours 04 — Docker : exécuter le projet partout, sans casse-tête

**Objectifs** : comprendre ce qu'est une image Docker et un conteneur, savoir lire
le Dockerfile utilisé, et maîtriser les commandes quotidiennes du projet.

---

## 1. Le problème que Docker résout

Un projet d'IA dépend d'une pile d'outils précis : une version de Python, des
bibliothèques (leurs versions exactes !), des logiciels système (poppler pour
convertir les PDF en images)… Installer tout cela « en direct » sur une machine
mène à la phrase classique : *« mais ça marchait sur ma machine ! »*.

**Docker** emballe tout : le système, les outils, les dépendances, dans une
**image** — une recette figée et reproductible. Quand on **exécute** cette image,
on obtient un **conteneur** : un environnement isolé qui tourne pareil partout.

> 💡 **Analogie** : l'image est la **recette de cuisine complète avec les
> ingrédients dosés** ; le conteneur est le **plat préparé**. Tu peux cuisiner le
> même plat à Casablanca, Paris ou Tokyo, au gramme près.

## 2. Image vs conteneur (deux mots à ne pas confondre)

| | Image | Conteneur |
|---|---|---|
| C'est quoi | Un modèle figé, stocké sur disque | Une instance en cours d'exécution |
| Analogie | La recette | Le plat |
| Commande | `docker compose build` | `docker compose up -d` |
| Combien | Une seule | Autant qu'on veut |

Le projet a deux images : `warqa/docile` (l'atelier de travail) et `warqa/demo`
(la vitrine de démonstration, qui ajoute Streamlit par-dessus la première).

## 3. Lire le Dockerfile ligne par ligne

Le Dockerfile officiel de DocILE (`../docile-upstream/Dockerfile`) :

```dockerfile
FROM python:3.14
# ↑ On part de l'image officielle Python 3.14 (le "socle")

RUN apt-get update
RUN apt-get install poppler-utils -y
# ↑ On installe poppler, l'outil système qui convertit les PDF en images

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# ↑ On copie l'outil "uv" (gestionnaire de dépendances très rapide)
#   depuis une autre image — sans l'installer

ENV UV_PROJECT_ENVIRONMENT=/opt/docile-venv
# ↑ L'environnement virtuel sera rangé hors du dossier de travail

WORKDIR /app
# ↑ Le dossier de travail par défaut dans le conteneur

COPY uv.lock pyproject.toml /app/
COPY docile /app/docile
# ↑ On copie la définition des dépendances puis le code de la bibliothèque

RUN uv sync --locked --extra interactive
# ↑ On installe EXACTEMENT les versions verrouillées ("locked")
#   dans un fichier uv.lock — la clé de la reproductibilité
```

**Pourquoi c'est fort** : ce conteneur a résolu d'avance le problème n°1 de notre
planning (l'incompatibilité de version de Python) et il embarque poppler, qu'on
aurait dû installer manuellement péniblement sur Windows.

> 💡 `uv.lock` contient les versions **exactes** de toutes les bibliothèques.
> `--locked` = « refuse d'installer autre chose ». Deux personnes qui construisent
> l'image à six mois d'écart obtiennent le même environnement.

## 4. docker-compose.yml : la orchestration du projet

Le fichier `docker-compose.yml` décrit les **services** (conteneurs) du projet.
Celui du service de démonstration :

```yaml
  demo:
    build:
      context: ../docile-upstream     # (pour docile) où est la recette
      dockerfile: Demo.Dockerfile
    image: warqa/demo:latest          # le nom de l'image produite
    container_name: warqa-demo
    working_dir: /app/src/demo
    command: uv run --project /app streamlit run app.py ...
    volumes:                          # ← LA notion clé, voir §5
      - ./data/docile:/app/data/docile
      - ./models:/app/models
      - ./src:/app/src
    ports:
      - "8501:8501"                   # ouvrir le port 8501 vers l'extérieur
    deploy:
      resources:
        limits: { cpus: "4", memory: 8G }
```

## 5. Les volumes : des fenêtres vers ton disque

Un conteneur est **isolé** : par défaut il ne voit pas ton disque. Les `volumes`
créent des passerelles :

```
Ta machine                                   Le conteneur
C:\...\OCR-Projet\data\docile  ◄─────────►  /app/data/docile
C:\...\OCR-Projet\src           ◄─────────►  /app/src
C:\...\OCR-Projet\models        ◄─────────►  /app/models
```

Conséquences pratiques :
- tu modifies `src/demo/app.py` sur ton PC → le conteneur voit le changement
  immédiatement (pas de reconstruction) ;
- les données de 13 Go ne sont **pas copiées** dans l'image ;
- ce qui est écrit dans `/app/src` depuis le conteneur atterrit sur ton disque.

> ⚠️ Ce qui n'est PAS monté (ex. : le cache interne du conteneur) disparaît quand
> le conteneur est supprimé. Règle : tout ce qui doit survivre vit dans un volume.

## 6. Les commandes du quotidien

```bash
docker compose build                        # construire/rafraîchir les images
docker compose up -d                        # démarrer (arrière-plan)
docker compose exec docile uv run python scripts/smoke_test.py
                                            # exécuter une commande DANS le conteneur
docker compose restart demo                 # redémarrer un service
docker compose down                         # tout arrêter
curl http://localhost:8501/_stcore/health   # la démo est-elle vivante ? (HTTP 200)
```

Deux services, deux usages :
- `docile` (port 8888) : l'**atelier** — scripts, évaluations, exploration ;
- `demo` (port 8501) : la **vitrine** — l'application Streamlit à montrer.

## 7. Le piège Git Bash (rencontré pour de vrai)

Sous Windows, Git Bash « traduit » les chemins commençant par `/` : taper
`docker exec ls /app/models` devenait `ls C:/Program Files/Git/app/models` —
erreur incompréhensible tant qu'on ne connaît pas le piège. Solution : exporter
`MSYS_NO_PATHCONV=1` avant les commandes Docker, ou doubler les slashes (`//app`).

## 8. Ce que Docker nous a apporté concrètement

1. Zéro installation manuelle de Python/poppler/bibliothèques ;
2. Le même environnement chez toi, sur un autre PC, plus tard en production ;
3. Des versions **verrouillées** (`uv.lock`) — reproductibilité ;
4. Le nettoyage facile : supprimer un conteneur ne touche pas à ta machine.

## À retenir

- Image = recette ; conteneur = plat en cours.
- Le Dockerfile se lit comme une suite d'instructions de construction.
- Les volumes = passerelles vers ton disque ; les ports = fenêtres vers le réseau.
- `docker compose exec <service> <commande>` = ta porte d'entrée quotidienne.

## Exercices

1. Quelle commande vérifie que la démo tourne sans ouvrir de navigateur ?
2. Tu modifies `app.py` : faut-il reconstruire l'image ? *(Réponse : non — `src/`
   est un volume, un simple rechargement de la page suffit.)*
3. À quoi sert `uv.lock` et que garantirait son absence ?
