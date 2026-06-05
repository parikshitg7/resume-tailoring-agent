import os
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from graph import ResumeAgentState
from schemas import PersonalInformation, Education

# A mini-schema just for this node's isolated output
class StaticProfileSchema(BaseModel):
    personal_info: PersonalInformation
    education: List[Education]

def extract_static_info_node(state: ResumeAgentState) -> Dict[str, Any]:
    """
    Reads the user's old resume text and extracts unchanging profile data
    into a structured format using Groq.
    """
    print("--- EXTRACTING STATIC PROFILE INFORMATION ---")
    raw_text = state.get("raw_current_resume_text", "")
    
    # Initialize your Groq LLM
    llm = ChatGroq(
        temperature=0.0,
        model_name="llama-3.3-70b-versatile", # Or your preferred Groq model
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Force the LLM to output exactly our StaticProfileSchema structure
    structured_llm = llm.with_structured_output(StaticProfileSchema)
    
    system_prompt = (
        "You are an expert data extraction assistant. Your job is to extract "
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