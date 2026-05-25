import fitz

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw bytes of a PDF file, parses it using PyMuPDF,
    and returns clean, structurally ordered text.
    """
    # Open the PDF directly from the memory bytes
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    extracted_text = ""
    for page in doc:
        # "text" extracts plain text while respecting layout blocks
        page_text = page.get_text("text")
        if page_text:
            extracted_text += page_text + "\n"
            
    # Clean up excessive white spaces and newlines
    cleaned_text = " ".join(extracted_text.split())
    return cleaned_text