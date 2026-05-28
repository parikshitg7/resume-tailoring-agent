from pydantic import BaseModel, Field
from typing import List

class JDAnalysis(BaseModel):
    """Schema for the structured analysis of a Job Description."""
    required_technical_skills: List[str] = Field(description="List of core technical skills, languages, frameworks required.")
    soft_skills: List[str] = Field(description="Soft skills or behavioral traits mentioned in the JD.")
    experience_level: str = Field(description="Target experience or role level (e.g., Entry-level, Internship, Associate).")
    key_responsibilities: List[str] = Field(description="Top 3-5 major daily responsibilities or projects described.")
    estimated_ats_keywords: List[str] = Field(description="High-value keywords specific to this company or role that an ATS would look for.")
    