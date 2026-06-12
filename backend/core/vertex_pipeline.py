"""
Vertex AI Pipeline Adapter for BRD Forge.

If Vertex AI credentials are configured (VERTEX_PROJECT_ID + credentials),
wraps the core Gemini agent calls into a Vertex AI managed pipeline.
If not configured, falls back to the standard google-generativeai SDK.
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try importing Vertex AI SDK
try:
    from google.cloud import aiplatform
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    VERTEX_INSTALLED = True
except ImportError:
    VERTEX_INSTALLED = False
    logger.info("google-cloud-aiplatform not installed. Vertex AI features disabled.")

vertex_enabled = False
vertex_model = None


def init_vertex():
    """
    Initialize Vertex AI if credentials and project ID are present.
    """
    global vertex_enabled, vertex_model

    if not VERTEX_INSTALLED:
        logger.info("Vertex AI SDK not installed. Using standard Gemini SDK.")
        return

    project_id = os.getenv("VERTEX_PROJECT_ID", "")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    credentials_path = os.getenv("VERTEX_CREDENTIALS_PATH", "")

    if not project_id:
        logger.info("VERTEX_PROJECT_ID not set. Using standard Gemini SDK.")
        return

    try:
        if credentials_path and os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        vertexai.init(project=project_id, location=location)
        vertex_model = GenerativeModel("gemini-1.5-pro-002")
        vertex_enabled = True
        logger.info(f"Vertex AI initialized. Project: {project_id}, Location: {location}")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        vertex_enabled = False


def is_vertex_enabled() -> bool:
    return vertex_enabled


def analyze_with_vertex(prompt: str, image_bytes: bytes = None) -> str:
    """
    Send a prompt (and optional image) to Vertex AI Gemini model.
    Returns the generated text response.

    Falls back to standard Gemini SDK if Vertex is not enabled.
    """
    if not vertex_enabled or not vertex_model:
        raise ValueError("Vertex AI is not enabled. Use standard Gemini agent instead.")

    try:
        parts = [Part.from_text(prompt)]

        if image_bytes:
            parts.append(Part.from_data(image_bytes, mime_type="image/png"))

        response = vertex_model.generate_content(parts)
        return response.text
    except Exception as e:
        logger.error(f"Vertex AI generation failed: {e}")
        raise


def analyze_requirements_vertex(project_name: str, domain: str, raw_text: str) -> Dict[str, Any]:
    """
    Runs the full BRD requirements extraction pipeline through Vertex AI.
    Returns the parsed JSON structure of functional and non-functional requirements.
    """
    prompt = f"""You are a senior Business Analyst AI assistant called "BRD Forge".
Analyze the following project specifications and generate a structured Business Requirements Document.

**Project Name**: {project_name}
**Domain**: {domain}

**Input Specifications**:
{raw_text}

**Output Format** (respond in valid JSON only):
{{
  "project_name": "{project_name}",
  "domain": "{domain}",
  "executive_summary": "<2-3 sentence overview>",
  "functional_requirements": [
    {{
      "id": "FR-001",
      "title": "<requirement title>",
      "description": "<detailed description>",
      "priority": "MUST HAVE | SHOULD HAVE | NICE TO HAVE",
      "confidence": "HIGH | MEDIUM | LOW",
      "source": "<source document name>",
      "conflict": null
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR-001",
      "title": "<requirement title>",
      "description": "<detailed description>",
      "confidence": "HIGH | MEDIUM | LOW",
      "source": "<source document name>"
    }}
  ],
  "detected_conflicts": [],
  "conflict_count": 0,
  "compliance_suggestions": ["<relevant industry standards>"],
  "traceability_matrix": []
}}

Generate comprehensive, professional-grade requirements from the provided specifications.
"""

    try:
        response_text = analyze_with_vertex(prompt)
        # Try to parse JSON from response
        import json

        # Clean response - strip markdown code fences if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Vertex AI response as JSON: {e}")
        return {
            "project_name": project_name,
            "domain": domain,
            "executive_summary": "AI analysis completed but response parsing failed.",
            "functional_requirements": [],
            "non_functional_requirements": [],
            "detected_conflicts": [],
            "conflict_count": 0,
            "raw_ai_response": response_text
        }
    except Exception as e:
        logger.error(f"Vertex AI requirements analysis failed: {e}")
        raise


# Auto-initialize on module import
init_vertex()
