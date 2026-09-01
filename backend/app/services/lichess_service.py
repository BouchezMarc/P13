import os
import httpx


class LichessService:

    BASE_URL = "https://explorer.lichess.ovh/masters"

    async def get_opening_moves(self, fen: str) -> dict:

        token = os.getenv("LICHESS_API_KEY")

        if not token:
            raise RuntimeError(
                "LICHESS_API_KEY n'est pas configurée."
            )

        params = {
            "fen": fen,
            "moves": 20,
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                self.BASE_URL,
                params=params,
                headers=headers
            )

            response.raise_for_status()

            return response.json()
