from unittest.mock import Mock
import hashlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import config
from app.core.exceptions import NotFoundError
from app.database.database import Base
from app.database.models import (
    Candidate,
    ResumeChunk,
    ResumeProcessingJob
)
from app.models.processing_job_status import (
    ProcessingJobStatus
)
from app.models.resume_processing_message import (
    ResumeProcessingMessageError
)
from app.services import (
    processing_job_service,
    resume_processing_worker
)
from app.repositories import processing_job_repository
from app.services.resume_processing_worker import (
    ResumeWorkerError,
    WorkerOutcome
)


engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)


@pytest.fixture(autouse=True)
def isolated_worker_database(monkeypatch):

    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )

    yield

    Base.metadata.drop_all(bind=engine)


def message(job_id: int) -> dict:

    return {
        "version": 1,
        "processing_job_id": job_id,
        "gcs_object_key": "resumes/input/document.pdf"
    }


def candidate_processor(call_counter=None):

    def process(db, object_key):

        if call_counter is not None:
            call_counter["count"] += 1

        candidate = Candidate(
            name="Async Candidate",
            summary="Backend engineer",
            candidate_level="Senior",
            skill_score=90,
            rule_score=88,
            ai_score=92,
            ai_status="success",
            score_breakdown={},
            resume_storage_key=object_key
        )
        db.add(candidate)
        db.flush()

        db.add(
            ResumeChunk(
                candidate_id=candidate.id,
                document_id=f"{candidate.id}_0",
                chunk_index=0,
                chunk_text="Backend engineer resume",
                embedding=[0.0] * 384
            )
        )
        db.flush()

        return candidate

    return process


def test_pending_job_processes_and_associates_candidate():

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        commit = Mock(wraps=db.commit)
        db.commit = commit
        result = (
            resume_processing_worker
            .handle_resume_processing_message(
                db,
                message(job.id),
                processor=candidate_processor()
            )
        )

        assert result.outcome == WorkerOutcome.COMPLETED
        assert result.candidate_id is not None

        persisted_job = db.get(ResumeProcessingJob, job.id)
        candidate = db.get(Candidate, result.candidate_id)
        chunks = (
            db.query(ResumeChunk)
            .filter(ResumeChunk.candidate_id == candidate.id)
            .all()
        )
        assert persisted_job is not None
        assert persisted_job.status == "COMPLETED"
        assert persisted_job.started_at is not None
        assert persisted_job.completed_at is not None
        assert persisted_job.candidate_id == candidate.id
        assert candidate.resume_storage_key == (
            "resumes/input/document.pdf"
        )
        assert len(chunks) == 1
        assert chunks[0].chunk_text == "Backend engineer resume"
        assert commit.call_count == 2


def test_failure_after_association_flush_rolls_back_candidate_data(
    monkeypatch
):

    associate_candidate = (
        processing_job_repository.associate_candidate
    )

    def associate_then_fail(db, job, candidate_id):
        associate_candidate(db, job, candidate_id)
        db.flush()
        raise RuntimeError("failure after candidate association")

    monkeypatch.setattr(
        processing_job_repository,
        "associate_candidate",
        associate_then_fail
    )

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        with pytest.raises(ResumeWorkerError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(job.id),
                    processor=candidate_processor()
                )
            )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        assert persisted_job.status == "FAILED"
        assert persisted_job.candidate_id is None
        assert db.query(Candidate).count() == 0
        assert db.query(ResumeChunk).count() == 0


def test_indexing_failure_rolls_back_flushed_candidate_and_chunks(
    monkeypatch
):

    monkeypatch.setattr(
        resume_processing_worker.gcs_storage_service,
        "get_object",
        Mock(return_value=b"%PDF-1.7 test")
    )
    monkeypatch.setattr(
        resume_processing_worker.pdf_service,
        "extract_text_from_pdf",
        Mock(return_value="Resume text")
    )
    monkeypatch.setattr(
        resume_processing_worker.extraction_service,
        "extract_resume_data",
        Mock(return_value={"name": "Index Failure Candidate"})
    )
    monkeypatch.setattr(
        resume_processing_worker.gemini_service,
        "summarize_document",
        Mock(return_value="Candidate summary")
    )
    monkeypatch.setattr(
        resume_processing_worker.analyzer_service,
        "analyze_resume",
        Mock(return_value={
            "candidate_level": "Senior",
            "skill_score": 90,
            "rule_score": 88,
            "ai_score": 92,
            "ai_status": "success",
            "score_breakdown": {}
        })
    )

    def fail_indexing_after_chunk_flush(
        db,
        document_id,
        resume_text
    ):
        db.add(
            ResumeChunk(
                candidate_id=document_id,
                document_id=f"{document_id}_0",
                chunk_index=0,
                chunk_text=resume_text,
                embedding=[0.0] * 384
            )
        )
        db.flush()
        raise RuntimeError("index persistence failed")

    monkeypatch.setattr(
        resume_processing_worker.indexing_service,
        "index_resume",
        fail_indexing_after_chunk_flush
    )

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        with pytest.raises(ResumeWorkerError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(job.id)
                )
            )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        assert persisted_job.status == "FAILED"
        assert persisted_job.candidate_id is None
        assert db.query(Candidate).count() == 0
        assert db.query(ResumeChunk).count() == 0


def test_completion_conflict_rolls_back_data_and_preserves_terminal_state(
    monkeypatch
):

    transition = (
        processing_job_repository.transition_processing_job
    )

    def conflict_on_completion(**kwargs):
        if kwargs["next_status"] != "COMPLETED":
            return transition(**kwargs)

        db = kwargs["db"]
        db.rollback()
        (
            db.query(ResumeProcessingJob)
            .filter(ResumeProcessingJob.id == kwargs["job_id"])
            .update(
                {
                    "status": "COMPLETED",
                    "completed_at": kwargs["transitioned_at"],
                    "updated_at": kwargs["transitioned_at"]
                },
                synchronize_session=False
            )
        )
        db.commit()
        return None

    monkeypatch.setattr(
        processing_job_repository,
        "transition_processing_job",
        conflict_on_completion
    )

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        with pytest.raises(ResumeWorkerError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(job.id),
                    processor=candidate_processor()
                )
            )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        assert persisted_job.status == "COMPLETED"
        assert persisted_job.candidate_id is None
        assert db.query(Candidate).count() == 0
        assert db.query(ResumeChunk).count() == 0


def test_processing_failure_marks_job_failed():

    def fail_processing(db, object_key):
        raise RuntimeError(
            "internal provider detail"
        )

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        with pytest.raises(
            ResumeWorkerError,
            match="Resume processing failed"
        ) as exc_info:
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(job.id),
                    processor=fail_processing
                )
            )

        assert isinstance(exc_info.value.__cause__, RuntimeError)
        persisted = db.get(ResumeProcessingJob, job.id)
        assert persisted is not None
        assert persisted.status == "FAILED"
        assert persisted.completed_at is not None
        assert persisted.error_message == (
            processing_job_service.DEFAULT_PROCESSING_ERROR
        )
        assert "provider" not in persisted.error_message


def test_completed_duplicate_is_safe_no_op():

    counter = {"count": 0}

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        processor = candidate_processor(counter)
        first = (
            resume_processing_worker
            .handle_resume_processing_message(
                db,
                message(job.id),
                processor=processor
            )
        )
        duplicate = (
            resume_processing_worker
            .handle_resume_processing_message(
                db,
                message(job.id),
                processor=processor
            )
        )

        assert first.outcome == WorkerOutcome.COMPLETED
        assert duplicate.outcome == (
            WorkerOutcome.ALREADY_COMPLETED
        )
        assert duplicate.candidate_id == first.candidate_id
        assert counter["count"] == 1


def test_processing_duplicate_does_not_execute_processor():

    processor = Mock()

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        processing_job_service.transition_processing_job(
            db,
            job.id,
            ProcessingJobStatus.PROCESSING
        )

        result = (
            resume_processing_worker
            .handle_resume_processing_message(
                db,
                message(job.id),
                processor=processor
            )
        )

        assert result.outcome == (
            WorkerOutcome.ALREADY_PROCESSING
        )
        processor.assert_not_called()


def test_failed_duplicate_does_not_reopen_job():

    processor = Mock()

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        processing_job_service.transition_processing_job(
            db,
            job.id,
            ProcessingJobStatus.PROCESSING
        )
        processing_job_service.transition_processing_job(
            db,
            job.id,
            ProcessingJobStatus.FAILED,
            error_message="Resume processing failed"
        )

        result = (
            resume_processing_worker
            .handle_resume_processing_message(
                db,
                message(job.id),
                processor=processor
            )
        )

        assert result.outcome == WorkerOutcome.TERMINAL_FAILED
        processor.assert_not_called()
        assert db.get(
            ResumeProcessingJob,
            job.id
        ).status == "FAILED"


def test_missing_processing_job_is_rejected():

    with TestingSessionLocal() as db:
        with pytest.raises(NotFoundError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(999999),
                    processor=Mock()
                )
            )


def test_malformed_worker_message_is_rejected():

    with TestingSessionLocal() as db:
        with pytest.raises(ResumeProcessingMessageError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    b"not-json",
                    processor=Mock()
                )
            )


def test_default_processor_reuses_existing_services(
    monkeypatch
):

    get_object = Mock(return_value=b"%PDF-1.7 test")
    extract_text = Mock(return_value="Resume text")
    extract_data = Mock(return_value={
        "name": "Worker Candidate"
    })
    summarize = Mock(return_value="Candidate summary")
    analyze = Mock(return_value={
        "candidate_level": "Mid-Level",
        "skill_score": 84,
        "rule_score": 82,
        "ai_score": 90,
        "ai_status": "success",
        "score_breakdown": {}
    })
    index_resume = Mock()

    monkeypatch.setattr(
        resume_processing_worker.gcs_storage_service,
        "get_object",
        get_object
    )
    monkeypatch.setattr(
        resume_processing_worker.pdf_service,
        "extract_text_from_pdf",
        extract_text
    )
    monkeypatch.setattr(
        resume_processing_worker.extraction_service,
        "extract_resume_data",
        extract_data
    )
    monkeypatch.setattr(
        resume_processing_worker.gemini_service,
        "summarize_document",
        summarize
    )
    monkeypatch.setattr(
        resume_processing_worker.analyzer_service,
        "analyze_resume",
        analyze
    )
    monkeypatch.setattr(
        resume_processing_worker.indexing_service,
        "index_resume",
        index_resume
    )

    with TestingSessionLocal() as db:
        candidate = (
            resume_processing_worker
            .process_resume_from_gcs(
                db,
                "resumes/input/document.pdf"
            )
        )

        assert candidate.id is not None
        assert candidate.name == "Worker Candidate"
        assert candidate.resume_storage_key == (
            "resumes/input/document.pdf"
        )
        assert candidate.resume_sha256 == hashlib.sha256(
            b"%PDF-1.7 test"
        ).hexdigest()
        get_object.assert_called_once_with(
            "resumes/input/document.pdf"
        )
        extract_text.assert_called_once_with(
            b"%PDF-1.7 test"
        )
        extract_data.assert_called_once_with("Resume text")
        summarize.assert_called_once_with("Resume text")
        analyze.assert_called_once_with({
            "name": "Worker Candidate"
        })
        index_resume.assert_called_once_with(
            db=db,
            document_id=candidate.id,
            resume_text="Resume text"
        )


def test_candidate_uniqueness_conflict_leaves_no_partial_worker_data():

    resume_sha256 = "a" * 64

    def conflicting_processor(db, object_key):
        candidate = Candidate(
            name="Duplicate Candidate",
            summary="Duplicate",
            candidate_level="Senior",
            skill_score=90,
            rule_score=90,
            ai_score=90,
            ai_status="success",
            score_breakdown={},
            resume_storage_key=object_key,
            resume_sha256=resume_sha256
        )
        db.add(candidate)
        db.flush()
        return candidate

    with TestingSessionLocal() as db:
        existing = Candidate(
            name="Existing Candidate",
            summary="Existing",
            candidate_level="Senior",
            skill_score=95,
            rule_score=95,
            ai_score=95,
            ai_status="success",
            score_breakdown={},
            resume_sha256=resume_sha256
        )
        db.add(existing)
        db.commit()

        job = processing_job_service.create_processing_job(
            db,
            resume_sha256=resume_sha256
        )

        with pytest.raises(ResumeWorkerError):
            (
                resume_processing_worker
                .handle_resume_processing_message(
                    db,
                    message(job.id),
                    processor=conflicting_processor
                )
            )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        assert persisted_job.status == "FAILED"
        assert persisted_job.candidate_id is None
        assert persisted_job.resume_sha256 is None
        assert db.query(Candidate).count() == 1
        assert db.query(ResumeChunk).count() == 0
