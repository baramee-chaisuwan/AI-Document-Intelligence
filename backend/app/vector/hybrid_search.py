RRF_K = 60
DEFAULT_VECTOR_WEIGHT = 1.0
DEFAULT_BM25_WEIGHT = 1.0
MAX_RESULTS = 50


def search_documents(*args, **kwargs):

    from app.vector.vector_service import (
        search_documents as vector_search
    )

    return vector_search(*args, **kwargs)


def search_bm25(*args, **kwargs):

    from app.vector.bm25_service import (
        search_bm25 as keyword_search
    )

    return keyword_search(*args, **kwargs)


def validate_query(
    query
):

    if not isinstance(
        query,
        str
    ):

        raise ValueError(
            "Search query must be a string"
        )


    query = query.strip()


    if not query:

        raise ValueError(
            "Search query must not be empty"
        )


    return query


def validate_n_results(
    n_results
):

    if (
        not isinstance(
            n_results,
            int
        )
        or isinstance(
            n_results,
            bool
        )
    ):

        raise ValueError(
            "n_results must be an integer"
        )


    if n_results <= 0:

        raise ValueError(
            "n_results must be greater than 0"
        )


    return min(
        n_results,
        MAX_RESULTS
    )


def get_vector_items(
    vector_results
):

    if not isinstance(
        vector_results,
        dict
    ):

        return []


    documents_group = vector_results.get(
        "documents",
        []
    )

    metadatas_group = vector_results.get(
        "metadatas",
        []
    )

    distances_group = vector_results.get(
        "distances",
        []
    )


    if (
        not documents_group
        or not metadatas_group
        or not distances_group
    ):

        return []


    documents = documents_group[0] or []
    metadatas = metadatas_group[0] or []
    distances = distances_group[0] or []


    items = []


    for rank, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances
        ),
        start=1
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


        document_id = str(
            metadata.get(
                "document_id",
                ""
            )
        ).strip()


        if not document_id:

            continue


        items.append({
            "document_id": document_id,
            "document": document,
            "metadata": metadata,
            "rank": rank,
            "distance": distance
        })


    return items


def get_bm25_items(
    bm25_results
):

    if not isinstance(
        bm25_results,
        dict
    ):

        return []


    documents = bm25_results.get(
        "documents",
        []
    )

    metadatas = bm25_results.get(
        "metadatas",
        []
    )

    scores = bm25_results.get(
        "scores",
        []
    )


    if (
        not isinstance(
            documents,
            list
        )
        or not isinstance(
            metadatas,
            list
        )
        or not isinstance(
            scores,
            list
        )
    ):

        return []


    items = []


    for rank, (
        document,
        metadata,
        score
    ) in enumerate(
        zip(
            documents,
            metadatas,
            scores
        ),
        start=1
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


        try:

            numeric_score = float(
                score
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        if numeric_score <= 0:

            continue


        document_id = str(
            metadata.get(
                "document_id",
                ""
            )
        ).strip()


        if not document_id:

            continue


        items.append({
            "document_id": document_id,
            "document": document,
            "metadata": metadata,
            "rank": rank,
            "bm25_score": numeric_score
        })


    return items


def add_result(
    fused_results,
    item,
    source,
    weight
):

    document_id = item[
        "document_id"
    ]


    rrf_score = (
        weight
        / (
            RRF_K
            + item["rank"]
        )
    )


    if document_id not in fused_results:

        fused_results[
            document_id
        ] = {
            "document": item[
                "document"
            ],
            "metadata": item[
                "metadata"
            ],
            "score": 0,
            "sources": [],
            "vector_rank": None,
            "bm25_rank": None,
            "vector_distance": None,
            "bm25_score": None
        }


    result = fused_results[
        document_id
    ]


    result["score"] += (
        rrf_score
    )


    if source not in result[
        "sources"
    ]:

        result["sources"].append(
            source
        )


    if source == "vector":

        result["vector_rank"] = item[
            "rank"
        ]

        result["vector_distance"] = (
            item.get(
                "distance"
            )
        )


    if source == "bm25":

        result["bm25_rank"] = item[
            "rank"
        ]

        result["bm25_score"] = (
            item.get(
                "bm25_score"
            )
        )


def hybrid_search(
    query: str,
    n_results: int = 10
):

    query = validate_query(
        query
    )


    n_results = validate_n_results(
        n_results
    )


    vector_results = search_documents(
        query=query,
        n_results=n_results
    )


    bm25_results = search_bm25(
        query=query,
        n_results=n_results
    )


    vector_items = get_vector_items(
        vector_results
    )


    bm25_items = get_bm25_items(
        bm25_results
    )


    fused_results = {}


    for item in vector_items:

        add_result(
            fused_results,
            item,
            source="vector",
            weight=DEFAULT_VECTOR_WEIGHT
        )


    for item in bm25_items:

        add_result(
            fused_results,
            item,
            source="bm25",
            weight=DEFAULT_BM25_WEIGHT
        )


    ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item[
            "score"
        ],
        reverse=True
    )


    top_results = ranked_results[
        :n_results
    ]


    return {
        "documents": [
            [
                item["document"]
                for item in top_results
            ]
        ],
        "metadatas": [
            [
                {
                    **item["metadata"],
                    "retrieval_sources": (
                        item["sources"]
                    ),
                    "vector_rank": (
                        item["vector_rank"]
                    ),
                    "bm25_rank": (
                        item["bm25_rank"]
                    )
                }
                for item in top_results
            ]
        ],
        "scores": [
            [
                item["score"]
                for item in top_results
            ]
        ]
    }
