import os
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from utils import extract_text_from_pdf, chunk_master_text
from rag import store_and_retrieve_master_data
from graph import build_resume_graph
from document_generator import generate_resume_docx

app = FastAPI(title="Autonomous ATS-Buster API")

def cleanup_file(file_path: str):
    """Deletes the temporary file after it has been sent to the user."""
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"--- CLEANUP: Removed temporary file {file_path} ---")

@app.post("/generate-resume/")
async def generate_resume(
    background_tasks: BackgroundTasks,
    current_resume: UploadFile = File(..., description="Upload your current base resume (PDF)"),
    jd_file: UploadFile = File(..., description="Upload the Target Job Description (PDF)"),
    master_file: Optional[UploadFile] = File(None, description="Upload your Master Resume/Data (PDF)"),
    master_text: Optional[str] = Form(None, description="Or paste your master data text here")
):
    try:
        print("--- API ENDPOINT HIT: /generate-resume/ ---")
        
        # 1. Extract Text from Uploaded PDFs
        current_resume_bytes = await current_resume.read()
        jd_bytes = await jd_file.read()
        
        raw_current_resume_text = extract_text_from_pdf(current_resume_bytes)
        raw_jd_text = extract_text_from_pdf(jd_bytes)
        
        # 2. Handle Master Data (Either File or Text)
        raw_master_text = ""
        if master_file:
            master_bytes = await master_file.read()
            raw_master_text = extract_text_from_pdf(master_bytes)
        elif master_text:
            raw_master_text = master_text
            
        if not raw_master_text:
            raise HTTPException(
                status_code=400, 
                detail="You must provide either a master_file or master_text."
            )
            
        # 3. SMART RAG ROUTER: Check if the master data needs chunking
        word_count = len(raw_master_text.split())
        final_master_context = ""
        
        if word_count > 1500: # Roughly 2-3 pages
            print(f"--- ROUTER: Master data is {word_count} words. Initiating RAG Pipeline. ---")
            master_chunks = chunk_master_text(raw_master_text)
            final_master_context = store_and_retrieve_master_data(master_chunks, jd_query=raw_jd_text)
        else:
            print(f"--- ROUTER: Master data is {word_count} words. Bypassing RAG for direct injection. ---")
            final_master_context = raw_master_text
            
        # 4. Trigger the Brain (LangGraph)
        workflow = build_resume_graph()
        initial_state = {
            "raw_current_resume_text": raw_current_resume_text,
            "raw_jd_text": raw_jd_text,
            "raw_master_text": final_master_context, # Inject the smartly routed context here
            "structured_resume_data": {}
        }
        
        final_state = workflow.invoke(initial_state)
        resume_data = final_state.get("structured_resume_data", {})
        
        if not resume_data or "personal_info" not in resume_data:
            raise ValueError("LangGraph failed to generate valid structured data.")
        
        # 5. Trigger the Hands (Document Generator)
        output_file_path = generate_resume_docx(resume_data)
        
        # 6. Send the file to the user and queue the cleanup task
        background_tasks.add_task(cleanup_file, output_file_path)
        
        return FileResponse(
            path=output_file_path,
            filename="Tailored_ATS_Resume.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        print(f"ERROR in /generate-resume/: {e}")
        raise HTTPException(status_code=500, detail=str(e))