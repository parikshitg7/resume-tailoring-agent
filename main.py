from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from utils import extract_text_from_pdf, chunk_text_by_type
from rag import store_chunks_in_db
from agent import analyze_job_description
from graph import ats_agent


app = FastAPI(title="Autonomous ATS-Buster API")

@app.get("/")
def read_root():
    return {"status": "Agent is online and ready."}

@app.post("/upload-master/")
async def upload_master(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text_by_type(text, doc_type="master")
    chunks_saved = store_chunks_in_db(chunks, file.filename)
    return {
        "filename": file.filename,
        "chunks_saved_to_db": chunks_saved,
        "message": "Master Data memorized successfully."
    }

# UPDATED: This now triggers the Groq API for lightning-fast analysis
# UPDATED: This now triggers the entire Agentic Loop!
@app.post("/upload-jd/")
async def upload_jd(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    
    # 1. Initialize the State with the raw JD text
    initial_state = {"jd_text": text}
    
    # 2. Run the LangGraph state machine
    final_state = ats_agent.invoke(initial_state)
    
    # 3. Return the drafted text and the exact memories used
    return {
        "status": "Resume Tailored Successfully",
        "retrieved_memories_used": len(final_state["retrieved_experiences"]),
        "tailored_draft": final_state["drafted_resume"]
    }

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text_by_type(text, doc_type="resume")
    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "status": "Resume loaded for gap analysis"
    }