import os
import sqlite3
import json
import uuid
from datetime import datetime
from config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "brd_forge.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create brd_projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brd_projects (
      id TEXT PRIMARY KEY,
      project_name TEXT,
      domain TEXT,
      created_at TIMESTAMP,
      brd_json TEXT,
      confidence_score REAL,
      total_requirements INTEGER,
      conflict_count INTEGER
    );
    """)
    
    # Create brd_versions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brd_versions (
      id TEXT PRIMARY KEY,
      project_id TEXT,
      version INTEGER,
      changed_at TIMESTAMP,
      brd_json TEXT,
      change_summary TEXT
    );
    """)
    
    conn.commit()
    conn.close()

def save_brd(project_name, brd_json_str, project_id=None) -> str:
    """
    Saves a BRD to the SQLite database. If project_id is provided,
    it updates the project and creates a new version in brd_versions.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Parse json to extract scores and fields
    try:
        data = json.loads(brd_json_str) if isinstance(brd_json_str, str) else brd_json_str
        brd_json_str = json.dumps(data)
    except Exception:
        data = {}
        
    domain = data.get("domain", "General")
    
    # Calculate stats
    fr_list = data.get("functional_requirements", [])
    nfr_list = data.get("non_functional_requirements", [])
    total_reqs = len(fr_list) + len(nfr_list)
    
    # Calculate confidence score
    high_conf = 0
    conflict_count = 0
    for req in fr_list + nfr_list:
        if req.get("confidence") == "HIGH":
            high_conf += 1
        if req.get("conflict"):
            conflict_count += 1
            
    coverage_score = (high_conf / max(total_reqs, 1)) * 100
    
    now = datetime.now().isoformat()
    
    if not project_id:
        # Create new project
        project_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO brd_projects (id, project_name, domain, created_at, brd_json, confidence_score, total_requirements, conflict_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project_id, project_name, domain, now, brd_json_str, coverage_score, total_reqs, conflict_count)
        )
        
        # Save version 1
        version_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO brd_versions (id, project_id, version, changed_at, brd_json, change_summary) VALUES (?, ?, ?, ?, ?, ?)",
            (version_id, project_id, 1, now, brd_json_str, "Initial generation")
        )
    else:
        # Update existing project
        cursor.execute(
            "UPDATE brd_projects SET project_name = ?, domain = ?, brd_json = ?, confidence_score = ?, total_requirements = ?, conflict_count = ? WHERE id = ?",
            (project_name, domain, brd_json_str, coverage_score, total_reqs, conflict_count, project_id)
        )
        
        # Get next version number
        cursor.execute("SELECT MAX(version) as max_v FROM brd_versions WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        next_v = (row["max_v"] or 0) + 1
        
        # Save new version
        version_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO brd_versions (id, project_id, version, changed_at, brd_json, change_summary) VALUES (?, ?, ?, ?, ?, ?)",
            (version_id, project_id, next_v, now, brd_json_str, f"Updated to version {next_v}")
        )
        
    conn.commit()
    conn.close()
    return project_id

def get_all_brds() -> list:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, domain, created_at, confidence_score, total_requirements, conflict_count FROM brd_projects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def get_brd_by_id(project_id) -> dict:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brd_projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    result = dict(row) if row else None
    conn.close()
    return result

def save_version(project_id, brd_json_str, summary) -> str:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(version) as max_v FROM brd_versions WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    next_v = (row["max_v"] or 0) + 1
    
    version_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO brd_versions (id, project_id, version, changed_at, brd_json, change_summary) VALUES (?, ?, ?, ?, ?, ?)",
        (version_id, project_id, next_v, now, brd_json_str, summary)
    )
    conn.commit()
    conn.close()
    return version_id

def get_versions(project_id) -> list:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version, changed_at, change_summary, brd_json FROM brd_versions WHERE project_id = ? ORDER BY version DESC", (project_id,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def delete_brd(project_id):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM brd_projects WHERE id = ?", (project_id,))
    cursor.execute("DELETE FROM brd_versions WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
