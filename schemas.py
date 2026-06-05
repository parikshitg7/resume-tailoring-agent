from pydantic import BaseModel, Field
from typing import List, Optional

class PersonalInformation(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    linkedin: str = Field(description="LinkedIn profile URL")
    github: Optional[str] = Field(default="", description="GitHub profile URL")
    location: Optional[str] = Field(default="", description="City, Country")

class Education(BaseModel):
    degree: str = Field(description="Degree name, e.g., B.Tech Computer Science")
    university: str = Field(description="University or college name")
    duration: str = Field(description="Dates attended, e.g., 2023 - 2027")
    score: Optional[str] = Field(default="", description="CGPA or percentage")

class Experience(BaseModel):
    job_title: str
    company: str
    duration: str
    bullets: List[str] = Field(description="3-5 impact-driven bullet points matching the target JD")

class Project(BaseModel):
    title: str
    tech_stack: str = Field(description="Key technologies used, e.g., Java, Spring Boot, AWS")
    duration: str
    bullets: List[str] = Field(description="3-4 highly technical, impact-driven bullet points")

class ResumeData(BaseModel):
    """
    The master schema. This exactly mirrors the {{ tags }} we will put in the Word template.
    """
    personal_info: PersonalInformation
    education: List[Education]
    summary: str = Field(description="A strong, 3-line professional summary tailored to the JD")
    skills: str = Field(description="Comma-separated list of highly relevant skills matching the JD")
    experience: List[Experience]
    projects: List[Project]