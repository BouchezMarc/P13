from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService
from app.services.milvus_service import MilvusService
from app.services.youtube_service import YouTubeService
from app.services.chess_context_service import ChessContextService


# ============================================================
# ÉTAT DU GRAPHE
# ============================================================

class ServiceResult(TypedDict, total=False):
    status: str
    message: str
    data: object


class ChessState(TypedDict, total=False):
    fen: str

    lichess: dict
    stockfish: dict
    chess_context: dict
    milvus: dict
    youtube: dict


# ============================================================
# SERVICES
# ============================================================

lichess_service = LichessService()
stockfish_service = StockfishService()
milvus_service = MilvusService()
youtube_service = YouTubeService()
chess_context_service = ChessContextService()


# ============================================================
# LICHESS
# ============================================================

async def search_lichess(state: ChessState):

    try:

        data = await lichess_service.get_opening_moves(
            state["fen"]
        )

        moves = data.get(
            "moves",
            []
        )

        # ----------------------------------------------------
        # LICHESS A RÉPONDU MAIS AUCUNE THÉORIE
        # ----------------------------------------------------

        if not moves:

            return {
                "lichess": {
                    "status": "empty",
                    "message": "Aucune théorie trouvée dans Lichess",
                    "data": data,
                }
            }

        # ----------------------------------------------------
        # LICHESS A TROUVÉ UNE RÉPONSE
        # ----------------------------------------------------

        return {
            "lichess": {
                "status": "response",
                "message": "Théorie trouvée dans Lichess",
                "data": data,
            }
        }

    except Exception as exc:

        return {
            "lichess": {
                "status": "error",
                "message": str(exc),
                "data": {},
            }
        }


# ============================================================
# ROUTAGE LICHESS
# ============================================================

def route_after_lichess(state: ChessState):

    lichess = state.get(
        "lichess",
        {}
    )

    # --------------------------------------------------------
    # LICHESS A UNE RÉPONSE
    #
    # On ne lance PAS Stockfish.
    # --------------------------------------------------------

    if lichess.get("status") == "response":

        return "context"

    # --------------------------------------------------------
    # LICHESS EMPTY OU ERROR
    #
    # On utilise Stockfish.
    # --------------------------------------------------------

    return "stockfish"


# ============================================================
# STOCKFISH
# ============================================================

def evaluate_stockfish(state: ChessState):

    try:

        data = stockfish_service.evaluate(
            state["fen"]
        )

        # ----------------------------------------------------
        # STOCKFISH N'A RIEN RETOURNÉ
        # ----------------------------------------------------

        if not data:

            return {
                "stockfish": {
                    "status": "empty",
                    "message": "Aucune évaluation retournée par Stockfish",
                    "data": {},
                }
            }

        # ----------------------------------------------------
        # STOCKFISH A RÉPONDU
        # ----------------------------------------------------

        return {
            "stockfish": {
                "status": "response",
                "message": "Évaluation Stockfish obtenue",
                "data": data,
            }
        }

    except Exception as exc:

        return {
            "stockfish": {
                "status": "error",
                "message": str(exc),
                "data": {},
            }
        }


# ============================================================
# CONSTRUCTION DU CONTEXTE
# ============================================================

def build_chess_context(state: ChessState):

    context = chess_context_service.build(
        fen=state["fen"],
        lichess=state.get(
            "lichess"
        ),
        stockfish=state.get(
            "stockfish"
        ),
    )

    return {
        "chess_context": context
    }


# ============================================================
# MILVUS
# ============================================================
def search_milvus(state: ChessState):

    try:

        # ========================================================
        # 1. DONNÉES BRUTES AVANT TRANSFORMATION
        # ========================================================

        if state.get("lichess", {}).get("status") == "response":

            source = "lichess"
            raw_data = state["lichess"].get("data", {})

        elif state.get("stockfish", {}).get("status") == "response":

            source = "stockfish"
            raw_data = state["stockfish"].get("data", {})

        else:

            return {
                "milvus": {
                    "status": "empty",
                    "message": "Aucune donnée disponible pour construire le contexte Milvus",
                    "data": [],
                }
            }

        print("\n" + "=" * 70)
        print("AVANT TRANSFORMATION")
        print("=" * 70)
        print(f"Source : {source}")
        print(raw_data)


        # ========================================================
        # 2. TRANSFORMATION EN CONTEXTE
        # ========================================================

        context = chess_context_service.build(
            fen=state["fen"],
            lichess=state.get("lichess"),
            stockfish=state.get("stockfish"),
)


        # ========================================================
        # 3. CONTEXTE APRÈS TRANSFORMATION
        # ========================================================

        print("\n" + "=" * 70)
        print("APRÈS TRANSFORMATION")
        print("=" * 70)
        print(context)


        # ========================================================
        # 4. REQUÊTE MILVUS
        # ========================================================

        query = context.get("query", "")

        print("\n" + "=" * 70)
        print("REQUÊTE ENVOYÉE À MILVUS")
        print("=" * 70)
        print(query)


        if not query:

            return {
                "milvus": {
                    "status": "empty",
                    "message": "Contexte sans requête exploitable pour Milvus",
                    "data": [],
                }
            }


        results = milvus_service.search(
            query=query,
            limit=5,
        )


        if not results:

            return {
                "milvus": {
                    "status": "empty",
                    "message": "Aucun résultat trouvé dans Milvus",
                    "data": [],
                }
            }


        return {
            "milvus": {
                "status": "response",
                "message": "Résultats Milvus trouvés",
                "data": results,
            }
        }


    except Exception as exc:

        return {
            "milvus": {
                "status": "error",
                "message": str(exc),
                "data": [],
            }
        }

# ============================================================
# YOUTUBE
# ============================================================
async def search_youtube(state: ChessState):

    try:

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        if not youtube_service.api_key:

            return {
                "youtube": {
                    "status": "error",
                    "message": "Clé API YouTube absente ou invalide",
                    "data": [],
                }
            }

        # ----------------------------------------------------
        # RÉSULTATS MILVUS
        # ----------------------------------------------------

        milvus = state.get(
            "milvus",
            {}
        )

        milvus_data = milvus.get(
            "data",
            []
        )

        # ----------------------------------------------------
        # MILVUS N'A PAS DE RÉSULTAT
        # ----------------------------------------------------

        if not milvus_data:

            return {
                "youtube": {
                    "status": "empty",
                    "message": "Aucune donnée Milvus disponible pour rechercher des vidéos",
                    "data": [],
                }
            }

        # ----------------------------------------------------
        # PREMIER RÉSULTAT MILVUS
        # ----------------------------------------------------

        first_result = milvus_data[0]

        title = first_result.get(
            "title",
            ""
        )

        opening = first_result.get(
            "opening",
            ""
        )

        # ----------------------------------------------------
        # AUCUNE INFORMATION EXPLOITABLE
        # ----------------------------------------------------

        if not title and not opening:

            return {
                "youtube": {
                    "status": "empty",
                    "message": "Aucune ouverture exploitable pour rechercher des vidéos",
                    "data": [],
                }
            }

        # ----------------------------------------------------
        # YOUTUBE
        #
        # La requête sera :
        # title + opening + chess
        #
        # Exemple :
        # "Ouverture italienne Italian Game chess"
        # ----------------------------------------------------

        videos = youtube_service.search_videos(
            title=title,
            opening=opening,
            limit=5,
        )

        # ----------------------------------------------------
        # AUCUNE VIDÉO
        # ----------------------------------------------------

        if not videos:

            return {
                "youtube": {
                    "status": "empty",
                    "message": "Aucune vidéo trouvée",
                    "data": [],
                }
            }

        # ----------------------------------------------------
        # VIDÉOS TROUVÉES
        # ----------------------------------------------------

        return {
            "youtube": {
                "status": "response",
                "message": "Vidéos trouvées",
                "data": videos,
            }
        }

    except Exception as exc:

        return {
            "youtube": {
                "status": "error",
                "message": str(exc),
                "data": [],
            }
        }


# ============================================================
# CONSTRUCTION DU GRAPHE
# ============================================================

graph_builder = StateGraph(
    ChessState
)


# ============================================================
# NODES
# ============================================================

graph_builder.add_node(
    "lichess",
    search_lichess
)

graph_builder.add_node(
    "stockfish",
    evaluate_stockfish
)

graph_builder.add_node(
    "context",
    build_chess_context
)

graph_builder.add_node(
    "milvus",
    search_milvus
)

graph_builder.add_node(
    "youtube",
    search_youtube
)


# ============================================================
# ENTRY POINT
# ============================================================

graph_builder.set_entry_point(
    "lichess"
)


# ============================================================
# LICHESS
#
# response → context
# empty    → stockfish
# error    → stockfish
# ============================================================

graph_builder.add_conditional_edges(
    "lichess",
    route_after_lichess,
    {
        "stockfish": "stockfish",
        "context": "context",
    },
)


# ============================================================
# STOCKFISH → CONTEXT
# ============================================================

graph_builder.add_edge(
    "stockfish",
    "context"
)


# ============================================================
# CONTEXT → MILVUS
# ============================================================

graph_builder.add_edge(
    "context",
    "milvus"
)


# ============================================================
# MILVUS → YOUTUBE
#
# Toujours, même si Milvus retourne une erreur.
# ============================================================

graph_builder.add_edge(
    "milvus",
    "youtube"
)


# ============================================================
# YOUTUBE → END
# ============================================================

graph_builder.add_edge(
    "youtube",
    END
)


# ============================================================
# COMPILATION
# ============================================================

graph = graph_builder.compile()



# from typing import TypedDict

# from langgraph.graph import StateGraph, END

# from app.services.lichess_service import LichessService
# from app.services.stockfish_service import StockfishService
# from app.services.milvus_service import MilvusService
# from app.services.youtube_service import YouTubeService


# class ChessState(TypedDict, total=False):
#     fen: str
#     lichess_data: dict
#     theoretical: bool
#     stockfish_data: dict
#     milvus_data: list
#     youtube_data: list
#     opening: str
#     error: str


# lichess_service = LichessService()
# stockfish_service = StockfishService()
# youtube_service = YouTubeService()


# async def search_lichess(state: ChessState):
#     try:
#         data = await lichess_service.get_opening_moves(
#             state["fen"]
#         )

#         moves = data.get("moves", [])

#         return {
#             "lichess_data": data,
#             "theoretical": len(moves) > 0,
#         }

#     except Exception as exc:
#         return {
#             "error": f"Lichess error: {exc}",
#             "theoretical": False,
#         }


# def evaluate_stockfish(state: ChessState):
#     try:
#         data = stockfish_service.evaluate(
#             state["fen"]
#         )

#         return {
#             "stockfish_data": data,
#         }

#     except Exception as exc:
#         return {
#             "error": f"Stockfish error: {exc}",
#         }


# def route_after_lichess(state: ChessState):
#     if state.get("theoretical"):
#         return "milvus"

#     return "stockfish"


# def search_milvus(state: ChessState):
#     try:
#         milvus_service = MilvusService()

#         if state.get("theoretical"):
#             query = str(
#                 state.get("lichess_data", {})
#             )
#         else:
#             query = str(
#                 state.get("stockfish_data", {})
#             )

#         results = milvus_service.search(
#             query=query,
#             limit=5,
#         )

#         return {
#             "milvus_data": results,
#         }

#     except Exception as exc:
#         return {
#             "error": f"Milvus error: {exc}",
#             "milvus_data": [],
#         }


# async def search_youtube(state: ChessState):
#     try:
#         if not youtube_service.api_key:
#             return {
#                 "youtube_data": [],
#                 "error": "Clé API YouTube non valide ou absente",
#             }

#         milvus_data = state.get(
#             "milvus_data",
#             []
#         )

#         if not milvus_data:
#             return {
#                 "youtube_data": []
#             }

#         query = milvus_data[0].get(
#             "text",
#             "chess opening"
#         )

#         videos = await youtube_service.search_videos(
#             query
#         )

#         return {
#             "youtube_data": videos,
#         }

#     except Exception as exc:
#         return {
#             "youtube_data": [],
#             "error": f"Erreur YouTube : {exc}",
#         }


# graph_builder = StateGraph(ChessState)

# graph_builder.add_node(
#     "lichess",
#     search_lichess
# )

# graph_builder.add_node(
#     "stockfish",
#     evaluate_stockfish
# )

# graph_builder.add_node(
#     "milvus",
#     search_milvus
# )

# graph_builder.add_node(
#     "youtube",
#     search_youtube
# )

# graph_builder.set_entry_point(
#     "lichess"
# )

# graph_builder.add_conditional_edges(
#     "lichess",
#     route_after_lichess,
#     {
#         "stockfish": "stockfish",
#         "milvus": "milvus",
#     },
# )

# graph_builder.add_edge(
#     "stockfish",
#     "milvus"
# )

# graph_builder.add_edge(
#     "milvus",
#     END
# )

# graph = graph_builder.compile()