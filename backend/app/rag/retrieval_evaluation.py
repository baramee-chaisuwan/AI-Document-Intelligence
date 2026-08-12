import json
from pathlib import Path
from typing import Callable

from app.rag.retrieval_metrics import (
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
    unique_ranked_references,
)


Retriever = Callable[[str, int], dict]
METRIC_NAMES = (
    "recall_at_1",
    "recall_at_3",
    "recall_at_5",
    "mrr",
    "ndcg_at_5",
)
DEFAULT_REGRESSION_TOLERANCES = {
    "recall_at_1": 0.05,
    "recall_at_3": 0.05,
    "recall_at_5": 0.05,
    "mrr": 0.05,
    "ndcg_at_5": 0.05,
}


class BenchmarkValidationError(ValueError):
    """Raised when a benchmark or baseline contract is malformed."""


def load_benchmark(path: str | Path) -> dict:

    payload = _load_json(path)
    version = payload.get("benchmark_version")
    cases = payload.get("cases")

    if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
        raise BenchmarkValidationError(
            "benchmark_version must be a positive integer"
        )

    if not isinstance(cases, list) or not cases:
        raise BenchmarkValidationError("cases must be a non-empty list")

    seen_ids = set()

    for index, case in enumerate(cases):
        _validate_case(case, index)

        if case["id"] in seen_ids:
            raise BenchmarkValidationError(
                f"duplicate benchmark case id: {case['id']}"
            )

        seen_ids.add(case["id"])

    return payload


def load_baseline(path: str | Path) -> dict:

    payload = _load_json(path)
    _validate_metric_payload(payload, require_case_count=True)
    return payload


def evaluate_benchmark(
    benchmark: dict,
    retriever: Retriever,
    *,
    max_results: int = 5,
) -> dict:

    if max_results < 5:
        raise ValueError("max_results must be at least 5")

    cases = benchmark["cases"]
    details = []

    for case in cases:
        retrieval = retriever(case["query"], max_results)
        ranked = extract_ranked_document_ids(retrieval)
        relevant = case["relevant_document_ids"]
        case_metrics = {
            "recall_at_1": recall_at_k(ranked, relevant, 1),
            "recall_at_3": recall_at_k(ranked, relevant, 3),
            "recall_at_5": recall_at_k(ranked, relevant, 5),
            "mrr": reciprocal_rank(ranked, relevant),
            "ndcg_at_5": ndcg_at_k(ranked, relevant, 5),
        }
        details.append({
            "id": case["id"],
            "category": case.get("category"),
            "relevant_document_ids": relevant,
            "retrieved_document_ids": ranked,
            "metrics": _round_metrics(case_metrics),
        })

    aggregate = {
        metric: sum(
            detail["metrics"][metric]
            for detail in details
        ) / len(details)
        for metric in METRIC_NAMES
    }

    return {
        "benchmark_version": benchmark["benchmark_version"],
        "case_count": len(details),
        **_round_metrics(aggregate),
        "cases": details,
    }


def extract_ranked_document_ids(results) -> list[str]:

    if not isinstance(results, dict):
        return []

    groups = results.get("metadatas")

    if not isinstance(groups, list) or not groups:
        return []

    metadatas = groups[0]

    if not isinstance(metadatas, list):
        return []

    return unique_ranked_references(
        metadata.get("document_id")
        for metadata in metadatas
        if isinstance(metadata, dict)
    )


def baseline_from_results(results: dict) -> dict:

    _validate_metric_payload(results, require_case_count=True)

    return {
        "benchmark_version": results["benchmark_version"],
        "case_count": results["case_count"],
        **{
            metric: results[metric]
            for metric in METRIC_NAMES
        },
    }


def compare_with_baseline(
    results: dict,
    baseline: dict,
    tolerances: dict[str, float] | None = None,
) -> dict:

    _validate_metric_payload(results, require_case_count=True)
    _validate_metric_payload(baseline, require_case_count=True)

    if results["benchmark_version"] != baseline["benchmark_version"]:
        raise BenchmarkValidationError(
            "benchmark and baseline versions do not match"
        )

    if results["case_count"] != baseline["case_count"]:
        raise BenchmarkValidationError(
            "benchmark and baseline case counts do not match"
        )

    policy = {
        **DEFAULT_REGRESSION_TOLERANCES,
        **(tolerances or {}),
    }
    regressions = []

    for metric in METRIC_NAMES:
        tolerance = policy.get(metric)

        if (
            isinstance(tolerance, bool)
            or not isinstance(tolerance, (int, float))
            or tolerance < 0
        ):
            raise BenchmarkValidationError(
                f"invalid regression tolerance for {metric}"
            )

        drop = baseline[metric] - results[metric]

        if drop > tolerance + 1e-12:
            regressions.append({
                "metric": metric,
                "baseline": baseline[metric],
                "actual": results[metric],
                "drop": round(drop, 6),
                "tolerance": tolerance,
            })

    return {
        "passed": not regressions,
        "regressions": regressions,
        "tolerances": policy,
    }


def _load_json(path: str | Path) -> dict:

    try:
        with Path(path).open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise BenchmarkValidationError(
            f"could not load evaluation JSON: {path}"
        ) from error

    if not isinstance(payload, dict):
        raise BenchmarkValidationError("evaluation JSON must be an object")

    return payload


def _validate_case(case, index: int) -> None:

    if not isinstance(case, dict):
        raise BenchmarkValidationError(
            f"case {index} must be an object"
        )

    case_id = case.get("id")
    query = case.get("query")
    relevant = case.get("relevant_document_ids")

    if not isinstance(case_id, str) or not case_id.strip():
        raise BenchmarkValidationError(
            f"case {index} id must be a non-empty string"
        )

    if not isinstance(query, str) or not query.strip():
        raise BenchmarkValidationError(
            f"case {case_id} query must be a non-empty string"
        )

    if not isinstance(relevant, list):
        raise BenchmarkValidationError(
            f"case {case_id} relevant_document_ids must be a list"
        )

    normalized = unique_ranked_references(relevant)

    if len(normalized) != len(relevant):
        raise BenchmarkValidationError(
            f"case {case_id} relevant_document_ids must be unique non-empty strings"
        )


def _validate_metric_payload(
    payload,
    *,
    require_case_count: bool,
) -> None:

    if not isinstance(payload, dict):
        raise BenchmarkValidationError("metric payload must be an object")

    version = payload.get("benchmark_version")

    if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
        raise BenchmarkValidationError(
            "metric payload benchmark_version is invalid"
        )

    if require_case_count:
        count = payload.get("case_count")

        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise BenchmarkValidationError(
                "metric payload case_count is invalid"
            )

    for metric in METRIC_NAMES:
        value = payload.get(metric)

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0.0 <= float(value) <= 1.0
        ):
            raise BenchmarkValidationError(
                f"metric payload {metric} is invalid"
            )


def _round_metrics(metrics: dict[str, float]) -> dict[str, float]:

    return {
        metric: round(float(metrics[metric]), 6)
        for metric in METRIC_NAMES
    }
