from typing import List, TypedDict
from schemas import JDAnalysis
from agent import analyze_job_description
from rag import vector_store

# 1. Define the State (The Shared Clipboard)
class AgentState(TypedDict):
    """
    This dictionary holds all the information as it moves through our LangGraph workflow.
    Every node (function) will read from and write to this state.
    """
    jd_text: str
    jd_analysis: JDAnalysis
    retrieved_experiences: List[str]
    drafted_resume: str

    

# Node 1: Analyze the JD
def analyze_jd_node(state: AgentState) -> AgentState:
    print("---NODE: ANALYZING JD---")
    jd_text = state["jd_text"]
    analysis = analyze_job_description(jd_text)
    
    # Update the state with the structured analysis
    state["jd_analysis"] = analysis
    return state

# Node 2: Retrieve Matching Experiences
def retrieve_experiences_node(state: AgentState) -> AgentState:
    print("---NODE: RETRIEVING MEMORIES---")
    analysis = state["jd_analysis"]
    
    # Combine the core skills into a single search query
    search_query = " ".join(analysis.required_technical_skills + analysis.key_responsibilities)
    
    # Search ChromaDB for the top 5 most relevant chunks from your Master Data
    results = vector_store.similarity_search(search_query, k=5)
    extracted_chunks = [doc.page_content for doc in results]
    
    # Update the state with the retrieved memories
    state["retrieved_experiences"] = extracted_chunks
    return state

# Node 3: Draft the Resume (Placeholder for now)
def draft_resume_node(state: AgentState) -> AgentState:
    print("---NODE: DRAFTING RESUME---")
    # We will wire Groq up here in the next step to actually write the resume
    state["drafted_resume"] = "Resume generation logic goes here..."
    return state

