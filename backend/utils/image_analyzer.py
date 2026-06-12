import os
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

def load_image_bytes(file_path: str) -> bytes:
    """
    Read image file and return its bytes.
    """
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading image bytes from {file_path}: {e}")
        return b""

def get_image_info(file_path: str) -> dict:
    """
    Get image dimension and format details.
    """
    try:
        with Image.open(file_path) as img:
            return {
                "filename": os.path.basename(file_path),
                "format": img.format,
                "width": img.width,
                "height": img.height,
                "mode": img.mode
            }
    except Exception as e:
        logger.error(f"Error opening image {file_path}: {e}")
        return {"filename": os.path.basename(file_path), "error": str(e)}
