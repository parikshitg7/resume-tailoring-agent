import os
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from graph import ResumeAgentState
from schemas import PersonalInformation, Education, Experience, Project

# ==========================================
# 1. STANDALONE NODES SCHEMAS
# ==========================================

class StaticProfileSchema(BaseModel):
    personal_info: PersonalInformation
    education: List[Education]

class DynamicProfileSchema(BaseModel):
    """Schema for tailored, JD-dependent resume content."""
    summary: str = Field(description="A strong, 3-line professional summary tailored to the target JD")
    skills: str = Field(description="Comma-separated list of highly relevant technical skills matching the target JD")
    experience: List[Experience] = Field(description="Tailored work experiences matching the JD or utilizing fallbacks")
    projects: List[Project] = Field(description="Tailored projects matching the JD or utilizing fallbacks")


# ==========================================
# 2. LANGGRAPH NODE FUNCTIONS
# ==========================================

def extract_static_info_node(state: ResumeAgentState) -> Dict[str, Any]:
    """
    Reads the user's old resume text and extracts unchanging profile data
    into a structured format using Groq.
    """
    print("--- NODE: EXTRACTING STATIC PROFILE INFORMATION ---")
    raw_text = state.get("raw_current_resume_text", "")
    
    # Initialize your Groq LLM
    llm = ChatGroq(
        temperature=0.0,
        model_name="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Force the LLM to output exactly our StaticProfileSchema structure
    structured_llm = llm.with_structured_output(StaticProfileSchema)
    
    system_prompt = (
        "You are an expert data extraction assistant. Your job is to extract  "
        "personal contact details and education history from the provided raw resume text. "
        "Do not alter facts, names, or metrics. If a field like GitHub is missing, leave it empty."
    )
    
    # Execute the LLM call
    extracted_data = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Raw Resume Text:\n\n{raw_text}"}
    ])
    
    # Update our master state container with the extracted information
    current_data = state.get("structured_resume_data", {})
    current_data["personal_info"] = extracted_data.personal_info.model_dump()
    current_data["education"] = [edu.model_dump() for edu in extracted_data.education]
    
    return {"structured_resume_data": current_data}


def strategic_matcher_node(state: ResumeAgentState) -> Dict[str, Any]:
    """
    Analyzes the JD, retrieves master data, applies fallback logic, 
    and generates the tailored experience and projects.
    """
    print("--- NODE: RUNNING STRATEGIC JD MATCHER & FALLBACK LOGIC ---")
    
    jd_text = state.get("raw_jd_text", "")
    master_text = state.get("raw_master_text", "") 
    
    # Initialize your Groq LLM
    llm = ChatGroq(
        temperature=0.2, # Slight creativity allowed for writing bullet points
        model_name="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    structured_llm = llm.with_structured_output(DynamicProfileSchema)
    
    # This is the most important prompt in your entire application.
    system_prompt = """You are an elite executive resume writer and ATS optimization expert.
    Your goal is to perfectly map the candidate's Master Data to the Target Job Description (JD).
    
    RULES FOR SELECTION & FALLBACK LOGIC:
    1. DIRECT MATCH: If the candidate has projects/experience directly matching the JD's required skills (e.g., Java, Spring Boot), prioritize them.
    2. THE FALLBACK RULE: If the JD asks for a skill the candidate DOES NOT HAVE, DO NOT leave the section empty. Fall back to their most impressive, complex, or credible adjacent project from the Master Data to prove their general engineering competency. 
    3. NO HALLUCINATION: You may rephrase bullet points to highlight different angles of a project, but do not invent companies, degrees, or projects that do not exist in the Master Data.
    4. BULLET POINTS: Write 3-4 heavy-hitting bullet points per project/job. Start with strong action verbs. Include metrics if available in the master data.
    
    Output a perfectly tailored Professional Summary, a comma-separated Skills list matching the JD, and the tailored Projects and Experience.
    """
    
    user_prompt = f"""
    TARGET JOB DESCRIPTION:
    {jd_text}
    
    CANDIDATE'S MASTER DATA (RAG CONTEXT):
    {master_text}
    """
    
    # Execute the LLM call
    extracted_data = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    # Update our master state container
    current_data = state.get("structured_resume_data", {})
    current_data["summary"] = extracted_data.summary
    current_data["skills"] = extracted_data.skills
    current_data["experience"] = [exp.model_dump() for exp in extracted_data.experience]
    current_data["projects"] = [proj.model_dump() for proj in extracted_data.projects]
    
    return {"structured_resume_data": current_data}