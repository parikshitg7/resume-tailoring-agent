import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    extracted_text = ""
    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            extracted_text += page_text + "\n"
    return " ".join(extracted_text.split())

def chunk_text_by_type(text: str, doc_type: str) -> list[str]:
    """
    Splits text dynamically based on the document type.
    """
    if doc_type == "master":
        # Small chunks for precise skill matching (e.g., finding Java projects)
        size = 600
        overlap = 100
    elif doc_type == "resume":
        # Larger chunks to keep whole roles together
        size = 1200
        overlap = 200
    elif doc_type == "jd":
        # Job Descriptions are kept whole, no chunking
        return [text]
    else:
        size = 1000
        overlap = 200

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return text_splitter.split_text(text)