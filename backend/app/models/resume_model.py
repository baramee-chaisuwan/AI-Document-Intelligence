from typing import (
    Any,
    Dict,
    List,
    Optional
)

from pydantic import (
    BaseModel,
    Field
)


class Education(BaseModel):

    institution: str = ""
    degree: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Experience(BaseModel):

    title: str = ""
    company: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    description: List[str] = Field(
        default_factory=list
    )


class Project(BaseModel):

    name: str = ""

    description: List[str] = Field(
        default_factory=list
    )

    technologies: List[str] = Field(
        default_factory=list
    )


class ResumeData(BaseModel):

    name: str = ""

    skills: List[str] = Field(
        default_factory=list
    )

    languages: List[str] = Field(
        default_factory=list
    )

    education: List[Education] = Field(
        default_factory=list
    )

    experience: List[Experience] = Field(
        default_factory=list
    )

    projects: List[Project] = Field(
        default_factory=list
    )


class ResumeResponse(BaseModel):

    candidate_id: int

    filename: str
    message: str
    summary: str

    resume_data: ResumeData
    analysis: Dict[str, Any]


class DuplicateResponse(BaseModel):

    status: str = "duplicate"
    message: str
    existing_id: int
    filename: str