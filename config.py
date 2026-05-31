import os
from dotenv import load_dotenv

load_dotenv()

# App general config
APP_NAME = os.getenv("APP_NAME", "BRD Forge")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() in ("true", "1", "yes")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILES_PER_SESSION = int(os.getenv("MAX_FILES_PER_session", 10))

# Gemini Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SAMPLE_INPUTS_DIR = os.path.join(BASE_DIR, "sample_inputs")

for path in [UPLOADS_DIR, OUTPUTS_DIR, SAMPLE_INPUTS_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)

# UI Theme styling color palette
THEME = {
  "primary": "#4285F4",      # Google Blue
  "secondary": "#34A853",    # Google Green  
  "warning": "#FBBC04",      # Google Yellow
  "danger": "#EA4335",       # Google Red
  "background": "#1E1E2E",   # Dark background
  "surface": "#2A2A3E",      # Card background
  "text": "#FFFFFF"
}
