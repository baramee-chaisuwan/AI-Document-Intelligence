from app.vector.vector_service import search_documents
from app.rag.rag_chain import (
    ask_rag,
    ask_recommendation
)


def evaluate_retrieval(tests):

    top1_correct = 0
    top3_correct = 0
    total = len(tests)

    details = []

    for question, expected_candidate in tests:

        results = search_documents(
            query=question,
            n_results=5
        )

        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_candidates = [
            meta["candidate_id"]
            for meta in metadatas
        ]

        top1_candidate = retrieved_candidates[0]

        top1_pass = top1_candidate == expected_candidate
        top3_pass = expected_candidate in retrieved_candidates[:3]

        if top1_pass:
            top1_correct += 1

        if top3_pass:
            top3_correct += 1

        details.append({
            "query": question,
            "expected": expected_candidate,
            "retrieved": retrieved_candidates,
            "top1": top1_pass,
            "top3": top3_pass,
            "distances": distances
        })


    return {
        "top1_accuracy": top1_correct / total,
        "top3_accuracy": top3_correct / total,
        "top1_correct": top1_correct,
        "top3_correct": top3_correct,
        "total": total,
        "details": details
    }



def evaluate_assistant(tests):

    correct = 0
    total = len(tests)

    details = []

    for question, expected_keyword in tests:

        answer = ask_rag(question)

        passed = (
            expected_keyword.lower()
            in answer.lower()
        )

        if passed:
            correct += 1

        details.append({
            "question": question,
            "answer": answer,
            "expected": expected_keyword,
            "passed": passed
        })


    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total,
        "details": details
    }



def evaluate_recommendation(tests):

    correct = 0
    total = len(tests)

    details = []

    for question, expected_candidate in tests:

        result = ask_recommendation(question)

        candidate_id = str(
            result.get("candidate_id")
        )

        passed = (
            candidate_id == str(expected_candidate)
        )

        if passed:
            correct += 1

        details.append({
            "question": question,
            "expected": expected_candidate,
            "actual": candidate_id,
            "match_score": result.get("match_score"),
            "passed": passed
        })


    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total,
        "details": details
    }