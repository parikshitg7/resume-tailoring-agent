import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file stream using the high-speed PyMuPDF engine.
    Used for reading the Job Description and Current/Master Resumes.
    """
    text = ""
    try:
        # Open the PDF directly from the byte stream in memory
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Iterate through all pages and extract block text
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text") + "\n"
            
        pdf_document.close()
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text via PyMuPDF: {e}")
        return ""

def chunk_master_text(text: str) -> list[str]:
    """
    Splits the Master Data into overlapping chunks optimized for semantic search.
    Chunk size 800 ensures entire project blocks stay together.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)