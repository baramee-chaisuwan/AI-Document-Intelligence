from langchain_core.output_parsers import StrOutputParser

from app.rag.chain import (
    get_assistant_chain,
    get_recommendation_chain
)

from app.vector.hybrid_search import hybrid_search
from app.vector.vector_service import get_candidate_documents


assistant_rag_chain = None


MAX_ASSISTANT_CANDIDATES = 4
MAX_RECOMMENDATION_CANDIDATES = 8
MAX_CHUNKS_PER_CANDIDATE = 4
MAX_CONTEXT_CHARACTERS = 30000


NO_INFORMATION_MESSAGE = (
    "I couldn't find that information "
    "in the resume database."
)


def get_assistant_rag_chain():

    global assistant_rag_chain

    if assistant_rag_chain is None:

        assistant_rag_chain = (
            get_assistant_chain()
            | StrOutputParser()
        )

    return assistant_rag_chain


def get_result_groups(
    results
):

    if not isinstance(
        results,
        dict
    ):

        return [], []


    document_groups = results.get(
        "documents",
        []
    )

    metadata_groups = results.get(
        "metadatas",
        []
    )


    if (
        not document_groups
        or not metadata_groups
    ):

        return [], []


    documents = document_groups[0]
    metadatas = metadata_groups[0]


    if not isinstance(
        documents,
        list
    ):

        documents = []


    if not isinstance(
        metadatas,
        list
    ):

        metadatas = []


    return (
        documents,
        metadatas
    )


def get_candidate_ids(
    results,
    max_candidates
):

    documents, metadatas = (
        get_result_groups(
            results
        )
    )


    candidate_ids = []


    for metadata in metadatas:

        if not isinstance(
            metadata,
            dict
        ):
            continue


        candidate_id = str(
            metadata.get(
                "candidate_id",
                ""
            )
        ).strip()


        if not candidate_id:
            continue


        if candidate_id in candidate_ids:
            continue


        candidate_ids.append(
            candidate_id
        )


        if len(
            candidate_ids
        ) >= max_candidates:
            break


    return candidate_ids


def get_candidate_chunks(
    candidate_id,
    max_chunks=MAX_CHUNKS_PER_CANDIDATE
):

    result = get_candidate_documents(
        candidate_id
    )


    if not isinstance(
        result,
        dict
    ):

        return []


    documents = result.get(
        "documents",
        []
    )


    if not isinstance(
        documents,
        list
    ):

        return []


    clean_documents = []


    for document in documents:

        if not isinstance(
            document,
            str
        ):
            continue


        document = document.strip()


        if not document:
            continue


        if document in clean_documents:
            continue


        clean_documents.append(
            document
        )


        if len(
            clean_documents
        ) >= max_chunks:
            break


    return clean_documents


def build_candidate_context(
    results,
    max_candidates=MAX_ASSISTANT_CANDIDATES,
    max_chunks_per_candidate=MAX_CHUNKS_PER_CANDIDATE
):

    documents, metadatas = (
        get_result_groups(
            results
        )
    )


    candidates = {}


    for document, metadata in zip(
        documents,
        metadatas
    ):

        if not isinstance(
            document,
            str
        ):

            continue


        if not isinstance(
            metadata,
            dict
        ):

            continue


        candidate_id = str(
            metadata.get(
                "candidate_id",
                ""
            )
        ).strip()


        document = document.strip()


        if (
            not candidate_id
            or not document
        ):

            continue


        if candidate_id not in candidates:

            if len(
                candidates
            ) >= max_candidates:
                continue


            candidates[
                candidate_id
            ] = []


        if document in candidates[
            candidate_id
        ]:
            continue


        if len(
            candidates[
                candidate_id
            ]
        ) >= max_chunks_per_candidate:
            continue


        candidates[
            candidate_id
        ].append(
            document
        )


    context_parts = []


    for candidate_id, chunks in candidates.items():

        if not chunks:
            continue


        context_parts.append(
            "\n".join([
                f"Candidate ID: {candidate_id}",
                "",
                "Resume evidence:",
                "\n".join(chunks),
                "",
                "--------------------"
            ])
        )


    context = "\n".join(
        context_parts
    )


    return context[
        :MAX_CONTEXT_CHARACTERS
    ]


def build_full_candidate_context(
    candidate_id,
    max_chunks=MAX_CHUNKS_PER_CANDIDATE
):

    candidate_id = str(
        candidate_id or ""
    ).strip()


    if not candidate_id:

        return ""


    documents = get_candidate_chunks(
        candidate_id,
        max_chunks=max_chunks
    )


    if not documents:

        return ""


    return "\n".join([
        f"Candidate ID: {candidate_id}",
        "",
        "Resume evidence:",
        "\n".join(documents),
        "",
        "--------------------"
    ])


def build_multiple_candidate_context(
    candidate_ids,
    max_chunks_per_candidate=MAX_CHUNKS_PER_CANDIDATE
):

    context_parts = []


    for candidate_id in candidate_ids:

        candidate_context = (
            build_full_candidate_context(
                candidate_id,
                max_chunks=(
                    max_chunks_per_candidate
                )
            )
        )


        if candidate_context:

            context_parts.append(
                candidate_context
            )


    context = "\n".join(
        context_parts
    )


    return context[
        :MAX_CONTEXT_CHARACTERS
    ]


def ask_rag(
    question: str
):

    question = str(
        question or ""
    ).strip()


    if not question:

        raise ValueError(
            "Question must not be empty"
        )


    results = hybrid_search(
        query=question,
        n_results=12
    )


    context = build_candidate_context(
        results,
        max_candidates=MAX_ASSISTANT_CANDIDATES,
        max_chunks_per_candidate=(
            MAX_CHUNKS_PER_CANDIDATE
        )
    )


    if not context.strip():

        return NO_INFORMATION_MESSAGE


    answer = (
        get_assistant_rag_chain()
        .invoke(
            {
                "resume": context,
                "question": question
            }
        )
    )


    answer = str(
        answer or ""
    ).strip()


    if not answer:

        return NO_INFORMATION_MESSAGE


    return answer


def create_empty_recommendation():

    return {
        "candidate_id": "N/A",
        "candidate_name": "No Candidate Found",
        "match_score": 0,
        "strengths": [],
        "relevant_experience": [],
        "reason": (
            "No candidate information was found "
            "in the resume database."
        )
    }


def normalize_recommendation_answer(
    answer,
    allowed_candidate_ids
):

    if hasattr(
        answer,
        "model_dump"
    ):

        answer = answer.model_dump()


    if not isinstance(
        answer,
        dict
    ):

        return create_empty_recommendation()


    candidate_id = str(
        answer.get(
            "candidate_id",
            ""
        )
    ).strip()


    if candidate_id not in allowed_candidate_ids:

        return create_empty_recommendation()


    candidate_name = str(
        answer.get(
            "candidate_name",
            ""
        )
    ).strip()


    try:

        match_score = int(
            round(
                float(
                    answer.get(
                        "match_score",
                        0
                    )
                )
            )
        )

    except (
        TypeError,
        ValueError
    ):

        match_score = 0


    match_score = max(
        0,
        min(
            match_score,
            100
        )
    )


    strengths = answer.get(
        "strengths",
        []
    )


    relevant_experience = answer.get(
        "relevant_experience",
        []
    )


    if not isinstance(
        strengths,
        list
    ):

        strengths = []


    if not isinstance(
        relevant_experience,
        list
    ):

        relevant_experience = []


    strengths = [
        str(item).strip()
        for item in strengths
        if str(item).strip()
    ]


    relevant_experience = [
        str(item).strip()
        for item in relevant_experience
        if str(item).strip()
    ]


    reason = str(
        answer.get(
            "reason",
            ""
        )
    ).strip()


    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "match_score": match_score,
        "strengths": strengths,
        "relevant_experience": (
            relevant_experience
        ),
        "reason": reason
    }


def ask_recommendation(
    question: str
):

    question = str(
        question or ""
    ).strip()


    if not question:

        raise ValueError(
            "Job requirement must not be empty"
        )


    results = hybrid_search(
        query=question,
        n_results=20
    )


    candidate_ids = get_candidate_ids(
        results,
        max_candidates=(
            MAX_RECOMMENDATION_CANDIDATES
        )
    )


    if not candidate_ids:

        return create_empty_recommendation()


    context = build_multiple_candidate_context(
        candidate_ids,
        max_chunks_per_candidate=(
            MAX_CHUNKS_PER_CANDIDATE
        )
    )


    if not context.strip():

        return create_empty_recommendation()


    answer = (
        get_recommendation_chain()
        .invoke(
            {
                "resume": context,
                "question": question
            }
        )
    )


    return normalize_recommendation_answer(
        answer,
        allowed_candidate_ids=(
            candidate_ids
        )
    )