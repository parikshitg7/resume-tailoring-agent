import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file stream using the high-speed PyMuPDF engine.
    Used for reading the Job Description, Master PDF, and Current Resume.
    """
    text = ""
    try:
        # Open the PDF directly from the byte stream in memory
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Iterate through all pages and extract block text
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # 'text' extraction preserves basic reading order better than raw coordinates
            text += page.get_text("text") + "\n"
            
        pdf_document.close()
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text via PyMuPDF: {e}")
        return ""