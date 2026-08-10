from enum import Enum


class CandidateStage(str, Enum):

    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


CANDIDATE_STAGE_CHECK_SQL = (
    "candidate_stage IN ("
    + ", ".join(
        f"'{stage.value}'"
        for stage in CandidateStage
    )
    + ")"
)
