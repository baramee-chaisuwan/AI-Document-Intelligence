from pydantic import BaseModel
from typing import List, Optional, Dict, Any


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
    description: List[str] = []

class Project(BaseModel):
    name: str
    description: List[str] = []
    technologies: List[str] = []

class ResumeData(BaseModel):
    name: str
    skills: List[str] = []
    languages: List[str] = []
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Dict[str, Any]] = [] 

class ResumeResponse(BaseModel):
    filename: str
    message: str
    summary: str

    resume_data: Dict[str, Any]
    analysis: Dict[str, Any]


class DuplicateResponse(BaseModel):
    status: str = "duplicate"
    message: str
    existing_id: int
    filename: str