import os
import shutil
import logging
import config
from utils.pdf_parser import extract_text_from_pdf
from utils.image_analyzer import load_image_bytes, get_image_info

logger = logging.getLogger(__name__)

def process_file_upload(uploaded_file) -> dict:
    """
    Saves an uploaded file locally and extracts its contents/metadata.
    Returns a dict with metadata and extracted representation.
    """
    filename = uploaded_file.name
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Generate local path
    local_path = os.path.join(config.UPLOADS_DIR, filename)
    
    # Save file to uploads folder
    with open(local_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
    logger.info(f"Saved uploaded file {filename} ({file_size_mb:.2f} MB)")
    
    result = {
        "filename": filename,
        "extension": file_ext,
        "size_mb": round(file_size_mb, 2),
        "local_path": local_path,
        "type": "text", # default
        "content": "",
        "bytes": b""
    }
    
    # Ingestion route based on file extension
    try:
        if file_ext == ".pdf":
            result["type"] = "pdf"
            result["content"] = extract_text_from_pdf(local_path)
        elif file_ext in [".png", ".jpg", ".jpeg"]:
            result["type"] = "image"
            result["bytes"] = load_image_bytes(local_path)
            # Fetch metadata
            img_info = get_image_info(local_path)
            result["content"] = f"Image metadata: {img_info}"
        elif file_ext in [".txt", ".csv"]:
            result["type"] = "text"
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                result["content"] = f.read()
        elif file_ext == ".docx":
            result["type"] = "docx"
            from docx import Document
            doc = Document(local_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            result["content"] = text
        else:
            result["type"] = "unsupported"
            result["content"] = f"Unsupported file format: {file_ext}"
    except Exception as e:
        logger.error(f"Error ingesting file {filename}: {e}")
        result["content"] = f"Failed to parse content: {str(e)}"
        
    return result

def clear_uploads():
    """
    Wipes the uploads folder to keep disk clean.
    """
    if os.path.exists(config.UPLOADS_DIR):
        for filename in os.listdir(config.UPLOADS_DIR):
            file_path = os.path.join(config.UPLOADS_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")
