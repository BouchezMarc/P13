import os

from googleapiclient.discovery import build


class YouTubeService:

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")

        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY non définie")

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=self.api_key,
        )

    def search_videos(
        self,
        title: str,
        opening: str,
        limit: int = 5,
        duration: str | None = None,
    ):

        # --------------------------------------------------
        # REQUÊTE
        # --------------------------------------------------

        query = f"{title} {opening} chess"

        # --------------------------------------------------
        # RECHERCHE YOUTUBE
        # --------------------------------------------------

        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=limit,
            relevanceLanguage="en",
        )

        # --------------------------------------------------
        # FILTRE DE DURÉE OPTIONNEL
        # short  = < 4 min
        # medium = 4 à 20 min
        # long   = > 20 min
        # --------------------------------------------------

        if duration in ("short", "medium", "long"):
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                videoDuration=duration,
                maxResults=limit,
                relevanceLanguage="en",
            )

        response = request.execute()

        videos = []

        for item in response.get("items", []):

            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "description": snippet["description"],
                "channel": snippet["channelTitle"],
                "published_at": snippet["publishedAt"],
                "thumbnail": (
                    snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                ),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

        return videos