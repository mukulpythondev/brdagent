import os
from dotenv import load_dotenv

load_dotenv()

# App general config
APP_NAME = os.getenv("APP_NAME", "BRD Forge")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() in ("true", "1", "yes")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILES_PER_SESSION = int(os.getenv("MAX_FILES_PER_SESSION", 10))

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

# SMTP Email Configuration for Sharing BRDs
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@brdforge.ai")

# GCP Cloud Storage Configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
GCS_CREDENTIALS_PATH = os.getenv("GCS_CREDENTIALS_PATH", "")

# BigQuery Configuration
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "brd_forge_dataset")
BQ_CREDENTIALS_PATH = os.getenv("BQ_CREDENTIALS_PATH", "")

# Vertex AI Configuration
VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
VERTEX_CREDENTIALS_PATH = os.getenv("VERTEX_CREDENTIALS_PATH", "")
