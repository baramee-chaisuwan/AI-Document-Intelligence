import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

BM25_FILE = BASE_DIR / "data" / "bm25_data.json"


def save_bm25_data(
    documents,
    metadatas
):

    BM25_FILE.parent.mkdir(
        exist_ok=True
    )

    with open(
        BM25_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "documents": documents,
                "metadatas": metadatas
            },
            f,
            ensure_ascii=False,
            indent=2
        )

def load_bm25_data():

    if not BM25_FILE.exists():

        return [], []

    with open(
        BM25_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return (
        data["documents"],
        data["metadatas"]
    )