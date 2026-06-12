import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try to import firebase_admin. If it fails, firebase won't be enabled.
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    FIREBASE_INSTALLED = True
except ImportError:
    FIREBASE_INSTALLED = False

firebase_app = None
db_client = None
firebase_enabled = False

# Initialize Firebase if installed and credential key is present
if FIREBASE_INSTALLED:
    # Look for firebase-key.json in the backend root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = os.path.join(base_dir, "firebase-key.json")
    
    if os.path.exists(key_path):
        try:
            cred = credentials.Certificate(key_path)
            # Initialize default app if not already initialized
            if not firebase_admin._apps:
                firebase_app = firebase_admin.initialize_app(cred)
            else:
                firebase_app = firebase_admin.get_app()
            db_client = firestore.client()
            firebase_enabled = True
            logger.info("Firebase Admin initialized successfully using firebase-key.json")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase with service account key: {e}")
    else:
        logger.info("firebase-key.json not found in backend root. Firebase features disabled (local fallback mode).")
else:
    logger.info("firebase-admin package not installed. Firebase features disabled (local fallback mode).")


def is_firebase_enabled() -> bool:
    return firebase_enabled


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token. Returns the decoded token dictionary.
    Raises exception if verification fails.
    """
    if not firebase_enabled:
        raise ValueError("Firebase is not initialized or configured.")
    return auth.verify_id_token(id_token)


# --- Firestore Data Sync Operations ---

def save_brd_firestore(project_name: str, brd_payload: Dict[str, Any], project_id: str = None) -> str:
    """
    Saves a BRD payload to Google Cloud Firestore database.
    Increments versions list and updates project document.
    """
    if not firebase_enabled:
        raise ValueError("Firestore is not enabled.")
        
    db = db_client
    
    # Calculate stats
    fr_list = brd_payload.get("functional_requirements", [])
    nfr_list = brd_payload.get("non_functional_requirements", [])
    total_reqs = len(fr_list) + len(nfr_list)
    
    # Calculate stats
    high_conf = 0
    conflict_count = 0
    for req in fr_list + nfr_list:
        if req.get("confidence") == "HIGH":
            high_conf += 1
        if req.get("conflict"):
            conflict_count += 1
            
    coverage_score = (high_conf / max(total_reqs, 1)) * 100
    now = datetime.utcnow().isoformat() + "Z"
    
    if not project_id:
        project_id = str(uuid.uuid4())
        version = 1
        summary = "Initial generation"
    else:
        # Get current version number
        proj_ref = db.collection("brd_projects").document(project_id)
        proj_doc = proj_ref.get()
        if proj_doc.exists:
            # Check versions count
            versions = db.collection("brd_projects").document(project_id).collection("versions").get()
            version = len(versions) + 1
        else:
            version = 1
        summary = f"Updated to version {version}"

    # Prepare project metadata
    project_doc_data = {
        "id": project_id,
        "project_name": project_name,
        "domain": brd_payload.get("domain", "General"),
        "created_at": now,
        "confidence_score": coverage_score,
        "total_requirements": total_reqs,
        "conflict_count": conflict_count,
        "brd_json": brd_payload
    }
    
    # Save base project document
    db.collection("brd_projects").document(project_id).set(project_doc_data)
    
    # Save to versions subcollection
    version_id = str(uuid.uuid4())
    db.collection("brd_projects").document(project_id).collection("versions").document(version_id).set({
        "id": version_id,
        "project_id": project_id,
        "version": version,
        "changed_at": now,
        "brd_json": brd_payload,
        "change_summary": summary
    })
    
    return project_id


def get_all_brds_firestore() -> List[Dict[str, Any]]:
    """
    Returns list of all saved BRD metadata.
    """
    if not firebase_enabled:
        raise ValueError("Firestore is not enabled.")
        
    db = db_client
    projects_ref = db.collection("brd_projects")
    docs = projects_ref.stream()
    
    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append({
            "id": d.get("id"),
            "project_name": d.get("project_name"),
            "domain": d.get("domain"),
            "created_at": d.get("created_at"),
            "confidence_score": d.get("confidence_score"),
            "total_requirements": d.get("total_requirements"),
            "conflict_count": d.get("conflict_count")
        })
        
    # Sort by creation time descending
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results


def get_brd_by_id_firestore(project_id: str) -> Dict[str, Any]:
    """
    Gets complete project record.
    """
    if not firebase_enabled:
        raise ValueError("Firestore is not enabled.")
        
    db = db_client
    doc_ref = db.collection("brd_projects").document(project_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return None


def delete_brd_firestore(project_id: str):
    """
    Deletes project and its version subcollections.
    """
    if not firebase_enabled:
        raise ValueError("Firestore is not enabled.")
        
    db = db_client
    
    # Delete all versions first
    versions_ref = db.collection("brd_projects").document(project_id).collection("versions")
    versions = versions_ref.stream()
    for v in versions:
        v.reference.delete()
        
    # Delete main document
    db.collection("brd_projects").document(project_id).delete()


def get_versions_firestore(project_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all change versions of a project.
    """
    if not firebase_enabled:
        raise ValueError("Firestore is not enabled.")
        
    db = db_client
    versions_ref = db.collection("brd_projects").document(project_id).collection("versions")
    docs = versions_ref.stream()
    
    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append({
            "version": d.get("version"),
            "changed_at": d.get("changed_at"),
            "change_summary": d.get("change_summary"),
            "brd_json": d.get("brd_json")
        })
        
    results.sort(key=lambda x: x.get("version", 0), reverse=True)
    return results
