from pydantic import BaseModel
from typing import List
from typing import Optional


class Education(BaseModel):

    institution: str

    degree: str

    start_date: Optional[str] = None

    end_date: Optional[str] = None


class Experience(BaseModel):

    title: str

    company: str

    start_date: Optional[str] = None

    end_date: Optional[str] = None

    description: List[str]


class ResumeData(BaseModel):

    name: str

    skills: List[str]

    languages: List[str]

    education: List[Education]

    experience: List[Experience]


class ResumeResponse(BaseModel):

    filename: str

    message: str

    summary: str

    resume_data: ResumeData