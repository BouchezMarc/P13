class ChessContextService:

    def build(
        self,
        fen: str,
        lichess: dict | None = None,
        stockfish: dict | None = None,
    ) -> dict:

        lichess = lichess or {}
        stockfish = stockfish or {}

        # ============================================================
        # CONTEXTE DE BASE
        # ============================================================

        context = {
            "fen": fen,
            "source": None,

            # Informations théoriques
            "opening": None,
            "moves": [],
            "eco": None,
            # Informations Stockfish
            "best_move": None,
            "evaluation": None,
            "depth": None,

            # Texte final destiné à Milvus
            "query": "",
        }

        # ============================================================
        # 1. LICHESS
        # ============================================================

        if lichess.get("status") == "response":
            data = lichess.get("data", {})
            context["source"] = "lichess"

            opening = data.get("opening")

            if isinstance(opening, dict):
                context["opening"] = opening.get("name")
                context["eco"] = opening.get("eco")
            else:
                context["opening"] = opening or data.get("opening_name")
                context["eco"] = data.get("eco")

            context["moves"] = data.get("moves", [])

            query_parts = []

            if context["opening"]:
                query_parts.append(context["opening"])

            if context.get("eco"):
                query_parts.append(f"ECO {context['eco']}")

            context["query"] = " ".join(query_parts)

            return context

            # --------------------------------------------------------
            # CONSTRUCTION DE LA REQUÊTE MILVUS
            # --------------------------------------------------------

            query_parts = []

            if context["opening"]:
                query_parts.append(
                    f"chess opening {context['opening']}"
                )

            if context["moves"]:
                query_parts.append(
                    " ".join(
                        # str(move)
                        move.get("san", "")
                        for move in context["moves"][:5]
                    )
                )

            if not query_parts:
                query_parts.append(
                    "chess opening"
                )

            context["query"] = " ".join(query_parts)

            return context

        # ============================================================
        # 2. STOCKFISH
        # ============================================================

        if stockfish.get("status") == "response":

            data = stockfish.get("data", {})

            context["source"] = "stockfish"

            # Meilleur coup
            context["best_move"] = data.get(
                "best_move"
            )

            # Évaluation
            evaluation = data.get(
                "evaluation"
            )

            if isinstance(evaluation, dict):

                context["evaluation"] = evaluation.get(
                    "value"
                )

            else:

                context["evaluation"] = evaluation

            # Profondeur
            context["depth"] = data.get(
                "depth"
            )

            # --------------------------------------------------------
            # CONSTRUCTION DE LA REQUÊTE MILVUS
            # --------------------------------------------------------

            query_parts = [
                "chess position"
            ]

            if context["best_move"]:
                query_parts.append(
                    f"best move {context['best_move']}"
                )

            if context["evaluation"] is not None:
                query_parts.append(
                    f"evaluation {context['evaluation']}"
                )

            if context["depth"] is not None:
                query_parts.append(
                    f"depth {context['depth']}"
                )

            context["query"] = " ".join(
                query_parts
            )

            return context

        # ============================================================
        # 3. AUCUNE RÉPONSE
        # ============================================================

        context["source"] = None

        context["query"] = ""

        return context