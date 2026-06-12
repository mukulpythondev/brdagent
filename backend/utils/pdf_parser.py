import PyPDF2
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content page-by-page from a PDF file.
    """
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n" + page_text
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {e}")
        return f"Error extracting text from PDF: {str(e)}"
        
    return text.strip()
