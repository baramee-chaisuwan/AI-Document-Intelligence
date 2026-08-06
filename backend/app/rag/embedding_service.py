import logging
import math
import os
import threading


os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


logger = logging.getLogger(__name__)


EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "paraphrase-MiniLM-L3-v2"
)

EMBEDDING_BATCH_SIZE = int(
    os.getenv(
        "EMBEDDING_BATCH_SIZE",
        "16"
    )
)

EMBEDDING_DIMENSION = 384


embedding_model = None
model_lock = threading.Lock()


def get_model():

    global embedding_model

    if embedding_model is None:

        with model_lock:

            if embedding_model is None:

                try:

                    from sentence_transformers import (
                        SentenceTransformer
                    )

                    logger.info(
                        "Loading embedding model: %s",
                        EMBEDDING_MODEL_NAME
                    )

                    candidate_model = SentenceTransformer(
                        EMBEDDING_MODEL_NAME,
                        device="cpu"
                    )

                    model_dimension = (
                        candidate_model
                        .get_embedding_dimension()
                    )

                    if model_dimension != EMBEDDING_DIMENSION:

                        raise RuntimeError(
                            "Embedding model dimension does not "
                            f"match the required {EMBEDDING_DIMENSION}"
                        )

                    embedding_model = candidate_model

                except Exception as error:

                    logger.exception(
                        "Embedding model could not be loaded"
                    )

                    raise RuntimeError(
                        "Embedding model is unavailable"
                    ) from error

    return embedding_model


def normalize_embedding(
    embedding
):

    try:

        values = embedding.tolist()

    except AttributeError:

        values = embedding

    if not isinstance(values, list):

        raise ValueError(
            "Embedding must be a list"
        )

    if len(values) != EMBEDDING_DIMENSION:

        raise ValueError(
            "Embedding dimension must be "
            f"{EMBEDDING_DIMENSION}"
        )

    normalized_values = []

    for value in values:

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):

            raise ValueError(
                "Embedding values must be finite numbers"
            )

        normalized_values.append(
            float(value)
        )

    return normalized_values


def validate_text(
    text
):

    if not isinstance(
        text,
        str
    ):

        raise ValueError(
            "Embedding text must be a string"
        )

    normalized_text = text.strip()

    if not normalized_text:

        raise ValueError(
            "Embedding text must not be empty"
        )

    return normalized_text


def create_embedding(
    text
):

    """
    Convert one text value into an embedding vector.
    """

    normalized_text = validate_text(
        text
    )

    current_model = get_model()

    try:

        embedding = current_model.encode(
            normalized_text,
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    except Exception as error:

        logger.exception(
            "Embedding creation failed"
        )

        raise RuntimeError(
            "Embedding could not be created"
        ) from error

    return embedding


def create_embeddings(
    texts
):

    """
    Convert multiple text values into embedding vectors
    in one model call.
    """

    if not isinstance(
        texts,
        list
    ):

        raise ValueError(
            "Embedding texts must be a list"
        )

    normalized_texts = []

    for text in texts:

        normalized_texts.append(
            validate_text(
                text
            )
        )

    if not normalized_texts:

        raise ValueError(
            "At least one embedding text is required"
        )

    current_model = get_model()

    try:

        embeddings = current_model.encode(
            normalized_texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    except Exception as error:

        logger.exception(
            "Batch embedding creation failed"
        )

        raise RuntimeError(
            "Embeddings could not be created"
        ) from error

    return embeddings
