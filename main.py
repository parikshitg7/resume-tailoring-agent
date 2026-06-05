from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
import tempfile
import os

from utils import extract_text_from_pdf, chunk_text_by_type
from rag import store_chunks_in_db
from resume_parser import parse_resume_structure
from graph import ats_agent 

app = FastAPI(title="Autonomous ATS-Buster API")

@app.get("/")
def read_root():
    return {"status": "Agent is online and ready."}

# --- 1. The Memory Upload (Unchanged) ---
@app.post("/upload-master/")
async def upload_master(file: UploadFile = File(...)):
    """Upload your master PDF once to save it to your local ChromaDB vector database."""
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text_by_type(text, doc_type="master")
    chunks_saved = store_chunks_in_db(chunks, file.filename)
    return {
        "filename": file.filename,
        "chunks_saved_to_db": chunks_saved,
        "message": "Master Data memorized successfully."
    }

# --- 2. The New XML Injection Generation Route ---
@app.post("/generate-resume/")
async def generate_resume(
    jd_file: UploadFile = File(..., description="Upload the Job Description PDF"),
    base_resume: UploadFile = File(..., description="Upload your formatted base .docx resume")
):
    """
    Upload a JD and your Base Resume. The agent will read the JD, query your Master Memory,
    draft elite bullet points, and surgically inject them into your Base Resume format.
    """
    # 1. Extract the text from the JD
    jd_bytes = await jd_file.read()
    jd_text = extract_text_from_pdf(jd_bytes)
    
    # 2. Save the uploaded .docx to a temporary file so python-docx can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        temp_docx.write(await base_resume.read())
        temp_docx_path = temp_docx.name
        
    try:
        # 3. Use the "Eyes": Parse the visual structure of your uploaded Word doc
        resume_structure = parse_resume_structure(temp_docx_path)
        
        # 4. Use the "Brain & Hands": Trigger the LangGraph State Machine
        initial_state = {
            "jd_text": jd_text,
            "resume_structure": resume_structure
        }
        final_state = ats_agent.invoke(initial_state)
        
        # 5. Extract the final binary Word file from the state
        final_docx_bytes = final_state["output_docx_bytes"]
        
        # 6. Stream the perfectly formatted file directly to your browser
        return Response(
            content=final_docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": 'attachment; filename="Tailored_ATS_Resume.docx"'}
        )
        
    finally:
        # 7. Clean up the temporary file from your local hard drive
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)