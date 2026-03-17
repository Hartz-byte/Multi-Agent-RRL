import fitz  # PyMuPDF
import requests
import io

def parse_pdf_from_url(url: str):
    """
    Download and extract text from a PDF URL
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        text = ""
        # Limit to first 10 pages to avoid context window issues
        for page_num in range(min(len(doc), 10)):
            text += doc[page_num].get_text()
            
        return text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Basic text chunking for better embedding quality
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
