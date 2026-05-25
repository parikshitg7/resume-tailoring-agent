from fastapi import FastAPI
from pydantic import BaseModel

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