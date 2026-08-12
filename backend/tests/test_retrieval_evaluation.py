import json
import math
from pathlib import Path

import pytest

from app.rag.evaluate_retrieval import (
    DEFAULT_BASELINE,
    DEFAULT_BENCHMARK,
    DEFAULT_FIXTURE,
    DeterministicFixtureRetriever,
)
from app.rag.retrieval_evaluation import (
    BenchmarkValidationError,
    baseline_from_results,
    compare_with_baseline,
    evaluate_benchmark,
    load_baseline,
    load_benchmark,
)
from app.rag.retrieval_metrics import (
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k_uses_unique_ranked_references():

    retrieved = ["doc-a", "doc-a", "doc-b", "doc-c"]
    relevant = ["doc-a", "doc-c"]

    assert recall_at_k(retrieved, relevant, 1) == 0.5
    assert recall_at_k(retrieved, relevant, 3) == 1.0


def test_reciprocal_rank_returns_first_relevant_position():

    assert reciprocal_rank(
        ["irrelevant", "relevant", "later"],
        ["relevant", "later"],
    ) == 0.5
    assert reciprocal_rank(["irrelevant"], ["relevant"]) == 0.0


def test_ndcg_at_k_uses_binary_relevance_and_ideal_order():

    score = ndcg_at_k(
        ["irrelevant", "relevant-a", "relevant-b"],
        ["relevant-a", "relevant-b"],
        5,
    )
    expected = 1 / math.log2(3) + 1 / math.log2(4)
    ideal = 1 + 1 / math.log2(3)

    assert score == pytest.approx(expected / ideal)


@pytest.mark.parametrize(
    ("retrieved", "expected"),
    [
        ([], 1.0),
        (["unexpected"], 0.0),
    ],
)
def test_no_relevant_results_require_empty_retrieval(
    retrieved,
    expected,
):

    assert recall_at_k(retrieved, [], 5) == expected
    assert reciprocal_rank(retrieved, []) == expected
    assert ndcg_at_k(retrieved, [], 5) == expected


def test_empty_retrieval_scores_zero_when_relevant_exists():

    assert recall_at_k([], ["expected"], 5) == 0.0
    assert reciprocal_rank([], ["expected"]) == 0.0
    assert ndcg_at_k([], ["expected"], 5) == 0.0


def test_load_benchmark_rejects_malformed_case(tmp_path: Path):

    malformed = tmp_path / "malformed.json"
    malformed.write_text(
        json.dumps({
            "benchmark_version": 1,
            "cases": [{
                "id": "missing-query",
                "relevant_document_ids": [],
            }],
        }),
        encoding="utf-8",
    )

    with pytest.raises(
        BenchmarkValidationError,
        match="query must be a non-empty string",
    ):
        load_benchmark(malformed)


def test_versioned_benchmark_loads_synthetic_cases():

    benchmark = load_benchmark(DEFAULT_BENCHMARK)

    assert benchmark["benchmark_version"] == 1
    assert len(benchmark["cases"]) == 6
    assert {case["category"] for case in benchmark["cases"]} == {
        "semantic_matching",
        "exact_technical_keywords",
        "abbreviation",
        "multi_skill",
        "no_result",
        "lexical_vs_semantic",
    }


def test_deterministic_hybrid_evaluation_matches_committed_baseline():

    benchmark = load_benchmark(DEFAULT_BENCHMARK)
    retriever = DeterministicFixtureRetriever(
        benchmark,
        DEFAULT_FIXTURE,
    )
    first = evaluate_benchmark(benchmark, retriever)
    second = evaluate_benchmark(benchmark, retriever)
    baseline = load_baseline(DEFAULT_BASELINE)

    assert first == second
    assert baseline_from_results(first) == baseline
    assert compare_with_baseline(first, baseline)["passed"] is True


def test_baseline_comparison_allows_documented_tolerance():

    baseline = load_baseline(DEFAULT_BASELINE)
    result = {
        **baseline,
        "recall_at_1": baseline["recall_at_1"] - 0.05,
        "mrr": baseline["mrr"] - 0.049,
    }

    comparison = compare_with_baseline(result, baseline)

    assert comparison["passed"] is True
    assert comparison["regressions"] == []


def test_baseline_comparison_detects_meaningful_regression():

    baseline = load_baseline(DEFAULT_BASELINE)
    result = {
        **baseline,
        "recall_at_3": baseline["recall_at_3"] - 0.06,
        "ndcg_at_5": baseline["ndcg_at_5"] - 0.07,
    }

    comparison = compare_with_baseline(result, baseline)

    assert comparison["passed"] is False
    assert {
        regression["metric"]
        for regression in comparison["regressions"]
    } == {"recall_at_3", "ndcg_at_5"}
