from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def create_embedding(text):
    """
    Convert text into embedding vector
    """

    embedding = model.encode(text)

    return embedding