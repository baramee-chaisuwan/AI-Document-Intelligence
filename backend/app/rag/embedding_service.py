import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

model = None


def get_model():

    global model

    if model is None:

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            "paraphrase-MiniLM-L3-v2",
            device="cpu"
        )

    return model


def create_embedding(text):

    """
    Convert text into embedding vector
    """

    model = get_model()

    embedding = model.encode(
        text,
        batch_size=1,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return embedding