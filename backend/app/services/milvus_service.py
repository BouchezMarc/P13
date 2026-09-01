from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)

from sentence_transformers import SentenceTransformer


class MilvusService:

    COLLECTION_NAME = "chess_openings"
    EMBEDDING_DIM = 384

    def __init__(self):
        connections.connect(
            alias="default",
            host="milvus",
            port="19530",
        )

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):

        if utility.has_collection(self.COLLECTION_NAME):
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            return collection

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=False,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.EMBEDDING_DIM,
            ),
            FieldSchema(
                name="title",
                dtype=DataType.VARCHAR,
                max_length=255,
            ),
            FieldSchema(
                name="opening",
                dtype=DataType.VARCHAR,
                max_length=255,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=5000,
            ),
            FieldSchema(
                name="source",
                dtype=DataType.VARCHAR,
                max_length=255,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Chess opening knowledge",
        )

        collection = Collection(
            name=self.COLLECTION_NAME,
            schema=schema,
        )

        index_params = {
            "index_type": "AUTOINDEX",
            "metric_type": "COSINE",
            "params": {},
        }

        collection.create_index(
            field_name="embedding",
            index_params=index_params,
        )

        collection.load()

        return collection

    def insert_documents(self, documents: list[dict]):

        texts = [
            document["text"]
            for document in documents
        ]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        ).tolist()

        ids = list(
            range(1, len(documents) + 1)
        )

        titles = [
            document["title"]
            for document in documents
        ]

        openings = [
            document["opening"]
            for document in documents
        ]

        sources = [
            document["source"]
            for document in documents
        ]

        self.collection.insert([
            ids,
            embeddings,
            titles,
            openings,
            texts,
            sources,
        ])

        self.collection.flush()

    def search(
        self,
        query: str,
        limit: int = 5,
    ):

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.search(
            data=embedding,
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
                "params": {},
            },
            limit=limit,
            output_fields=[
                "title",
                "opening",
                "text",
                "source",
            ],
        )

        documents = []

        for hits in results:
            for hit in hits:
                documents.append({
                    "score": float(hit.score),
                    "title": hit.entity.get("title"),
                    "opening": hit.entity.get("opening"),
                    "text": hit.entity.get("text"),
                    "source": hit.entity.get("source"),
                })

        return documents