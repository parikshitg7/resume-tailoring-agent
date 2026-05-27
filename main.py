from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from utils import extract_text_from_pdf, chunk_text_by_type
from rag import store_chunks_in_db

app = FastAPI(title="Autonomous ATS-Buster API")

@app.get("/")
def read_root():
    return {"status": "Agent is online and ready."}

# ROUTE 1: Master Data (Extracts, Chunks, and Saves to Database)
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

# ROUTE 2: Job Description (Extracts and holds whole text)
@app.post("/upload-jd/")
async def upload_jd(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text_by_type(text, doc_type="jd")
    
    return {
        "filename": file.filename,
        "status": "Ready for analysis",
        "jd_text_preview": chunks[0][:300]
    }

# ROUTE 3: Current Resume (Extracts and chunks for skill gaps)
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