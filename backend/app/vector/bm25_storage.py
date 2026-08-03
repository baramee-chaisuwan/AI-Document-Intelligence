import json
import os
from pathlib import Path


BASE_DIR = Path(
    __file__
).resolve().parents[2]


BM25_FILE = (
    BASE_DIR
    / "data"
    / "bm25_data.json"
)


BM25_TEMP_FILE = (
    BASE_DIR
    / "data"
    / "bm25_data.tmp"
)


def validate_bm25_data(
    documents,
    metadatas
):

    if not isinstance(
        documents,
        list
    ):

        raise ValueError(
            "BM25 documents must be a list"
        )


    if not isinstance(
        metadatas,
        list
    ):

        raise ValueError(
            "BM25 metadatas must be a list"
        )


    if len(documents) != len(
        metadatas
    ):

        raise ValueError(
            "BM25 documents and metadatas "
            "must have the same length"
        )


    for document in documents:

        if not isinstance(
            document,
            str
        ):

            raise ValueError(
                "Every BM25 document "
                "must be a string"
            )


    for metadata in metadatas:

        if not isinstance(
            metadata,
            dict
        ):

            raise ValueError(
                "Every BM25 metadata "
                "must be an object"
            )


def save_bm25_data(
    documents,
    metadatas
):

    validate_bm25_data(
        documents,
        metadatas
    )


    BM25_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    data = {
        "documents": documents,
        "metadatas": metadatas
    }


    try:

        with open(
            BM25_TEMP_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )


            file.flush()

            os.fsync(
                file.fileno()
            )


        os.replace(
            BM25_TEMP_FILE,
            BM25_FILE
        )


    except Exception:

        if BM25_TEMP_FILE.exists():

            try:

                BM25_TEMP_FILE.unlink()

            except Exception:

                pass


        raise


def load_bm25_data():

    if not BM25_FILE.exists():

        return [], []


    try:

        with open(
            BM25_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )


    except (
        json.JSONDecodeError,
        OSError
    ):

        return [], []


    if not isinstance(
        data,
        dict
    ):

        return [], []


    documents = data.get(
        "documents",
        []
    )


    metadatas = data.get(
        "metadatas",
        []
    )


    if not isinstance(
        documents,
        list
    ):

        return [], []


    if not isinstance(
        metadatas,
        list
    ):

        return [], []


    if len(documents) != len(
        metadatas
    ):

        valid_length = min(
            len(documents),
            len(metadatas)
        )


        documents = documents[
            :valid_length
        ]


        metadatas = metadatas[
            :valid_length
        ]


    return (
        documents,
        metadatas
    )