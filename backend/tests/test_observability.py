import json
import logging
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.rag import embedding_service, rag_chain
from app.services import (
    gemini_service,
    indexing_service
)
from app.services.observability_service import (
    install_request_logging,
    observe_operation
)
from app.services import observability_service


@pytest.fixture(autouse=True)
def capture_observability_logs(caplog):

    observability_service.logger.addHandler(
        caplog.handler
    )
    yield
    observability_service.logger.removeHandler(
        caplog.handler
    )


def events(caplog):

    return [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "ats.observability"
    ]


def test_request_logging_is_structured_and_excludes_sensitive_data(
    caplog
):

    test_app = FastAPI()
    install_request_logging(
        test_app,
        default_service="test-api"
    )

    @test_app.post("/echo/{item_id}")
    async def echo(item_id: int, request: Request):
        await request.body()
        return {"item_id": item_id}

    caplog.set_level(logging.INFO, logger="ats.observability")
    response = TestClient(test_app).post(
        "/echo/42",
        headers={"Authorization": "Bearer private-jwt"},
        content='{"password":"private-password"}',
        follow_redirects=False
    )

    assert response.status_code == 200
    request_event = events(caplog)[-1]
    assert request_event["event"] == "http_request"
    assert request_event["service"] == "test-api"
    assert request_event["method"] == "POST"
    assert request_event["route"] == "/echo/{item_id}"
    assert request_event["status_code"] == 200
    assert request_event["duration_ms"] >= 0

    logged = " ".join(
        record.message
        for record in caplog.records
    )
    assert "private-jwt" not in logged
    assert "private-password" not in logged
    assert '"item_id":42' not in logged


def test_gemini_summary_preserves_result_and_emits_timing(
    monkeypatch,
    caplog
):

    model = Mock()
    model.generate_content.return_value = Mock(
        text="Expected summary"
    )
    monkeypatch.setattr(gemini_service, "get_model", lambda: model)
    caplog.set_level(logging.INFO, logger="ats.observability")

    result = gemini_service.summarize_document("private resume text")

    assert result == "Expected summary"
    event = events(caplog)[-1]
    assert event["operation"] == "gemini_resume_summarization"
    assert event["outcome"] == "success"
    assert "private resume text" not in event.values()


def test_gemini_failure_event_is_safe_and_behavior_is_preserved(
    monkeypatch,
    caplog
):

    model = Mock()
    model.generate_content.side_effect = RuntimeError(
        "provider secret=do-not-log"
    )
    monkeypatch.setattr(gemini_service, "get_model", lambda: model)
    caplog.set_level(logging.INFO, logger="ats.observability")

    result = gemini_service.summarize_document("private resume text")

    assert result == "Summary generation failed"
    event = events(caplog)[-1]
    assert event["event"] == "operation_failed"
    assert event["error_category"] == "RuntimeError"
    assert "do-not-log" not in json.dumps(event)
    assert "private resume text" not in json.dumps(event)


def test_embedding_timing_preserves_original_return_value(
    monkeypatch,
    caplog
):

    expected = [0.25] * embedding_service.EMBEDDING_DIMENSION
    model = Mock()
    model.encode.return_value = expected
    monkeypatch.setattr(embedding_service, "get_model", lambda: model)
    caplog.set_level(logging.INFO, logger="ats.observability")

    result = embedding_service.create_embedding("private input")

    assert result is expected
    event = events(caplog)[-1]
    assert event["operation"] == "embedding_generation"
    assert event["batch_size"] == 1
    assert "private input" not in json.dumps(event)


def test_indexing_timing_preserves_result(
    monkeypatch,
    caplog
):

    monkeypatch.setattr(
        indexing_service,
        "split_resume",
        lambda text: ["private chunk"]
    )
    monkeypatch.setattr(
        indexing_service,
        "create_embeddings",
        lambda chunks: [[0.0] * 384]
    )
    replace = Mock()
    monkeypatch.setattr(
        indexing_service.resume_chunk_repository,
        "replace_candidate_chunks",
        replace
    )
    caplog.set_level(logging.INFO, logger="ats.observability")

    result = indexing_service.index_resume(
        Mock(),
        7,
        "private resume text"
    )

    assert result == {
        "candidate_id": "7",
        "chunk_count": 1,
        "status": "indexed"
    }
    event = [
        item
        for item in events(caplog)
        if item.get("operation") == "resume_indexing"
    ][-1]
    assert event["outcome"] == "success"
    assert "private resume text" not in json.dumps(event)


def test_rag_retrieval_timing_preserves_empty_result(
    monkeypatch,
    caplog
):

    monkeypatch.setattr(
        rag_chain,
        "hybrid_search",
        lambda **kwargs: {"documents": [[]], "metadatas": [[]]}
    )
    caplog.set_level(logging.INFO, logger="ats.observability")

    result = rag_chain.ask_rag("private recruiter question")

    assert result == rag_chain.NO_INFORMATION_MESSAGE
    event = events(caplog)[-1]
    assert event["operation"] == "rag_retrieval"
    assert event["outcome"] == "success"
    assert "private recruiter question" not in json.dumps(event)


def test_rag_generation_timing_preserves_result_and_failure(
    monkeypatch,
    caplog
):

    retrieval_result = {
        "documents": [["private resume evidence"]],
        "metadatas": [[{"candidate_id": "7"}]]
    }
    chain = Mock()
    chain.invoke.return_value = "Expected answer"
    monkeypatch.setattr(
        rag_chain,
        "hybrid_search",
        lambda **kwargs: retrieval_result
    )
    monkeypatch.setattr(
        rag_chain,
        "get_assistant_rag_chain",
        lambda: chain
    )
    caplog.set_level(logging.INFO, logger="ats.observability")

    assert rag_chain.ask_rag("private question") == "Expected answer"
    generation_event = [
        event
        for event in events(caplog)
        if event.get("operation") == "rag_answer_generation"
    ][-1]
    assert generation_event["outcome"] == "success"
    assert "private resume evidence" not in json.dumps(
        generation_event
    )

    caplog.clear()
    chain.invoke.side_effect = RuntimeError(
        "provider response do-not-log"
    )

    with pytest.raises(RuntimeError, match="do-not-log"):
        rag_chain.ask_rag("private question")

    failure_event = [
        event
        for event in events(caplog)
        if event.get("operation") == "rag_answer_generation"
    ][-1]
    assert failure_event["outcome"] == "failure"
    assert failure_event["error_category"] == "RuntimeError"
    assert "do-not-log" not in json.dumps(failure_event)


def test_observation_preserves_original_exception(caplog):

    caplog.set_level(logging.INFO, logger="ats.observability")

    with pytest.raises(ValueError, match="original failure"):
        with observe_operation("test_operation"):
            raise ValueError("original failure")

    event = events(caplog)[-1]
    assert event["error_category"] == "ValueError"
    assert "original failure" not in json.dumps(event)
