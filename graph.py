from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END
from schemas import JDAnalysis

# Import the Groq LLM and the structured analyzer from your agent
from agent import analyze_job_description, llm
from rag import vector_store

# 1. Define the State
class AgentState(TypedDict):
    jd_text: str
    jd_analysis: JDAnalysis
    retrieved_experiences: List[str]
    drafted_resume: str

# --- 2. Define the Nodes ---

def analyze_jd_node(state: AgentState) -> AgentState:
    print("--- NODE: ANALYZING JD ---")
    jd_text = state["jd_text"]
    analysis = analyze_job_description(jd_text)
    state["jd_analysis"] = analysis
    return state

def retrieve_experiences_node(state: AgentState) -> AgentState:
    print("--- NODE: RETRIEVING MEMORIES ---")
    analysis = state["jd_analysis"]
    
    # Combine the core skills into a single database search query
    search_query = " ".join(analysis.required_technical_skills + analysis.key_responsibilities)
    
    # Search ChromaDB for the top 5 most relevant chunks from your Master Data
    results = vector_store.similarity_search(search_query, k=5)
    extracted_chunks = [doc.page_content for doc in results]
    
    state["retrieved_experiences"] = extracted_chunks
    return state

# UPDATED: We replaced the placeholder with an actual Groq LLM call
def draft_resume_node(state: AgentState) -> AgentState:
    print("--- NODE: DRAFTING RESUME ---")
    analysis = state["jd_analysis"]
    experiences = "\n\n".join(state["retrieved_experiences"])
    
    # Prompt Groq to write the resume using ONLY your retrieved memories
    prompt = f"""
    You are an expert technical ATS-resume writer.
    
    TARGET JOB REQUIREMENTS:
    {analysis.model_dump_json(indent=2)}
    
    CANDIDATE'S VERIFIED EXPERIENCES:
    {experiences}
    
    Task: Write a highly tailored professional resume summary and 3-5 experience bullet points. 
    Rule: You MUST base the bullet points ONLY on the 'Verified Experiences' provided. Do not invent or hallucinate skills.
    """
    
    # Call the base Groq LLM (no structured output here, we want natural text)
    response = llm.invoke(prompt)
    state["drafted_resume"] = response.content
    return state

# --- 3. Build and Compile the Graph (The Routing) ---

workflow = StateGraph(AgentState)

# Add the nodes to the graph
workflow.add_node("analyze_jd", analyze_jd_node)
workflow.add_node("retrieve_experiences", retrieve_experiences_node)
workflow.add_node("draft_resume", draft_resume_node)

# Define the precise flow of execution
workflow.add_edge(START, "analyze_jd")
workflow.add_edge("analyze_jd", "retrieve_experiences")
workflow.add_edge("retrieve_experiences", "draft_resume")
workflow.add_edge("draft_resume", END)

# Compile the graph into an executable application
ats_agent = workflow.compile()