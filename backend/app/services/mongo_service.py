from pymongo import MongoClient
from datetime import datetime, timezone
import os


class MongoService:

    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGO_URI", "mongodb://mongo:27017")
        )

        self.db = self.client["chess_agent"]
        self.games = self.db["games"]

    def create_game(self, initial_fen: str):
        game = {
            "started_at": datetime.now(timezone.utc),
            "ended_at": None,
            "initial_fen": initial_fen,
            "moves": []
        }

        result = self.games.insert_one(game)

        return str(result.inserted_id)

    def add_move(self, game_id: str, move_data: dict):
        from bson import ObjectId

        self.games.update_one(
            {"_id": ObjectId(game_id)},
            {
                "$push": {
                    "moves": move_data
                }
            }
        )

    def end_game(self, game_id: str):
        from bson import ObjectId

        self.games.update_one(
            {"_id": ObjectId(game_id)},
            {
                "$set": {
                    "ended_at": datetime.now(timezone.utc)
                }
            }
        )