import chess
from stockfish import Stockfish


class StockfishService:

    def __init__(self):
        self.stockfish = Stockfish(
            path="/usr/games/stockfish",
            depth=15,
        )

    def evaluate(self, fen: str) -> dict:
        board = chess.Board(fen)

        self.stockfish.set_fen_position(fen)

        evaluation = self.stockfish.get_evaluation()
        best_move = self.stockfish.get_best_move()

        return {
            "evaluation": evaluation,
            "best_move": best_move,
            "depth": 15,
        }