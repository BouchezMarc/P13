import json

from app.services.milvus_service import MilvusService


def main():
    with open(
        "/app/data/openings.json",
        "r",
        encoding="utf-8",
    ) as file:
        documents = json.load(file)

    milvus = MilvusService()

    milvus.insert_documents(documents)

    print(
        f"{len(documents)} documents chargés dans Milvus."
    )


if __name__ == "__main__":
    main()