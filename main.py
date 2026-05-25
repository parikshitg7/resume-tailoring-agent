from fastapi import FastAPI ,UploadFile, File
from pydantic import BaseModel
from utils import extract_text_from_pdf

# Initialize the app
app = FastAPI(title="Autonomous ATS-Buster API")

# Define our expected data structure
class JobDescriptionUpload(BaseModel):
    company_name: str
    job_role: str
    jd_text: str

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "Agent is online and ready."}

# Mock endpoint for testing
@app.post("/analyze-jd/")
def analyze_jd(payload: JobDescriptionUpload):
    return {
        "message": f"Received JD for {payload.job_role} at {payload.company_name}",
        "received_text_length": len(payload.jd_text)
    }

# NEW: Endpoint to handle PDF uploads
@app.post("/upload-pdf/")
async def upload_pdf_file(file: UploadFile = File(...)):
    # Read the incoming file as raw bytes
    file_bytes = await file.read()
    
    # Extract text using PyMuPDF
    extracted_text = extract_text_from_pdf(file_bytes)
    
    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "preview": extracted_text[:400]  # Return the first 400 characters to verify it worked
    }
