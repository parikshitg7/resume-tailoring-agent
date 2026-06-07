from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from agent import extract_static_info_node, strategic_matcher_node

# The central memory object passed between nodes
class ResumeAgentState(TypedDict):
    raw_current_resume_text: str
    raw_jd_text: str
    raw_master_text: str 
    structured_resume_data: Dict[str, Any]

def build_resume_graph():
    """
    Compiles the LangGraph workflow.
    Flow: Start -> Extract Static Info -> Match JD & Apply Fallback -> End
    """
    workflow = StateGraph(ResumeAgentState)
    
    # Add our two nodes
    workflow.add_node("extract_static", extract_static_info_node)
    workflow.add_node("strategic_match", strategic_matcher_node)
    
    # Define the execution flow
    workflow.set_entry_point("extract_static")
    workflow.add_edge("extract_static", "strategic_match")
    workflow.add_edge("strategic_match", END)
    
    # Compile and return the executable graph
    return workflow.compile()