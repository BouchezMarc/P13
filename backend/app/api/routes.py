import chess

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.graph import graph
from app.services.milvus_service import MilvusService
from app.services.youtube_service import YouTubeService
from app.services.mongo_service import MongoService


router = APIRouter(prefix="/api/v1")

mongo_service = MongoService()


# ============================================================
# Modèles MongoDB
# ============================================================

class MoveRequest(BaseModel):
    from_square: str
    to_square: str
    san: str
    fen: str


# ============================================================
# Validation FEN
# ============================================================

def validate_fen(fen: str):
    try:
        return chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"FEN invalide : {exc}",
        )


# ============================================================
# MONGO : créer une partie
# ============================================================

@router.post("/games")
async def create_game():
    try:
        board = chess.Board()

        game_id = mongo_service.create_game(
            initial_fen=board.fen()
        )

        return {
            "game_id": game_id,
            "initial_fen": board.fen(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur MongoDB : {exc}",
        )


# ============================================================
# MONGO : enregistrer un coup
# ============================================================

@router.post("/games/{game_id}/moves")
async def add_move(game_id: str, move: MoveRequest):

    validate_fen(move.fen)

    try:
        mongo_service.add_move(
            game_id=game_id,
            move_data={
                "from": move.from_square,
                "to": move.to_square,
                "san": move.san,
                "fen": move.fen,
            },
        )

        return {
            "status": "ok",
            "message": "Coup enregistré",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur MongoDB : {exc}",
        )


# ============================================================
# MONGO : terminer une partie
# ============================================================

@router.post("/games/{game_id}/end")
async def end_game(game_id: str):

    try:
        mongo_service.end_game(game_id)

        return {
            "status": "ok",
            "message": "Partie terminée",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur MongoDB : {exc}",
        )


# ============================================================
# ÉCHECS : analyse complète
# ============================================================

@router.get("/moves/{fen:path}")
async def get_moves(fen: str):

    validate_fen(fen)

    result = await graph.ainvoke({
        "fen": fen
    })

    return {
        "fen": fen,

        "lichess": result.get(
            "lichess",
            {
                "status": "empty",
                "message": "Aucune donnée",
                "data": {},
            }
        ),

        "stockfish": result.get(
            "stockfish",
            {
                "status": "empty",
                "message": "Non exécuté",
                "data": {},
            }
        ),

        "milvus": result.get(
            "milvus",
            {
                "status": "empty",
                "message": "Aucune donnée",
                "data": [],
            }
        ),

        "youtube": result.get(
            "youtube",
            {
                "status": "empty",
                "message": "Non exécuté",
                "data": [],
            }
        ),
    }


# ============================================================
# STOCKFISH
# ============================================================

@router.get("/evaluate/{fen:path}")
async def evaluate_position(fen: str):

    validate_fen(fen)

    result = await graph.ainvoke({
        "fen": fen
    })

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result["error"],
        )

    stockfish_data = result.get("stockfish_data")

    if not stockfish_data:
        return {
            "fen": fen,
            "message": "Position théorique trouvée dans Lichess",
            "lichess": result.get("lichess_data"),
        }

    return {
        "fen": fen,
        **stockfish_data,
    }


# ============================================================
# MILVUS
# ============================================================

@router.get("/vector-search")
async def vector_search(
    q: str,
    limit: int = 5,
):

    try:

        milvus_service = MilvusService()

        results = milvus_service.search(
            query=q,
            limit=limit,
        )

        return {
            "query": q,
            "results": results,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Erreur Milvus : {exc}",
        )


# ============================================================
# YOUTUBE
# ============================================================

@router.get("/videos/{opening}")
async def get_videos(opening: str):

    try:

        youtube_service = YouTubeService()

        videos = youtube_service.search_videos(
            opening=opening,
            limit=5,
        )

        return {
            "opening": opening,
            "videos": videos,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Erreur YouTube : {exc}",
        )