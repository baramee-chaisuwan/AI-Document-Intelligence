import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.rag.retrieval_evaluation import (
    BenchmarkValidationError,
    compare_with_baseline,
    evaluate_benchmark,
    load_baseline,
    load_benchmark,
)
from app.vector.bm25_service import search_bm25_chunks
from app.vector.hybrid_search import hybrid_search


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK = (
    BACKEND_ROOT / "evaluation" / "rag_retrieval_benchmark.json"
)
DEFAULT_FIXTURE = (
    BACKEND_ROOT / "evaluation" / "rag_retrieval_fixture.json"
)
DEFAULT_BASELINE = (
    BACKEND_ROOT / "evaluation" / "rag_retrieval_baseline.json"
)


class FixtureValidationError(BenchmarkValidationError):
    """Raised when the deterministic retrieval fixture is malformed."""


class DeterministicFixtureRetriever:

    def __init__(self, benchmark: dict, fixture_path: str | Path):
        self.benchmark = benchmark
        self.fixture = _load_fixture(fixture_path, benchmark)
        self.case_by_query = {
            case["query"]: case
            for case in benchmark["cases"]
        }
        self.documents = {
            document["document_id"]: document
            for document in self.fixture["documents"]
        }
        self.bm25_chunks = [
            SimpleNamespace(
                document_id=document["document_id"],
                candidate_id=document["candidate_ref"],
                chunk_text=document["text"],
            )
            for document in self.fixture["documents"]
        ]

    def __call__(self, query: str, n_results: int) -> dict:
        case = self.case_by_query.get(query)

        if case is None:
            raise FixtureValidationError(
                "query is not present in the deterministic benchmark"
            )

        ranking = self.fixture["vector_rankings"][case["id"]]
        vector_results = _vector_results(
            ranking,
            self.documents,
            n_results,
        )
        bm25_results = search_bm25_chunks(
            query,
            self.bm25_chunks,
            n_results,
        )

        with patch(
            "app.vector.hybrid_search.search_documents",
            return_value=vector_results,
        ), patch(
            "app.vector.hybrid_search.search_bm25",
            return_value=bm25_results,
        ):
            return hybrid_search(query, n_results=n_results)


def main(argv=None) -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Run the versioned deterministic hybrid retrieval benchmark."
        )
    )
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete result as JSON.",
    )
    parser.add_argument(
        "--no-regression-check",
        action="store_true",
        help="Calculate metrics without comparing the committed baseline.",
    )
    args = parser.parse_args(argv)

    try:
        benchmark = load_benchmark(args.benchmark)
        retriever = DeterministicFixtureRetriever(
            benchmark,
            args.fixture,
        )
        results = evaluate_benchmark(benchmark, retriever)
        comparison = None

        if not args.no_regression_check:
            comparison = compare_with_baseline(
                results,
                load_baseline(args.baseline),
            )
    except BenchmarkValidationError as error:
        print(f"Evaluation configuration error: {error}", file=sys.stderr)
        return 2

    if args.json:
        output = {"results": results}

        if comparison is not None:
            output["regression_check"] = comparison

        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        _print_report(results, comparison)

    return 1 if comparison and not comparison["passed"] else 0


def _load_fixture(path: str | Path, benchmark: dict) -> dict:

    try:
        with Path(path).open("r", encoding="utf-8") as file:
            fixture = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise FixtureValidationError(
            f"could not load deterministic fixture: {path}"
        ) from error

    if not isinstance(fixture, dict):
        raise FixtureValidationError("fixture must be an object")

    if fixture.get("benchmark_version") != benchmark["benchmark_version"]:
        raise FixtureValidationError(
            "fixture and benchmark versions do not match"
        )

    documents = fixture.get("documents")
    rankings = fixture.get("vector_rankings")

    if not isinstance(documents, list) or not documents:
        raise FixtureValidationError("fixture documents must be non-empty")

    if not isinstance(rankings, dict):
        raise FixtureValidationError("fixture vector_rankings must be an object")

    document_ids = set()

    for document in documents:
        if not isinstance(document, dict):
            raise FixtureValidationError("fixture document must be an object")

        values = (
            document.get("document_id"),
            document.get("candidate_ref"),
            document.get("text"),
        )

        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise FixtureValidationError(
                "fixture document fields must be non-empty strings"
            )

        if document["document_id"] in document_ids:
            raise FixtureValidationError("fixture document IDs must be unique")

        document_ids.add(document["document_id"])

    case_ids = {case["id"] for case in benchmark["cases"]}

    if set(rankings) != case_ids:
        raise FixtureValidationError(
            "fixture rankings must exactly cover benchmark cases"
        )

    for case_id, ranking in rankings.items():
        if not isinstance(ranking, list):
            raise FixtureValidationError(
                f"fixture ranking for {case_id} must be a list"
            )

        if (
            len(unique := list(dict.fromkeys(ranking))) != len(ranking)
            or any(reference not in document_ids for reference in unique)
        ):
            raise FixtureValidationError(
                f"fixture ranking for {case_id} is invalid"
            )

    return fixture


def _vector_results(ranking, documents, n_results: int) -> dict:

    selected = ranking[:n_results]

    return {
        "documents": [[documents[reference]["text"] for reference in selected]],
        "metadatas": [[
            {
                "document_id": reference,
                "candidate_id": documents[reference]["candidate_ref"],
            }
            for reference in selected
        ]],
        "distances": [[
            round(0.05 + rank * 0.05, 6)
            for rank in range(len(selected))
        ]],
    }


def _print_report(results: dict, comparison: dict | None) -> None:

    print(
        "RAG retrieval benchmark "
        f"v{results['benchmark_version']} ({results['case_count']} cases)"
    )
    print(f"Recall@1: {results['recall_at_1']:.4f}")
    print(f"Recall@3: {results['recall_at_3']:.4f}")
    print(f"Recall@5: {results['recall_at_5']:.4f}")
    print(f"MRR:      {results['mrr']:.4f}")
    print(f"nDCG@5:   {results['ndcg_at_5']:.4f}")

    if comparison is not None:
        status = "PASS" if comparison["passed"] else "FAIL"
        print(f"Regression check: {status}")

        for regression in comparison["regressions"]:
            print(
                f"  {regression['metric']}: "
                f"{regression['actual']:.4f} vs "
                f"{regression['baseline']:.4f} baseline"
            )


if __name__ == "__main__":
    raise SystemExit(main())
