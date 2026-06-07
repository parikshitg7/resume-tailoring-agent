from pydantic import BaseModel, Field
from typing import List, Optional

class PersonalInformation(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    linkedin: str = Field(description="LinkedIn profile URL")
    github: Optional[str] = Field(default="", description="GitHub profile URL")
    location: Optional[str] = Field(default="", description="City, Country or City, State")

class Education(BaseModel):
    degree: str = Field(description="Degree name, e.g., B.Tech Computer Science")
    university: str = Field(description="University or school name (Just the name)")
    location: str = Field(description="City and State")
    duration: str = Field(description="Dates attended, e.g., 2023 - 2027")
    score: Optional[str] = Field(default="", description="Just the number, e.g., 8.4/10 or 94%")

class Project(BaseModel):
    title: str = Field(description="Name of the project")
    tech_stack: str = Field(description="Key technologies used, separated by commas, e.g., Java, Spring Boot, MySQL")
    bullets: List[str] = Field(description="3-4 highly technical, impact-driven bullet points tailored to the target JD")

class Experience(BaseModel):
    job_title: str
    company: str
    duration: str
    bullets: List[str] = Field(description="3-4 impact-driven bullet points matching the target JD")

class ResumeData(BaseModel):
    """
    The master schema. This exactly mirrors the {{ tags }} in the docxtpl Word template.
    """
    personal_info: PersonalInformation
    summary: str = Field(description="A strong, 3-line professional objective tailored to the target JD")
    education: List[Education]
    skills: str = Field(description="Comma-separated list of highly relevant technical skills matching the target JD")
    projects: List[Project]
    experience: List[Experience]
    certifications: List[str]
    achievements: List[str]