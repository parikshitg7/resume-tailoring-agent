from typing import TypedDict, List, Dict, Any
from schemas import ResumeData

class ResumeAgentState(TypedDict):
    # Inputs from the user
    raw_current_resume_text: str
    raw_jd_text: str
    raw_master_text: str  # Fallback manual text if provided
    
    # Extracted metadata from the JD
    target_keywords: List[str]
    mandatory_skills: List[str]
    
    # The final structured container we are filling up
    # We will initialize this as a dictionary that matches ResumeData
    structured_resume_data: Dict[str, Any]