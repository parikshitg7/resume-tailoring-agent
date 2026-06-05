from typing import List, TypedDict, Any
from langgraph.graph import StateGraph, START, END
from schemas import JDAnalysis, GeneratedResume
from agent import analyze_job_description, llm
from rag import vector_store
from document_cloner import replace_experience_bullets
import io

# 1. Update the State Clipboard
class AgentState(TypedDict):
    jd_text: str
    jd_analysis: JDAnalysis
    retrieved_experiences: List[str]
    resume_structure: Any  # Holds the parsed ResumeStructure object
    generated_resume: GeneratedResume  # The structured AI output
    output_docx_bytes: bytes  # The final binary file ready for download

# --- 2. Define the Nodes ---

def analyze_jd_node(state: AgentState) -> AgentState:
    print("--- NODE: ANALYZING JD ---")
    state["jd_analysis"] = analyze_job_description(state["jd_text"])
    return state

def retrieve_experiences_node(state: AgentState) -> AgentState:
    print("--- NODE: RETRIEVING MEMORIES ---")
    analysis = state["jd_analysis"]
    search_query = " ".join(analysis.required_technical_skills + analysis.key_responsibilities)
    results = vector_store.similarity_search(search_query, k=5)
    state["retrieved_experiences"] = [doc.page_content for doc in results]
    return state

def draft_resume_node(state: AgentState) -> AgentState:
    print("--- NODE: DRAFTING ELITE BULLETS ---")
    analysis = state["jd_analysis"]
    rag_context = "\n\n".join(state["retrieved_experiences"])
    resume_struct = state["resume_structure"]
    
    # Give the AI context on the existing roles it needs to rewrite
    existing_experience_context = "\n".join([
        f"Role: {block.job_title} @ {block.company}"
        for block in resume_struct.dynamic_blocks if block.job_title
    ])

    # The Elite Few-Shot Prompt
    prompt = f"""
    You are an elite FAANG resume writer. Your job is to rewrite the candidate's existing roles using their Master Profile facts to perfectly match the Job Description.

    RULES:
    1. Use the XYZ formula: "Accomplished X by doing Y resulting in Z".
    2. Start every bullet with a strong past-tense verb (e.g., Architected, Engineered, Optimized).
    3. Quantify metrics wherever possible based on the Master Profile.
    4. Embed these exact keywords naturally: {analysis.required_technical_skills}
    
    JOB DESCRIPTION REQUIREMENTS:
    {analysis.model_dump_json(indent=2)}

    CANDIDATE MASTER MEMORIES (Strict Facts to use):
    {rag_context}
    
    ROLES TO REWRITE (Maintain these titles and companies):
    {existing_experience_context}
    """
    
    # Force the Groq LLM to output our exact Pydantic schema
    structured_llm = llm.with_structured_output(GeneratedResume)
    response = structured_llm.invoke(prompt)
    
    state["generated_resume"] = response
    return state

def inject_and_export_node(state: AgentState) -> AgentState:
    print("--- NODE: CLONING & INJECTING XML ---")
    resume_structure = state["resume_structure"]
    
    # Convert Pydantic objects to standard dictionaries for the cloner
    ai_experiences = [exp.model_dump() for exp in state["generated_resume"].experiences]
    
    # Run the XML surgery
    final_doc = replace_experience_bullets(resume_structure, ai_experiences)
    
    # Save the manipulated docx file into a binary buffer in RAM
    buffer = io.BytesIO()
    final_doc.save(buffer)
    state["output_docx_bytes"] = buffer.getvalue()
    
    return state

# --- 3. Build and Compile the Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("analyze_jd", analyze_jd_node)
workflow.add_node("retrieve_experiences", retrieve_experiences_node)
workflow.add_node("draft_resume", draft_resume_node)
workflow.add_node("inject_and_export", inject_and_export_node)

workflow.add_edge(START, "analyze_jd")
workflow.add_edge("analyze_jd", "retrieve_experiences")
workflow.add_edge("retrieve_experiences", "draft_resume")
workflow.add_edge("draft_resume", "inject_and_export")
workflow.add_edge("inject_and_export", END)

ats_agent = workflow.compile()