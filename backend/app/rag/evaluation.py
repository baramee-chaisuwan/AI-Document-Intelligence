"""Compatibility exports for the deterministic retrieval evaluation API.

The former helpers in this module used mutable database candidate IDs and
could invoke Gemini. They were not tests of the current hybrid retrieval path.
Use ``python -m app.rag.evaluate_retrieval`` for the versioned offline
benchmark.
"""

from app.rag.retrieval_evaluation import (
    BenchmarkValidationError,
    compare_with_baseline,
    evaluate_benchmark,
    load_benchmark,
)


__all__ = [
    "BenchmarkValidationError",
    "compare_with_baseline",
    "evaluate_benchmark",
    "load_benchmark",
]
