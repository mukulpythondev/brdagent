"""
BRD Forge Database Manager — Tri-Mode Storage Adapter.

Priority chain (highest to lowest):
1. BigQuery — If BQ_PROJECT_ID is configured (enterprise analytics).
2. Firestore — If firebase-key.json is present (cloud collaboration).
3. SQLite — Default local fallback (zero-setup sandbox).

This module transparently routes all CRUD operations to the active adapter.
"""

import json
import logging
import os
from typing import List, Dict, Any

from database.firebase_handler import is_firebase_enabled
from database.bigquery_handler import is_bigquery_enabled
import database.firebase_handler as fb
import database.db_handler as sq
import database.bigquery_handler as bq

logger = logging.getLogger(__name__)
DELETED_PROJECTS_FILE = os.path.join(os.path.dirname(__file__), "deleted_projects.json")


def _load_deleted_project_ids() -> set:
    try:
        if os.path.exists(DELETED_PROJECTS_FILE):
            with open(DELETED_PROJECTS_FILE, "r") as f:
                return set(json.load(f))
    except Exception as e:
        logger.warning("Could not load deleted project tombstones: %s", e)
    return set()


def _mark_project_deleted(project_id: str):
    deleted = _load_deleted_project_ids()
    deleted.add(project_id)
    try:
        with open(DELETED_PROJECTS_FILE, "w") as f:
            json.dump(sorted(deleted), f, indent=2)
    except Exception as e:
        logger.warning("Could not save deleted project tombstone for %s: %s", project_id, e)


def _is_project_deleted(project_id: str) -> bool:
    return project_id in _load_deleted_project_ids()


def get_db_mode(try_init_cloud: bool = False) -> str:
    """
    Returns the active database mode: 'bigquery', 'firebase', or 'sqlite'.
    """
    if try_init_cloud and bq.config.ENABLE_BIGQUERY and not is_bigquery_enabled():
        bq.init_bigquery()
    if is_bigquery_enabled():
        return "bigquery"
    if is_firebase_enabled():
        return "firebase"
    return "sqlite"


def save_brd(project_name: str, brd_payload: Dict[str, Any], project_id: str = None) -> str:
    """
    Saves a BRD document to the active database.
    """
    mode = get_db_mode(try_init_cloud=True)
    if mode == "bigquery":
        logger.info("Saving project to Google BigQuery...")
        saved_id = bq.save_brd_bigquery(project_name, brd_payload, project_id)
    elif mode == "firebase":
        logger.info("Saving project to Google Firestore collection...")
        saved_id = fb.save_brd_firestore(project_name, brd_payload, project_id)
    else:
        logger.info("Saving project to SQLite local table...")
        saved_id = sq.save_brd(project_name, brd_payload, project_id)

    return saved_id


def get_all_brds() -> List[Dict[str, Any]]:
    """
    Retrieves all projects from the active database.
    """
    mode = get_db_mode(try_init_cloud=True)
    if mode == "bigquery":
        projects = bq.get_all_brds_bigquery()
    elif mode == "firebase":
        projects = fb.get_all_brds_firestore()
    else:
        projects = sq.get_all_brds()
    deleted_ids = _load_deleted_project_ids()
    return [project for project in projects if project.get("id") not in deleted_ids]


def get_brd_by_id(project_id: str) -> Dict[str, Any]:
    """
    Gets project details by ID.
    """
    mode = get_db_mode(try_init_cloud=True)
    if _is_project_deleted(project_id):
        return None
    if mode == "bigquery":
        return bq.get_brd_by_id_bigquery(project_id)
    elif mode == "firebase":
        data = fb.get_brd_by_id_firestore(project_id)
        return data
    else:
        row = sq.get_brd_by_id(project_id)
        if row and "brd_json" in row:
            try:
                if isinstance(row["brd_json"], str):
                    row["brd_json"] = json.loads(row["brd_json"])
            except Exception:
                pass
        return row


def delete_brd(project_id: str):
    """
    Deletes project.
    """
    errors = []
    _mark_project_deleted(project_id)

    if bq.config.ENABLE_BIGQUERY:
        try:
            if not is_bigquery_enabled():
                bq.init_bigquery()
            if is_bigquery_enabled():
                bq.delete_brd_bigquery(project_id)
        except Exception as e:
            logger.warning("BigQuery delete skipped/failed for %s: %s", project_id, e)
            errors.append(f"bigquery: {e}")

    if is_firebase_enabled():
        try:
            fb.delete_brd_firestore(project_id)
        except Exception as e:
            logger.warning("Firestore delete skipped/failed for %s: %s", project_id, e)
            errors.append(f"firestore: {e}")

    try:
        sq.delete_brd(project_id)
    except Exception as e:
        logger.warning("SQLite delete skipped/failed for %s: %s", project_id, e)
        errors.append(f"sqlite: {e}")

    return {"deleted": True, "warnings": errors}


def delete_brd_active_only(project_id: str):
    """
    Deletes project from the active adapter only.
    """
    mode = get_db_mode(try_init_cloud=True)
    if mode == "bigquery":
        bq.delete_brd_bigquery(project_id)
    elif mode == "firebase":
        fb.delete_brd_firestore(project_id)
    else:
        sq.delete_brd(project_id)


def get_versions(project_id: str) -> List[Dict[str, Any]]:
    """
    Gets list of saved versions.
    """
    mode = get_db_mode(try_init_cloud=True)
    if mode == "bigquery":
        return bq.get_versions_bigquery(project_id)
    elif mode == "firebase":
        return fb.get_versions_firestore(project_id)
    else:
        rows = sq.get_versions(project_id)
        for row in rows:
            try:
                if isinstance(row.get("brd_json"), str):
                    row["brd_json"] = json.loads(row["brd_json"])
            except Exception:
                pass
        return rows
