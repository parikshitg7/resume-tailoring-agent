import os
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from schemas import PersonalInformation, Education, Experience, Project

# ==========================================
# 1. STANDALONE NODES SCHEMAS
# ==========================================

class StaticProfileSchema(BaseModel):
    """Schema for extracting unchanging facts from the current resume."""
    personal_info: PersonalInformation
    education: List[Education]

class DynamicProfileSchema(BaseModel):
    """Schema for tailored, JD-dependent resume content."""
    summary: str 
    skills: str 
    projects: List[Project] 
    experience: List[Experience] 
    certifications: List[str] 
    achievements: List[str] 

# ==========================================
# 2. LANGGRAPH NODE FUNCTIONS
# ==========================================

def extract_static_info_node(state: dict) -> Dict[str, Any]:
    """
    Reads the user's old base resume and cleanly extracts unchanging profile data.
    """
    print("--- NODE: EXTRACTING STATIC PROFILE INFORMATION ---")
    raw_text = state.get("raw_current_resume_text", "")
    
    llm = ChatGroq(
        temperature=0.0,
        model_name="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    structured_llm = llm.with_structured_output(StaticProfileSchema)
    
    system_prompt = (
        "You are an expert data extraction assistant. Your job is to extract "
        "personal contact details and education history from the provided raw resume text. "
        "Do not alter facts, names, or metrics. If a field like GitHub is missing, leave it empty."
    )
    
    extracted_data = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Raw Resume Text:\n\n{raw_text}"}
    ])
    
    current_data = state.get("structured_resume_data", {})
    current_data["personal_info"] = extracted_data.personal_info.model_dump()
    current_data["education"] = [edu.model_dump() for edu in extracted_data.education]
    
    return {"structured_resume_data": current_data}

def strategic_matcher_node(state: dict) -> Dict[str, Any]:
    """
    Analyzes the JD, retrieves master data, applies fallback logic, 
    and generates the tailored bullets and summaries.
    """
    print("--- NODE: RUNNING STRATEGIC JD MATCHER & FALLBACK LOGIC ---")
    
    jd_text = state.get("raw_jd_text", "")
    master_text = state.get("raw_master_text", "") 
    
    llm = ChatGroq(
        temperature=0.2, 
        model_name="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    structured_llm = llm.with_structured_output(DynamicProfileSchema)
    
    system_prompt = """You are an elite executive resume writer and ATS optimization expert.
    Your goal is to perfectly map the candidate's Master Data to the Target Job Description (JD).
    
    RULES FOR SELECTION & FALLBACK LOGIC:
    1. DIRECT MATCH: If the candidate has experience/projects directly matching the JD's required skills, prioritize them.
    2. THE FALLBACK RULE: If the JD asks for a skill the candidate DOES NOT HAVE, DO NOT leave the section empty. Fall back to their most impressive, complex, or credible adjacent project/experience from the Master Data to prove their general competency.
    3. NO HALLUCINATION: Do not invent experience, projects, certifications, or achievements that do not exist in the Master Data.
    4. BULLET POINTS: Write heavy-hitting bullet points per job/project. Start with strong action verbs. Include metrics if available. Extract the absolute best material to make the candidate look highly qualified for this specific JD.
    
    Output a perfectly tailored Professional Summary, Skills list, Experience, Projects, Certifications, and Achievements.
    """
    
    user_prompt = f"""
    TARGET JOB DESCRIPTION:
    {jd_text}
    
    CANDIDATE'S MASTER DATA:
    {master_text}
    """
    
    extracted_data = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    current_data = state.get("structured_resume_data", {})
    current_data["summary"] = extracted_data.summary
    current_data["skills"] = extracted_data.skills
    current_data["projects"] = [proj.model_dump() for proj in extracted_data.projects]
    current_data["experience"] = [exp.model_dump() for exp in extracted_data.experience]
    current_data["certifications"] = extracted_data.certifications
    current_data["achievements"] = extracted_data.achievements
    
    return {"structured_resume_data": current_data}