import os

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

CHUNK_SIZE = int(
    os.getenv(
        "RAG_CHUNK_SIZE",
        "1000"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "RAG_CHUNK_OVERLAP",
        "150"
    )
)

if CHUNK_SIZE <= 0:

    raise ValueError(
        "RAG_CHUNK_SIZE must be greater than 0"
    )

if (
    CHUNK_OVERLAP < 0
    or CHUNK_OVERLAP >= CHUNK_SIZE
):

    raise ValueError(
        "RAG_CHUNK_OVERLAP must be greater than "
        "or equal to 0 and smaller than RAG_CHUNK_SIZE"
    )

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "。 ",
        "• ",
        "- ",
        " ",
        ""
    ]
)

def normalize_resume_text(
    text
):

    if not isinstance(
        text,
        str
    ):

        raise ValueError(
            "Resume text must be a string"
        )


    normalized_text = (
        text
        .replace(
            "\r\n",
            "\n"
        )
        .replace(
            "\r",
            "\n"
        )
        .strip()
    )


    return normalized_text

def split_resume(
    text: str
):

    normalized_text = (
        normalize_resume_text(
            text
        )
    )

    if not normalized_text:

        return []

    chunks = (
        text_splitter.split_text(
            normalized_text
        )
    )

    return [
        chunk.strip()
        for chunk in chunks
        if chunk
        and chunk.strip()
    ]