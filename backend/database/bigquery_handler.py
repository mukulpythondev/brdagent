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
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import config

logger = logging.getLogger(__name__)

# Try importing BigQuery SDK
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession, Request as GoogleAuthRequest
    BQ_INSTALLED = True
except ImportError:
    BQ_INSTALLED = False
    logger.info("google-cloud-bigquery not installed. BigQuery features disabled.")

bq_client = None
bq_enabled = False
bq_dataset = None
BQ_PROJECT_ID = None
BQ_DATASET_ID = None
BQ_TRANSPORT = "sdk"
BQ_CREDENTIALS = None
BQ_TIMEOUT_SECONDS = 15
bq_last_error = None
bq_init_attempted = False


class InsecureGoogleAuthRequest(GoogleAuthRequest):
    """Local-dev Google auth request that bypasses broken Windows CA chains."""

    def __call__(self, url, method="GET", body=None, headers=None, timeout=None, **kwargs):
        kwargs["verify"] = False
        return super().__call__(url, method=method, body=body, headers=headers, timeout=timeout, **kwargs)


def _init_bigquery_sync():
    """
    Initialize BigQuery client if credentials are present.
    Creates dataset and tables if they don't exist.
    """
    global bq_client, bq_enabled, bq_dataset, bq_last_error, bq_init_attempted
    global BQ_PROJECT_ID, BQ_DATASET_ID, BQ_TRANSPORT, BQ_CREDENTIALS
    bq_init_attempted = True
    bq_last_error = None

    if not BQ_INSTALLED:
        bq_last_error = "BigQuery SDK not installed."
        logger.info("BigQuery SDK not installed. Using SQLite/Firestore fallback.")
        return False

    project_id = os.getenv("BQ_PROJECT_ID", "")
    dataset_id = os.getenv("BQ_DATASET_ID", "brd_forge_dataset")
    credentials_path = os.getenv("BQ_CREDENTIALS_PATH", "")

    if not project_id:
        bq_last_error = "BQ_PROJECT_ID not set."
        logger.info("BQ_PROJECT_ID not set. Using SQLite/Firestore fallback.")
        return False

    try:
        BQ_PROJECT_ID = project_id
        BQ_DATASET_ID = dataset_id
        bq_dataset = f"{project_id}.{dataset_id}"

        if credentials_path and os.path.exists(credentials_path) and not config.GOOGLE_VERIFY_SSL:
            BQ_CREDENTIALS = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            BQ_TRANSPORT = "rest"
            _ensure_dataset_rest()
            _ensure_tables_exist_rest()
            bq_enabled = True
            logger.info(f"BigQuery initialized via REST. Dataset: {bq_dataset}")
            return True

        if credentials_path and os.path.exists(credentials_path):
            if config.GOOGLE_VERIFY_SSL:
                bq_client = bigquery.Client.from_service_account_json(credentials_path)
            else:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
                auth_request = InsecureGoogleAuthRequest()
                authed_session = AuthorizedSession(credentials, auth_request=auth_request)
                authed_session.verify = False
                bq_client = bigquery.Client(
                    project=project_id,
                    credentials=credentials,
                    _http=authed_session,
                )
        else:
            bq_client = bigquery.Client(project=project_id)

        # Create dataset if not exists
        dataset_ref = bigquery.Dataset(bq_dataset)
        dataset_ref.location = "US"
        try:
            bq_client.get_dataset(bq_dataset, timeout=BQ_TIMEOUT_SECONDS)
        except Exception:
            bq_client.create_dataset(dataset_ref, exists_ok=True, timeout=BQ_TIMEOUT_SECONDS)

        # Create tables if not exist
        _ensure_tables_exist()

        bq_enabled = True
        logger.info(f"BigQuery initialized. Dataset: {bq_dataset}")
        return True
    except Exception as e:
        bq_last_error = str(e)
        logger.error(f"Failed to initialize BigQuery: {e}")
        bq_enabled = False
        return False


def init_bigquery(timeout_seconds: int = BQ_TIMEOUT_SECONDS) -> bool:
    """
    Initialize BigQuery with a hard wall-clock guard so startup/demo cannot hang.
    """
    if bq_enabled:
        return True

    result = {"ok": False}

    def target():
        result["ok"] = _init_bigquery_sync()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        global bq_last_error, bq_init_attempted
        bq_init_attempted = True
        bq_last_error = f"BigQuery initialization timed out after {timeout_seconds} seconds."
        logger.error(bq_last_error)
        return False
    return result["ok"]


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
        bq_client.get_table(projects_table, timeout=BQ_TIMEOUT_SECONDS)
    except Exception:
        bq_client.create_table(projects_table, exists_ok=True, timeout=BQ_TIMEOUT_SECONDS)

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
        bq_client.get_table(versions_table, timeout=BQ_TIMEOUT_SECONDS)
    except Exception:
        bq_client.create_table(versions_table, exists_ok=True, timeout=BQ_TIMEOUT_SECONDS)


def is_bigquery_enabled() -> bool:
    return bq_enabled


def get_bigquery_status() -> Dict[str, Any]:
    return {
        "installed": BQ_INSTALLED,
        "enabled": bq_enabled,
        "init_attempted": bq_init_attempted,
        "dataset": bq_dataset,
        "transport": BQ_TRANSPORT,
        "last_error": bq_last_error,
    }


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
        if BQ_TRANSPORT == "rest":
            rows = _query_rest(
                f"""
                SELECT COUNT(*) as cnt FROM `{bq_dataset}.brd_versions`
                WHERE project_id = @project_id
                """,
                [_string_param("project_id", project_id)],
            )
            version = int(rows[0].get("cnt", 0)) + 1 if rows else 1
        else:
            query = f"""
                SELECT COUNT(*) as cnt FROM `{bq_dataset}.brd_versions`
                WHERE project_id = @project_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
                ]
            )
            result = bq_client.query(query, job_config=job_config, timeout=BQ_TIMEOUT_SECONDS).result(timeout=BQ_TIMEOUT_SECONDS)
            row = list(result)[0]
            version = row.cnt + 1
        summary = f"Updated to version {version}"

    brd_json_str = json.dumps(brd_payload)

    if BQ_TRANSPORT == "rest":
        if project_id:
            _query_rest(
                f"DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id",
                [_string_param("project_id", project_id)],
            )
        _insert_rows_rest("brd_projects", [{
            "id": project_id,
            "project_name": project_name,
            "domain": brd_payload.get("domain", "General"),
            "created_at": now,
            "confidence_score": coverage_score,
            "total_requirements": total_reqs,
            "conflict_count": conflict_count,
            "brd_json": brd_json_str
        }])
        _insert_rows_rest("brd_versions", [{
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "version": version,
            "changed_at": now,
            "change_summary": summary,
            "brd_json": brd_json_str
        }])
        return project_id

    # Upsert project (delete + insert for simplicity)
    delete_query = f"""
        DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )
    bq_client.query(delete_query, job_config=job_config, timeout=BQ_TIMEOUT_SECONDS).result(timeout=BQ_TIMEOUT_SECONDS)

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
    table_ref = bq_client.get_table(f"{bq_dataset}.brd_projects", timeout=BQ_TIMEOUT_SECONDS)
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
    versions_table = bq_client.get_table(f"{bq_dataset}.brd_versions", timeout=BQ_TIMEOUT_SECONDS)
    errors = bq_client.insert_rows_json(versions_table, version_rows)
    if errors:
        logger.error(f"BigQuery version insert errors: {errors}")

    return project_id


def get_all_brds_bigquery() -> List[Dict[str, Any]]:
    """Retrieve all projects metadata from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    if BQ_TRANSPORT == "rest":
        return _query_rest(f"""
            SELECT id, project_name, domain, created_at, confidence_score,
                   total_requirements, conflict_count
            FROM `{bq_dataset}.brd_projects`
            ORDER BY created_at DESC
        """)

    query = f"""
        SELECT id, project_name, domain, created_at, confidence_score,
               total_requirements, conflict_count
        FROM `{bq_dataset}.brd_projects`
        ORDER BY created_at DESC
    """
    result = bq_client.query(query, timeout=BQ_TIMEOUT_SECONDS).result(timeout=BQ_TIMEOUT_SECONDS)
    return [dict(row) for row in result]


def get_brd_by_id_bigquery(project_id: str) -> Optional[Dict[str, Any]]:
    """Get complete project record from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    if BQ_TRANSPORT == "rest":
        rows = _query_rest(
            f"""
            SELECT * FROM `{bq_dataset}.brd_projects`
            WHERE id = @project_id
            LIMIT 1
            """,
            [_string_param("project_id", project_id)],
        )
        if not rows:
            return None
        row = rows[0]
        if isinstance(row.get("brd_json"), str):
            try:
                row["brd_json"] = json.loads(row["brd_json"])
            except Exception:
                pass
        return row

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
    result = bq_client.query(query, job_config=job_config, timeout=BQ_TIMEOUT_SECONDS).result(timeout=BQ_TIMEOUT_SECONDS)
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

    if BQ_TRANSPORT == "rest":
        _query_rest(
            f"DELETE FROM `{bq_dataset}.brd_versions` WHERE project_id = @project_id",
            [_string_param("project_id", project_id)],
        )
        _query_rest(
            f"DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id",
            [_string_param("project_id", project_id)],
        )
        return

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id)
        ]
    )

    # Delete versions
    bq_client.query(
        f"DELETE FROM `{bq_dataset}.brd_versions` WHERE project_id = @project_id",
        job_config=job_config,
        timeout=BQ_TIMEOUT_SECONDS
    ).result(timeout=BQ_TIMEOUT_SECONDS)

    # Delete project
    bq_client.query(
        f"DELETE FROM `{bq_dataset}.brd_projects` WHERE id = @project_id",
        job_config=job_config,
        timeout=BQ_TIMEOUT_SECONDS
    ).result(timeout=BQ_TIMEOUT_SECONDS)


def get_versions_bigquery(project_id: str) -> List[Dict[str, Any]]:
    """Get all saved versions for a project from BigQuery."""
    if not bq_enabled:
        raise ValueError("BigQuery is not enabled.")

    if BQ_TRANSPORT == "rest":
        results = _query_rest(
            f"""
            SELECT version, changed_at, change_summary, brd_json
            FROM `{bq_dataset}.brd_versions`
            WHERE project_id = @project_id
            ORDER BY version DESC
            """,
            [_string_param("project_id", project_id)],
        )
        for row in results:
            if isinstance(row.get("brd_json"), str):
                try:
                    row["brd_json"] = json.loads(row["brd_json"])
                except Exception:
                    pass
        return results

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
    result = bq_client.query(query, job_config=job_config, timeout=BQ_TIMEOUT_SECONDS).result(timeout=BQ_TIMEOUT_SECONDS)

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


def _refresh_rest_credentials():
    if not BQ_CREDENTIALS:
        raise ValueError("BigQuery REST credentials are not loaded.")
    if not BQ_CREDENTIALS.valid:
        BQ_CREDENTIALS.refresh(InsecureGoogleAuthRequest())


def _bq_rest(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    _refresh_rest_credentials()
    url = f"https://bigquery.googleapis.com/bigquery/v2/{path.lstrip('/')}"
    response = requests.request(
        method,
        url,
        headers={
            "Authorization": f"Bearer {BQ_CREDENTIALS.token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=BQ_TIMEOUT_SECONDS,
        verify=config.GOOGLE_VERIFY_SSL,
    )
    if response.status_code == 404:
        return {"_not_found": True}
    response.raise_for_status()
    if response.text:
        return response.json()
    return {}


def _ensure_dataset_rest():
    dataset_path = f"projects/{BQ_PROJECT_ID}/datasets/{BQ_DATASET_ID}"
    existing = _bq_rest("GET", dataset_path)
    if not existing.get("_not_found"):
        return
    _bq_rest("POST", f"projects/{BQ_PROJECT_ID}/datasets", {
        "datasetReference": {
            "projectId": BQ_PROJECT_ID,
            "datasetId": BQ_DATASET_ID,
        },
        "location": "US",
    })


def _table_schema_rest(fields: List[Dict[str, str]]) -> Dict[str, Any]:
    return {"schema": {"fields": fields}}


def _ensure_table_rest(table_id: str, fields: List[Dict[str, str]]):
    table_path = f"projects/{BQ_PROJECT_ID}/datasets/{BQ_DATASET_ID}/tables/{table_id}"
    existing = _bq_rest("GET", table_path)
    if not existing.get("_not_found"):
        return
    body = {
        "tableReference": {
            "projectId": BQ_PROJECT_ID,
            "datasetId": BQ_DATASET_ID,
            "tableId": table_id,
        },
        **_table_schema_rest(fields),
    }
    _bq_rest("POST", f"projects/{BQ_PROJECT_ID}/datasets/{BQ_DATASET_ID}/tables", body)


def _ensure_tables_exist_rest():
    _ensure_table_rest("brd_projects", [
        {"name": "id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "project_name", "type": "STRING"},
        {"name": "domain", "type": "STRING"},
        {"name": "created_at", "type": "TIMESTAMP"},
        {"name": "confidence_score", "type": "FLOAT"},
        {"name": "total_requirements", "type": "INTEGER"},
        {"name": "conflict_count", "type": "INTEGER"},
        {"name": "brd_json", "type": "STRING"},
    ])
    _ensure_table_rest("brd_versions", [
        {"name": "id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "project_id", "type": "STRING"},
        {"name": "version", "type": "INTEGER"},
        {"name": "changed_at", "type": "TIMESTAMP"},
        {"name": "change_summary", "type": "STRING"},
        {"name": "brd_json", "type": "STRING"},
    ])


def _insert_rows_rest(table_id: str, rows: List[Dict[str, Any]]):
    body = {
        "kind": "bigquery#tableDataInsertAllRequest",
        "rows": [{"json": row} for row in rows],
    }
    result = _bq_rest(
        "POST",
        f"projects/{BQ_PROJECT_ID}/datasets/{BQ_DATASET_ID}/tables/{table_id}/insertAll",
        body,
    )
    if result.get("insertErrors"):
        raise ValueError(f"BigQuery insert errors: {result['insertErrors']}")


def _query_rest(query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    body = {
        "query": query,
        "useLegacySql": False,
    }
    if parameters:
        body["parameterMode"] = "NAMED"
        body["queryParameters"] = parameters
    result = _bq_rest("POST", f"projects/{BQ_PROJECT_ID}/queries", body)
    fields = result.get("schema", {}).get("fields", [])
    rows = result.get("rows", [])
    parsed = []
    for row in rows:
        values = row.get("f", [])
        parsed.append({
            field["name"]: values[idx].get("v")
            for idx, field in enumerate(fields)
            if idx < len(values)
        })
    return parsed


def _string_param(name: str, value: str) -> Dict[str, Any]:
    return {
        "name": name,
        "parameterType": {"type": "STRING"},
        "parameterValue": {"value": value},
    }


# BigQuery is initialized lazily by db_manager/system test endpoints.
# This keeps backend startup safe when cloud networking or IAM is slow.
