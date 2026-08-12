import json
import math

from sqlalchemy.orm import Session

from app.database.models import RAGEvaluation
from app.repositories import rag_evaluation_repository
from app.services.observability_service import emit_event


ALLOWED_OPERATIONS = {
    "assistant",
    "recommendation"
}


def persist_evaluation_safely(
    db: Session | None,
    *,
    user_query: str,
    generated_answer,
    retrieved_results,
    retrieval_latency_ms: float,
    generation_latency_ms: float,
    total_latency_ms: float,
    operation: str
) -> RAGEvaluation | None:

    if db is None:
        return None

    try:
        evaluation = build_evaluation(
            user_query=user_query,
            generated_answer=generated_answer,
            retrieved_results=retrieved_results,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            total_latency_ms=total_latency_ms,
            operation=operation
        )

        return (
            rag_evaluation_repository
            .create_rag_evaluation(
                db,
                evaluation
            )
        )
    except Exception as error:
        db.rollback()
        emit_event(
            "rag_evaluation_persistence_failed",
            severity="ERROR",
            operation="rag_evaluation_persistence",
            outcome="failure",
            error_category=type(error).__name__,
            rag_operation=(
                operation
                if operation in ALLOWED_OPERATIONS
                else "invalid"
            )
        )
        return None


def build_evaluation(
    *,
    user_query: str,
    generated_answer,
    retrieved_results,
    retrieval_latency_ms: float,
    generation_latency_ms: float,
    total_latency_ms: float,
    operation: str
) -> RAGEvaluation:

    normalized_query = str(
        user_query or ""
    ).strip()
    normalized_answer = _normalize_answer(
        generated_answer
    )
    normalized_operation = str(
        operation or ""
    ).strip().lower()

    if not normalized_query:
        raise ValueError("Evaluation query is required")

    if not normalized_answer:
        raise ValueError("Evaluation answer is required")

    if normalized_operation not in ALLOWED_OPERATIONS:
        raise ValueError("Evaluation operation is invalid")

    retrieved_documents = normalize_retrieved_documents(
        retrieved_results
    )

    return RAGEvaluation(
        user_query=normalized_query,
        generated_answer=normalized_answer,
        retrieved_documents=retrieved_documents,
        retrieval_latency_ms=_normalize_timing(
            retrieval_latency_ms
        ),
        generation_latency_ms=_normalize_timing(
            generation_latency_ms
        ),
        total_latency_ms=_normalize_timing(
            total_latency_ms
        ),
        retrieved_count=len(retrieved_documents),
        operation=normalized_operation
    )


def normalize_retrieved_documents(results) -> list[dict]:

    if not isinstance(results, dict):
        return []

    metadata_groups = results.get("metadatas")
    score_groups = results.get("scores")

    if not isinstance(metadata_groups, list) or not metadata_groups:
        return []

    metadatas = metadata_groups[0]
    scores = (
        score_groups[0]
        if isinstance(score_groups, list)
        and score_groups
        and isinstance(score_groups[0], list)
        else []
    )

    if not isinstance(metadatas, list):
        return []

    normalized = []

    for rank, metadata in enumerate(metadatas, start=1):
        if not isinstance(metadata, dict):
            continue

        item = {
            "rank": rank
        }
        candidate_id = _positive_integer(
            metadata.get("candidate_id")
        )
        document_id = str(
            metadata.get("document_id") or ""
        ).strip()
        chunk_index = _nonnegative_integer(
            metadata.get("chunk_index")
        )
        score = (
            _finite_number(scores[rank - 1])
            if rank <= len(scores)
            else None
        )
        distance = _finite_number(
            metadata.get(
                "distance",
                metadata.get("vector_distance")
            )
        )
        sources = metadata.get("retrieval_sources")

        if candidate_id is not None:
            item["candidate_id"] = candidate_id

        if document_id:
            item["document_id"] = document_id

        if chunk_index is not None:
            item["chunk_index"] = chunk_index

        if score is not None:
            item["score"] = score

        if distance is not None:
            item["distance"] = distance

        if isinstance(sources, list):
            safe_sources = [
                source
                for source in sources
                if source in {"vector", "bm25"}
            ]

            if safe_sources:
                item["retrieval_sources"] = safe_sources

        if len(item) > 1:
            normalized.append(item)

    return normalized


def _normalize_answer(answer) -> str:

    if hasattr(answer, "model_dump"):
        answer = answer.model_dump()

    if isinstance(answer, (dict, list)):
        return json.dumps(
            answer,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True
        )

    return str(answer or "").strip()


def _normalize_timing(value) -> float:

    normalized = _finite_number(value)

    if normalized is None:
        return 0.0

    return round(max(0.0, normalized), 2)


def _finite_number(value) -> float | None:

    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


def _positive_integer(value) -> int | None:

    number = _nonnegative_integer(value)

    return number if number and number > 0 else None


def _nonnegative_integer(value) -> int | None:

    if isinstance(value, bool):
        return None

    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None

    return number if number >= 0 else None
