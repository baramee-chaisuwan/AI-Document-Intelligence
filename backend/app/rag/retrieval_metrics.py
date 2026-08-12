import math


def unique_ranked_references(retrieved) -> list[str]:

    unique = []
    seen = set()

    for value in retrieved or []:
        reference = str(value or "").strip()

        if not reference or reference in seen:
            continue

        seen.add(reference)
        unique.append(reference)

    return unique


def recall_at_k(
    retrieved,
    relevant,
    k: int,
) -> float:

    _validate_k(k)
    ranked = unique_ranked_references(retrieved)[:k]
    relevant_set = _relevant_set(relevant)

    if not relevant_set:
        return 1.0 if not ranked else 0.0

    return len(set(ranked) & relevant_set) / len(relevant_set)


def reciprocal_rank(
    retrieved,
    relevant,
) -> float:

    ranked = unique_ranked_references(retrieved)
    relevant_set = _relevant_set(relevant)

    if not relevant_set:
        return 1.0 if not ranked else 0.0

    for rank, reference in enumerate(ranked, start=1):
        if reference in relevant_set:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(
    retrieved,
    relevant,
    k: int,
) -> float:

    _validate_k(k)
    ranked = unique_ranked_references(retrieved)[:k]
    relevant_set = _relevant_set(relevant)

    if not relevant_set:
        return 1.0 if not ranked else 0.0

    discounted_gain = sum(
        1.0 / math.log2(rank + 1)
        for rank, reference in enumerate(ranked, start=1)
        if reference in relevant_set
    )
    ideal_count = min(len(relevant_set), k)
    ideal_gain = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )

    return discounted_gain / ideal_gain


def _relevant_set(relevant) -> set[str]:

    return set(unique_ranked_references(relevant))


def _validate_k(k: int) -> None:

    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")
