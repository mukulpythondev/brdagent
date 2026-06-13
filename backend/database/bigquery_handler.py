"""
BigQuery Database Adapter for BRD Forge.

If BigQuery credentials are configured (BQ_PROJECT_ID + credentials),
project data can be stored/retrieved from BigQuery tables.
Falls back to SQLite/Firestore via existing db_manager if not configured.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

# Try importing BigQuery SDK
try:
    from google.cloud import bigquery
    BQ_INSTALLED = True
except ImportError:
    BQ_INSTALLED = False
    logger.info("google-cloud-bigquery not installed. BigQuery features disabled.")

bq_client = None
bq_enabled = False
bq_dataset = None


def init_bigquery():
    """
    Initialize BigQuery client if credentials are present.
    Creates dataset and tables if they don't exist.
    """
    global bq_client, bq_enabled, bq_dataset

    if not BQ_INSTALLED:
        logger.info("BigQuery SDK not installed. Using SQLite/Firestore fallback.")
        return

    project_id = os.getenv("BQ_PROJECT_ID", "")
    dataset_id = os.getenv("BQ_DATASET_ID", "brd_forge_dataset")
    credentials_path = os.getenv("BQ_CREDENTIALS_PATH", "")

    if not project_id:
        logger.info("BQ_PROJECT_ID not set. Using SQLite/Firestore fallback.")
        return

    try:
        if credentials_path and os.path.exists(credentials_path):
            bq_client = bigquery.Client.from_service_account_json(credentials_path)
        else:
            bq_client = bigquery.Client(project=project_id)

        bq_dataset = f"{project_id}.{dataset_id}"

        # Create dataset if not exists
        dataset_ref = bigquery.Dataset(bq_dataset)
        dataset_ref.location = "US"
        try:
            bq_client.get_dataset(bq_dataset)
        except Exception:
            bq_client.create_dataset(dataset_ref, exists_ok=True)

        # Create tables if not exist
        _ensure_tables_exist()

        bq_enabled = True
        logger.info(f"BigQuery initialized. Dataset: {bq_dataset}")
    except Exception as e:
        logger.error(f"Failed to initialize BigQuery: {e}")
        bq_enabled = False


def _ensure_tables_exist():
    """Create BRD projects and versions tables if they don't exist."""
    # Projects table
    projects_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_name", "STRING"),
        bigquery.SchemaField("domain", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("confidence_score", "FLOAT64"),
        bigquery.SchemaField("total_requirements", "INT64"),
        bigquery.SchemaField("conflict_count", "INT64"),
        bigquery.SchemaField("brd_json", "STRING"),  # Stored as JSON string
    ]

    projects_table = bigquery.Table(f"{bq_dataset}.brd_projects", schema=projects_schema)
    try:
        bq_client.get_table(projects_table)
    except Exception:
        bq_client.create_table(projects_table, exists_ok=True)

    # Versions table
    versions_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_id", "STRING"),
        bigquery.SchemaField("version", "INT64"),
        bigquery.SchemaField("changed_at", "TIMESTAMP"),
        bigquery.SchemaField("change_summary", "STRING"),
        bigquery.SchemaField("brd_json", "STRING"),
    ]

    versions_table = bigquery.Table(f"{bq_dataset}.brd_versions", schema=versions_schema)
    try:
        bq_client.get_table(versions_table)
    except Exception:
        bq_client.create_table(versions_table, exists_ok=True)


def is_bigquery_enabled() -> bool:
    return bq_enabled


def save_brd_bigquery(project_name: str, brd_payload: Dict[str, Any],
                       project_id: str = None) -> str:
    """Save a BRD document to BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    fr_list = brd_payload.get("functional_requirements", [])
    nfr_list = brd_payload.get("non_functional_requirements", [])
    total_reqs = len(fr_list) + len(nfr_list)

    high_conf = sum(1 for r in fr_list + nfr_list if r.get("confidence") == "HIGH")
    conflict_count = sum(1 for r in fr_list + nfr_list if r.get("conflict"))
    coverage_score = (high_conf / max(total_reqs, 1)) * 100
    now = datetime.utcnow().isoformat()

    if not project_id:
        project_id = str(uuid.uuid4())
        version = 1
        summary = "Initial generation"
    else:
        # Get current version count
        query = f"""
            SELECT COUNT(*) as cnt FROM `{bq_dataset}.brd_versions`
            WHERE project_id = @project_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
            ]
        )
        result = bq_client.query(query, job_config=job_config).result()
        row = list(result)[0]
        version = row.cnt + 1
        summary = f"Updated to version {version}"

    brd_json_str = json.dumps(brd_payload)

    # Upsert project (delete + insert for simplicity)
    delete_query = f"""
        DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )
    bq_client.query(delete_query, job_config=job_config).result()

    # Insert project
    rows = [{
        "id": project_id,
        "project_name": project_name,
        "domain": brd_payload.get("domain", "General"),
        "created_at": now,
        "confidence_score": coverage_score,
        "total_requirements": total_reqs,
        "conflict_count": conflict_count,
        "brd_json": brd_json_str
    }]
    table_ref = bq_client.get_table(f"{bq_dataset}.brd_projects")
    errors = bq_client.insert_rows_json(table_ref, rows)
    if errors:
        logger.error(f"BigQuery insert errors: {errors}")

    # Insert version
    version_rows = [{
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "version": version,
        "changed_at": now,
        "change_summary": summary,
        "brd_json": brd_json_str
    }]
    versions_table = bq_client.get_table(f"{bq_dataset}.brd_versions")
    errors = bq_client.insert_rows_json(versions_table, version_rows)
    if errors:
        logger.error(f"BigQuery version insert errors: {errors}")

    return project_id


def get_all_brds_bigquery() -> List[Dict[str, Any]]:
    """Retrieve all projects metadata from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    query = f"""
        SELECT id, project_name, domain, created_at, confidence_score,
               total_requirements, conflict_count
        FROM `{bq_dataset}.brd_projects`
        ORDER BY created_at DESC
    """
    result = bq_client.query(query).result()
    return [dict(row) for row in result]


def get_brd_by_id_bigquery(project_id: str) -> Optional[Dict[str, Any]]:
    """Get complete project record from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    query = f"""
        SELECT * FROM `{bq_dataset}.brd_projects`
        WHERE id = @project_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )
    result = bq_client.query(query, job_config=job_config).result()
    rows = list(result)
    if not rows:
        return None

    row = dict(rows[0])
    # Parse brd_json string back to dict
    if isinstance(row.get("brd_json"), str):
        try:
            row["brd_json"] = json.loads(row["brd_json"])
        except Exception:
            pass
    return row


def delete_brd_bigquery(project_id: str):
    """Delete project and its versions from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )

    # Delete versions
    bq_client.query(
        f"DELETE FROM `{bq_dataset}.brd_versions` WHERE project_id = @project_id",
        job_config=job_config
    ).result()

    # Delete project
    bq_client.query(
        f"DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id",
        job_config=job_config
    ).result()


def get_versions_bigquery(project_id: str) -> List[Dict[str, Any]]:
    """Get all saved versions for a project from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    query = f"""
        SELECT version, changed_at, change_summary, brd_json
        FROM `{bq_dataset}.brd_versions`
        WHERE project_id = @project_id
        ORDER BY version DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )
    result = bq_client.query(query, job_config=job_config).result()

    results = []
    for row in result:
        d = dict(row)
        if isinstance(d.get("brd_json"), str):
            try:
                d["brd_json"] = json.loads(d["brd_json"])
            except Exception:
                pass
        results.append(d)
    return results


# Auto-initialize only when explicitly enabled. This keeps local demo startup fast
# even when cloud credentials are present but network access is unavailable.
if config.ENABLE_BIGQUERY:
    init_bigquery()
