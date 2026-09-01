# Chess Agent

Application d'analyse et d'assistance aux échecs composée d'un frontend Angular, d'un backend FastAPI et de services conteneurisés avec Docker Compose.

Le projet permet de jouer une position sur un échiquier interactif, de transmettre la position au backend sous forme de FEN et d'obtenir des informations issues des différents services d'analyse.

---
# 1. Architecture
```text
                         ┌──────────────────────┐
                         │       FRONTEND       │
                         │       Angular        │
                         │                      │
                         │  Échiquier interactif│
                         └──────────┬───────────┘
                                    │
                              HTTP / FEN
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       BACKEND        │
                         │       FastAPI        │
                         │                      │
                         │      LangGraph       │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
         Lichess                Stockfish               MongoDB
        Théorie                 Analyse                 Données
             │                      │
             └──────────┬───────────┘
                        │
                        ▼
                 Chess Context
                        │
                        ▼
                     Milvus
               Recherche vectorielle
                        │
                        ▼
                    YouTube
                Recherche de vidéos
```
Le backend constitue le point central de l'application.
Le frontend communique uniquement avec l'API backend. Les différents services sont ensuite appelés depuis le backend.

---
# 2. Technologies

## Frontend
- Angular    
- TypeScript    
- ngx-chessground    
- chess.js    

Le frontend fournit notamment :
- un échiquier interactif ;    
- la possibilité de jouer des coups ;    
- la gestion de la position ;    
- la génération de la FEN ;    
- la communication avec l'API backend ;    
- l'affichage des résultats.

## Backend
- Python
- FastAPI
- Uvicorn
- LangGraph  
- python-chess 
- PyMilvus
- MongoDB
- Stockfish

Le backend assure :
- l'exposition de l'API REST ;
- la validation des positions FEN ;
- l'orchestration des services ;
- la construction du contexte échiquéen ;
- la recherche vectorielle ;
- la recherche vidéo.

## Services externes
### Lichess
Lichess permet d'obtenir des informations théoriques sur une position :
- ouverture ;
- ECO ;
- coups théoriques ;
- statistiques disponibles.

### YouTube
L'API YouTube est utilisée pour rechercher des vidéos correspondant au contexte échiquéen.

### Stockfish
Stockfish permet d'obtenir une analyse moteur :
- meilleur coup ;    
- évaluation ;    
- profondeur.

Stockfish est un moteur d'échecs et non un modèle de Machine Learning.
## Stockage

### MongoDB
MongoDB est utilisé pour la persistance des données applicatives/conversations selon les besoins du projet.

### Milvus
Milvus est utilisé pour la recherche vectorielle.

La collection actuelle est :
```text
chess_openings
```

Le modèle d'embedding utilisé est :
```text
sentence-transformers/all-MiniLM-L6-v2
```

avec des vecteurs de dimension :
```text
384
```
---
# 3. Structure du projet
```text
projet13/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── agent/
│   │   │   └── graph.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   └── services/
│   │       ├── chess_context_service.py
│   │       ├── lichess_service.py
│   │       ├── milvus_service.py
│   │       ├── mongo_service.py
│   │       ├── stockfish_service.py
│   │       └── youtube_service.py
│   │
│   ├── data/
│   │   └── openings.json
│   │
│   ├── scripts/
│   │   ├── load_milvus.py
│   │   └── show_graph.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── index.html
│   │   ├── main.ts
│   │   ├── styles.css
│   │   │
│   │   └── app/
│   │       ├── app.ts
│   │       ├── app.html
│   │       ├── app.css
│   │       ├── app.config.ts
│   │       ├── app.routes.ts
│   │       │
│   │       ├── components/
│   │       │   └── chess-board/
│   │       │       ├── chess-board.ts
│   │       │       ├── chess-board.html
│   │       │       ├── chess-board.css
│   │       │       └── chess-board.spec.ts
│   │       │
│   │       └── services/
│   │           ├── chess-api.ts
│   │           ├── chess-api.service.ts
│   │           └── chess-api.spec.ts
│   │
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── angular.json
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml
├── package.json
├── package-lock.json
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```
---
# 4. Backend

Le point d'entrée du backend est :
```text
backend/app/main.py
```

Les routes HTTP sont définies dans :
```text
backend/app/api/routes.py
```
Le backend utilise FastAPI pour exposer les fonctionnalités à l'application Angular.

---
# 5. Gestion de la position

La position de l'échiquier est représentée par une FEN.

Le fonctionnement général est :
```text
Joueur
  ↓
Coup joué sur l'échiquier
  ↓
Nouvelle position
  ↓
FEN
  ↓
Frontend Angular
  ↓
API FastAPI
```
Le backend reçoit ensuite cette FEN et peut déclencher les différents services.

---
# 6. Orchestration LangGraph

L'orchestration actuelle est réalisée dans :
```text
backend/app/agent/graph.py
```

Le graphe suit actuellement une logique conditionnelle :
```text
                         FEN
                          │
                          ▼
                     ┌─────────┐
                     │ Lichess │
                     └────┬────┘
                          │
                ┌─────────┴─────────┐
                │                   │
           théorie trouvée      pas de théorie
                │                   │
                ▼                   ▼
             Context            Stockfish
                │                   │
                └─────────┬─────────┘
                          ▼
                       Context
                          │
                          ▼
                        Milvus
                          │
                          ▼
                       YouTube
```
### Lichess
Si Lichess fournit une théorie correspondant à la position, le graphe utilise cette information pour construire le contexte.

### Stockfish
Si Lichess ne fournit pas de théorie ou retourne une erreur, Stockfish est utilisé comme solution alternative.

### ChessContextService
Le service :
```text
chess_context_service.py
```
normalise les informations provenant de Lichess ou Stockfish afin de construire un contexte exploitable par les étapes suivantes.
### Milvus
Le contexte construit est transformé en requête destinée à Milvus.

Milvus retourne les documents les plus proches sémantiquement.
### YouTube
Les résultats Milvus sont ensuite utilisés pour construire une recherche de vidéos YouTube.

---
# 7. Services backend

Les services sont regroupés dans :
```text
backend/app/services/
```
## `lichess_service.py`
Communication avec Lichess pour récupérer les informations théoriques d'une position.

## `stockfish_service.py`
Analyse de la position avec Stockfish.

## `chess_context_service.py`
Construction et normalisation du contexte utilisé par les services suivants.

## `milvus_service.py`
Connexion à Milvus, création/chargement de la collection, insertion des embeddings et recherche vectorielle.

## `mongo_service.py`
Gestion de la connexion et des opérations liées à MongoDB.

## `youtube_service.py`
Recherche de vidéos YouTube à partir du contexte échiquéen.

---
# 8. MongoDB
MongoDB constitue le stockage documentaire du projet.

Il est utilisé par :
```text
backend/app/services/mongo_service.py
```

MongoDB est adapté au stockage de données dont la structure peut évoluer et permet notamment de conserver des documents JSON.

Il est distinct de Milvus :
```text
MongoDB
   ↓
Données / documents

Milvus
   ↓
Embeddings / recherche vectorielle
```
Les deux technologies ont donc des rôles différents.

---
# 9. Milvus

Milvus est utilisé pour la recherche par similarité vectorielle.

Les documents d'ouverture sont chargés depuis :
```text
backend/data/openings.json
```

Le script d'initialisation se trouve dans :
```text
backend/scripts/load_milvus.py
```

Pour charger les données dans Milvus :
```bash
docker compose exec backend python /app/scripts/load_milvus.py
```

La recherche utilise actuellement :
```text
Metric : COSINE
Embedding : all-MiniLM-L6-v2
Dimension : 384
```
Milvus est utilisé pour une recherche sémantique et ne doit pas être considéré comme une recherche exacte de FEN.

---
# 10. API Backend

Un exemple d'endpoint est :
```text
GET /api/v1/moves/{fen}
```

La FEN est transmise au backend afin de déclencher l'analyse.

Exemple :
```text
GET /api/v1/moves/rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR%20w%20KQkq%20-%200%202
```
Le backend valide la position puis lance le traitement défini dans le graphe.

---
# 11. Frontend Angular

Le frontend est situé dans :
```text
frontend/
```

Le composant principal de l'échiquier est :
```text
frontend/src/app/components/chess-board/
```

Il contient :
```text
chess-board.ts
chess-board.html
chess-board.css
chess-board.spec.ts
```
La communication avec l'API backend est regroupée dans :

```text
frontend/src/app/services/
```

notamment :
```text
chess-api.ts
chess-api.service.ts
```
---

# 12. Communication Angular → FastAPI

Le flux utilisateur est :
```text
┌──────────────┐
│    Joueur    │
└──────┬───────┘
       │ joue un coup
       ▼
┌──────────────┐
│   Angular    │
│  Échiquier   │
└──────┬───────┘
       │ FEN
       ▼
┌──────────────┐
│   FastAPI    │
└──────┬───────┘
       ▼
   LangGraph
       │
       ▼
 Services
       │
       ▼
   Résultats
       │
       ▼
    Angular
```
---
# 13. Docker

Le projet utilise Docker Compose pour orchestrer l'environnement.

Le fichier principal est :
```text
docker-compose.yml
```

Le backend possède son propre Dockerfile :
```text
backend/Dockerfile
```

Le frontend possède également son propre Dockerfile :
```text
frontend/Dockerfile
```

Le frontend utilise Nginx pour servir l'application Angular compilée.

Sa configuration est définie dans :
```text
frontend/nginx.conf
```
---
# 14. Démarrage

## Prérequis

Installer :
- Docker    
- Docker Compose    

Vérifier l'installation :
```bash
docker --version
docker compose version
```
## Démarrer les services

Depuis la racine du projet :
```bash
docker compose up -d
```

Pour reconstruire les images :
```bash
docker compose up -d --build
```

Pour forcer la recréation :
```bash
docker compose up -d --force-recreate
```

Pour reconstruire et recréer :
```bash
docker compose up -d --build --force-recreate
```
---
# 15. Vérification des conteneurs

```bash
docker compose ps
```

Logs du backend :
```bash
docker compose logs -f backend
```

Logs du frontend :
```bash
docker compose logs -f frontend
```

Logs de Milvus :
```bash
docker compose logs -f milvus
```
---
# 16. Documentation FastAPI

FastAPI fournit une documentation interactive de l'API.

Une fois le backend démarré :
```text
/docs
```
La documentation permet de tester directement les endpoints disponibles.

---
# 17. Configuration

La configuration du backend est principalement regroupée dans :
```text
backend/app/core/config.py
```

Les variables d'environnement sensibles sont définies dans :
```text
backend/.env
```
Les secrets et clés API ne doivent pas être intégrés directement dans le code source.

---
# 18. Scripts

Le dossier :
```text
backend/scripts/
```
contient des scripts utilitaires.
### Chargement de Milvus
```bash
docker compose exec backend python /app/scripts/load_milvus.py
```
### Visualisation du graphe
```bash
docker compose exec backend python /app/scripts/show_graph.py
```
Ce script permet notamment d'inspecter la structure du graphe LangGraph.

---
# 19. Arrêt
Pour arrêter les conteneurs :
```bash
docker compose down
```

Pour arrêter les conteneurs et supprimer les volumes :
```bash
docker compose down -v
```
**Attention : la suppression des volumes peut entraîner la perte des données persistantes.**

---
# 20. Vue d'ensemble du projet
```text
				 UTILISATEUR
					  ▼
			 ┌────────────────┐
			 │ Angular /      │
			 │ Échiquier      │
			 └───────┬────────┘
					FEN
					 ▼
			 ┌────────────────┐
			 │    FastAPI     │
			 │    Backend     │
			 └───────┬────────┘
			   LangGraph
	  ┌──────────────┼──────────────┐
	  │              │              │
	  ▼              ▼              ▼
  Lichess        Stockfish       Context
	  │              │              │
	  └──────────────┴──────┬───────┘
							▼
						 Milvus
							▼
						YouTube

			 ┌──────────────┐
			 │   MongoDB    │
			 │   Données    │
			 └──────────────┘
```

Le projet sépare ainsi les responsabilités entre :
- **Angular** : interface et échiquier ;    
- **FastAPI** : API backend ;    
- **LangGraph** : orchestration du traitement ;    
- **MongoDB** : stockage documentaire ;    
- **Milvus** : recherche vectorielle ;    
- **Lichess** : données théoriques ;    
- **Stockfish** : analyse moteur ;    
- **YouTube** : recherche de vidéos ;    
- **Docker Compose** : orchestration de l'environnement.