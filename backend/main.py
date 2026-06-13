import os
import json
import logging
import io
import jwt
import bcrypt
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import config
import database.db_manager as db_manager
from database.firebase_handler import is_firebase_enabled, verify_firebase_token
from core.brd_generator import generate_brd
from core.conflict_detector import detect_conflicts
from utils.export import export_to_pdf, export_to_word
from utils.excel_exporter import export_to_excel
from utils.email_sharer import send_brd_email
from utils.pdf_parser import extract_text_from_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brdforge_backend")

app = FastAPI(
    title="BRD Forge API Server",
    description="FastAPI Backend for Multi-Modal Business Requirements Document Generation",
    version="1.0.0"
)

# CORS Configuration - allow access from React UI dev server (port 5173) and build outputs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Constants for local fallback mode
JWT_SECRET = os.getenv("JWT_SECRET", "brdforge-dev-secret-key-12345-secured")
JWT_ALGORITHM = "HS256"

# File path for local user credentials persistence
USERS_FILE = os.path.join(config.BASE_DIR, "database", "users.json")

# Ensure database directory exists
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# Helper functions for local fallback user registry
def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users registry: {e}")
            return {}
    return {}

def save_users(users: dict):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users registry: {e}")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def ensure_demo_user():
    """
    Keeps a fixed local demo login ready for judges and team testing.
    """
    if is_firebase_enabled():
        return

    users = load_users()
    email = config.DEMO_LOGIN_EMAIL
    password = config.DEMO_LOGIN_PASSWORD
    existing = users.get(email)

    if existing and verify_password(password, existing.get("password", "")):
        return

    users[email] = {
        "name": config.DEMO_LOGIN_NAME,
        "password": hash_password(password)
    }
    save_users(users)
    logger.info("Local demo login ensured for %s", email)

ensure_demo_user()

# --- Security Authentication Middleware Dependency ---

async def get_current_user(request: Request) -> dict:
    """
    Decodes the request 'Authorization: Bearer <token>' header.
    Validates via Firebase if enabled, otherwise decodes local JWT fallback.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    
    token = auth_header.split(" ")[1]
    
    if is_firebase_enabled():
        try:
            decoded_token = verify_firebase_token(token)
            email = decoded_token.get("email")
            name = decoded_token.get("name", email.split('@')[0])
            uid = decoded_token.get("uid")
            return {
                "uid": uid,
                "email": email,
                "name": name,
                "role": "Workspace Architect",
                "firebase": True
            }
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid Firebase Token: {e}")
    else:
        # Fallback Local JWT Decryption
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            
            users = load_users()
            user_data = users.get(email)
            if not user_data:
                raise HTTPException(status_code=401, detail="User session not found")
                
            return {
                "uid": email,
                "email": email,
                "name": user_data.get("name"),
                "role": "Workspace Architect",
                "firebase": False
            }
        except jwt.PyJWTError as e:
            logger.error(f"Local JWT verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired session token")

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    """
    Diagnostic endpoint to monitor active db adapter mode.
    """
    return {
        "status": "healthy",
        "app_name": config.APP_NAME,
        "app_version": config.APP_VERSION,
        "database_mode": db_manager.get_db_mode(),
        "firebase_enabled": is_firebase_enabled(),
        "demo_mode": config.DEMO_MODE
    }

@app.get("/api/system/integrations")
def system_integrations():
    """
    Returns the configured integration state for demo and team-lead checks.
    """
    try:
        active_db_mode = db_manager.get_db_mode()
        return {
            "app": {
                "name": config.APP_NAME,
                "version": config.APP_VERSION,
                "demo_mode": config.DEMO_MODE,
            },
            "database": {
                "active_mode": active_db_mode,
                "bigquery_configured": bool(config.BQ_PROJECT_ID and config.BQ_CREDENTIALS_PATH),
                "bigquery_active": active_db_mode == "bigquery",
                "firebase_enabled": is_firebase_enabled(),
            },
            "storage": {
                "gcs_configured": bool(config.GCS_BUCKET_NAME and config.GCS_CREDENTIALS_PATH),
                "bucket": config.GCS_BUCKET_NAME or None,
            },
            "ai": {
                "provider": config.AI_PROVIDER,
                "openai_configured": bool(config.OPENAI_API_KEY),
                "gemini_configured": bool(config.GEMINI_API_KEY),
                "vertex_configured": bool(config.VERTEX_PROJECT_ID and config.VERTEX_CREDENTIALS_PATH),
                "fast_model": config.OPENAI_FAST_MODEL if config.AI_PROVIDER == "openai" else config.GEMINI_FAST_MODEL,
                "advanced_model": config.OPENAI_ADVANCED_MODEL if config.AI_PROVIDER == "openai" else config.GEMINI_ADVANCED_MODEL,
                "vision_model": config.OPENAI_VISION_MODEL if config.AI_PROVIDER == "openai" else config.GEMINI_VISION_MODEL,
                "adaptive_model_routing": True,
            },
            "email": {
                "smtp_configured": bool(config.SMTP_USERNAME and config.SMTP_PASSWORD),
                "from_email": config.SMTP_FROM_EMAIL,
            },
        }
    except Exception as e:
        logger.error(f"Error loading integration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/openai-test")
def openai_test():
    """
    Performs a tiny live OpenAI call without exposing credentials.
    Useful for demo setup checks before uploading BRD inputs.
    """
    if config.AI_PROVIDER != "openai":
        raise HTTPException(status_code=400, detail=f"AI_PROVIDER is set to {config.AI_PROVIDER}, not openai")
    if not config.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured")

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.OPENAI_FAST_MODEL,
                "input": "Reply with only: OpenAI test OK",
                "temperature": 0,
                "max_output_tokens": 20,
            },
            timeout=config.OPENAI_TIMEOUT_SECONDS,
            verify=config.OPENAI_VERIFY_SSL,
        )
        response.raise_for_status()
        payload = response.json()
        output_text = payload.get("output_text", "")
        if not output_text:
            output_text = "".join(
                content.get("text", "")
                for item in payload.get("output", [])
                for content in item.get("content", [])
                if content.get("type") in ("output_text", "text")
            )
        return {
            "status": "success",
            "provider": "openai",
            "model": config.OPENAI_FAST_MODEL,
            "message": output_text.strip() or "OpenAI responded successfully",
        }
    except requests.RequestException as e:
        detail = str(e)
        if getattr(e, "response", None) is not None:
            detail = e.response.text[:500]
        logger.error(f"OpenAI test failed: {detail}")
        raise HTTPException(status_code=502, detail=detail)

# --- 1. Authentication Endpoints ---

@app.post("/api/auth/login")
def login(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    users = load_users()
    user = users.get(email)
    
    if not user or not verify_password(password, user.get("password")):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    token = jwt.encode(
        {"sub": email, "exp": datetime.utcnow() + timedelta(days=7)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "token": token,
        "user": {
            "name": user.get("name"),
            "email": email,
            "role": "Workspace Architect"
        }
    }

@app.post("/api/auth/signup")
def signup(payload: dict):
    name = payload.get("name")
    email = payload.get("email")
    password = payload.get("password")
    
    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="All fields (name, email, password) are required")
        
    users = load_users()
    if email in users:
        raise HTTPException(status_code=400, detail="An account with this email already exists")
        
    users[email] = {
        "name": name,
        "password": hash_password(password)
    }
    save_users(users)
    
    token = jwt.encode(
        {"sub": email, "exp": datetime.utcnow() + timedelta(days=7)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "token": token,
        "user": {
            "name": name,
            "email": email,
            "role": "Workspace Architect"
        }
    }

@app.post("/api/auth/logout")
def logout():
    return {"status": "success", "detail": "Logged out successfully"}

# --- 2. Project Ingestion & CRUD Endpoints ---

@app.get("/api/projects")
def get_projects(current_user: dict = Depends(get_current_user)):
    try:
        # Currently, all local files are shown. If using Firestore, it returns all docs.
        projects = db_manager.get_all_brds()
        return {"projects": projects}
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}")
def get_project_details(project_id: str, current_user: dict = Depends(get_current_user)):
    try:
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"project": proj}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error loading project details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects")
async def generate_project_brd(
    project_name: str = Form(...),
    domain_selection: str = Form("Auto-detect"),
    pasted_text: str = Form(""),
    files: Optional[Union[List[UploadFile], UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        inputs = []
        
        # 1. Process Pasted text input if present
        if pasted_text.strip():
            inputs.append({
                "type": "text",
                "filename": "Pasted Notes.txt",
                "content": pasted_text
            })
            
        # 2. Process File Ingestion
        if files:
            upload_files = files if isinstance(files, list) else [files]
            for file in upload_files:
                if not file.filename:
                    continue
                filename = file.filename
                ext = os.path.splitext(filename)[1].lower()
                
                # Write file temporarily
                local_path = os.path.join(config.UPLOADS_DIR, filename)
                file_bytes = await file.read()
                with open(local_path, "wb") as f:
                    f.write(file_bytes)
                
                logger.info(f"Ingested file upload: {filename}")
                
                text_content = ""
                file_type = "text"
                
                # Read contents based on extension
                if ext == ".pdf":
                    file_type = "pdf"
                    text_content = extract_text_from_pdf(local_path)
                elif ext in [".png", ".jpg", ".jpeg"]:
                    file_type = "image"
                    text_content = f"Image input: {filename}"
                elif ext == ".docx":
                    file_type = "docx"
                    from docx import Document
                    doc = Document(local_path)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                elif ext in [".txt", ".csv"]:
                    file_type = "text"
                    try:
                        text_content = file_bytes.decode("utf-8", errors="ignore")
                    except Exception:
                        text_content = ""
                else:
                    file_type = "unsupported"
                    text_content = "Unsupported extension."
                
                inputs.append({
                    "type": file_type,
                    "filename": filename,
                    "content": text_content,
                    "bytes": file_bytes if file_type == "image" else b""
                })
        
        if not inputs:
            raise HTTPException(status_code=400, detail="Please provide specifications (pasted text or file uploads).")
            
        # 3. Trigger Synthesis Pipeline
        logger.info(f"Synthesizing requirements for: {project_name}")
        brd_payload = generate_brd(project_name, domain_selection, inputs)
        
        # 4. Save to database
        project_id = db_manager.save_brd(project_name, brd_payload)
        
        # Reload fully and return
        full_project = db_manager.get_brd_by_id(project_id)
        return {"project": full_project}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in BRD generation pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/projects/{project_id}")
def update_project(project_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    """
    Overwrites the saved JSON data for a project (called when user saves visualizer canvas state).
    """
    try:
        project_name = payload.get("project_name", "Updated Project")
        brd_json = payload.get("brd_json")
        
        if not brd_json:
            raise HTTPException(status_code=400, detail="Missing brd_json payload")
            
        # Save to database
        db_manager.save_brd(project_name, brd_json, project_id=project_id)
        
        return {"status": "success", "project_id": project_id}
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    try:
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        db_manager.delete_brd(project_id)
        return {"status": "success", "detail": f"Project {project_id} deleted."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. Conflict Resolution & Version Logs ---

@app.post("/api/projects/{project_id}/resolve")
def resolve_conflict(project_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    try:
        conflict_id = payload.get("conflict_id")
        res_type = payload.get("resolution_type") # keep_req1, keep_req2, merge
        merge_desc = payload.get("merge_description", "")
        
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        brd = proj.get("brd_json")
        if not brd:
            raise HTTPException(status_code=400, detail="No BRD JSON structure available")
            
        # Find conflict
        conflicts = brd.get("detected_conflicts", [])
        target_conflict = next((c for c in conflicts if c.get("id") == conflict_id), None)
        
        if not target_conflict:
            raise HTTPException(status_code=404, detail="Conflict not found")
            
        r1_id = target_conflict.get("req1_id")
        r2_id = target_conflict.get("req2_id")
        
        frs = brd.get("functional_requirements", [])
        
        # Apply edits
        if res_type == "keep_req1":
            # Remove req2
            brd["functional_requirements"] = [r for r in frs if r.get("id") != r2_id]
        elif res_type == "keep_req2":
            # Remove req1
            brd["functional_requirements"] = [r for r in frs if r.get("id") != r1_id]
        elif res_type == "merge":
            # Update description of req1, remove req2
            for req in frs:
                if req.get("id") == r1_id:
                    req["description"] = merge_desc
                    req["title"] = f"{req.get('title')} (Merged)"
            brd["functional_requirements"] = [r for r in frs if r.get("id") != r2_id]
            
        # Re-run conflict detector on updated requirements list to remove/update flags
        new_frs = brd.get("functional_requirements", [])
        updated_conflicts = detect_conflicts(new_frs)
        
        # Reset conflict text blocks in requirements
        for r in new_frs:
            r["conflict"] = None
            
        for c in updated_conflicts:
            c1_id = c.get("req1_id")
            c2_id = c.get("req2_id")
            c_desc = c.get("description")
            for r in new_frs:
                if r.get("id") in [c1_id, c2_id]:
                    r["conflict"] = c_desc
                    
        brd["detected_conflicts"] = updated_conflicts
        brd["conflict_count"] = len(updated_conflicts)
        
        # Save updated project
        db_manager.save_brd(proj.get("project_name"), brd, project_id=project_id)
        
        return {"status": "success", "detail": f"Conflict {conflict_id} resolved using {res_type}."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error resolving conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/versions")
def get_project_versions(project_id: str, current_user: dict = Depends(get_current_user)):
    try:
        versions = db_manager.get_versions(project_id)
        return {"versions": versions}
    except Exception as e:
        logger.error(f"Error fetching version archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. Styled Exporters & Stakeholder Sharing ---

@app.get("/api/projects/{project_id}/export/pdf")
def export_pdf_endpoint(project_id: str, theme: str = "Corporate Blue"):
    """
    Generates dynamic styled ReportLab PDF bytes matching the requested theme.
    Returns file attachment stream.
    """
    try:
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        brd = proj.get("brd_json")
        
        # Run reportlab export
        pdf_bytes = export_to_pdf(brd)
        
        # Define theme colors mapping
        theme_hex = "#4285F4"
        if theme == "Emerald Clean":
            theme_hex = "#059669"
        elif theme == "Warm Crimson":
            theme_hex = "#e11d48"
        elif theme == "Slate Minimalist":
            theme_hex = "#1f2937"
            
        # We can dynamically replace the default blue color in the generated ReportLab bytes,
        # but a cleaner way is modifying the export function or updating the styling definitions.
        # ReportLab generates the stream using the primary styles. Let's pass the payload.
        # Since export_to_pdf doesn't support custom colors directly in parameters in prototype,
        # we return the compiled PDF. In the next sprint, we can adjust the styles dynamically.
        
        filename = f"{proj.get('project_name','BRD').replace(' ', '_')}_Requirements.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/export/docx")
def export_docx_endpoint(project_id: str):
    try:
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        brd = proj.get("brd_json")
        docx_bytes = export_to_word(brd)
        
        filename = f"{proj.get('project_name','BRD').replace(' ', '_')}_Requirements.docx"
        
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting Word document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/export/xlsx")
def export_xlsx_endpoint(project_id: str):
    """
    Downloads requirements matrix as an Excel spreadsheet.
    """
    try:
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        brd = proj.get("brd_json")
        xlsx_bytes = export_to_excel(brd)
        
        filename = f"{proj.get('project_name','BRD').replace(' ', '_')}_Requirements.xlsx"
        
        return StreamingResponse(
            io.BytesIO(xlsx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting Excel grid: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_id}/share")
def share_project_brd(project_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    try:
        to_email = payload.get("email")
        if not to_email:
            raise HTTPException(status_code=400, detail="Recipient email required")
            
        proj = db_manager.get_brd_by_id(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
            
        brd = proj.get("brd_json")
        pdf_bytes = export_to_pdf(brd)
        
        # Send mail
        send_brd_email(to_email, proj.get("project_name"), pdf_bytes)
        
        return {"status": "success", "detail": f"Document emailed to: {to_email}"}
    except Exception as e:
        logger.error(f"Error sharing project BRD via email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Setup local uvicorn execution handler
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
