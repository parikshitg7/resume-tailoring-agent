from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from utils import extract_text_from_pdf, chunk_text_by_type
from rag import store_chunks_in_db
from agent import analyze_job_description

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
@app.post("/upload-jd/")
async def upload_jd(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    
    # Run the Groq structured analysis engine
    structured_analysis = analyze_job_description(text)
    
    return {
        "filename": file.filename,
        "status": "Analysis Completed by Groq (Llama 3)",
        "analysis": structured_analysis
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