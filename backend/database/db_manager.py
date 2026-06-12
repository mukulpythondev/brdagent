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
from typing import List, Dict, Any

from database.firebase_handler import is_firebase_enabled
from database.bigquery_handler import is_bigquery_enabled
import database.firebase_handler as fb
import database.db_handler as sq
import database.bigquery_handler as bq

logger = logging.getLogger(__name__)


def get_db_mode() -> str:
    """
    Returns the active database mode: 'bigquery', 'firebase', or 'sqlite'.
    """
    if is_bigquery_enabled():
        return "bigquery"
    if is_firebase_enabled():
        return "firebase"
    return "sqlite"


def save_brd(project_name: str, brd_payload: Dict[str, Any], project_id: str = None) -> str:
    """
    Saves a BRD document to the active database.
    """
    mode = get_db_mode()
    if mode == "bigquery":
        logger.info("Saving project to Google BigQuery...")
        return bq.save_brd_bigquery(project_name, brd_payload, project_id)
    elif mode == "firebase":
        logger.info("Saving project to Google Firestore collection...")
        return fb.save_brd_firestore(project_name, brd_payload, project_id)
    else:
        logger.info("Saving project to SQLite local table...")
        return sq.save_brd(project_name, brd_payload, project_id)


def get_all_brds() -> List[Dict[str, Any]]:
    """
    Retrieves all projects from the active database.
    """
    mode = get_db_mode()
    if mode == "bigquery":
        return bq.get_all_brds_bigquery()
    elif mode == "firebase":
        return fb.get_all_brds_firestore()
    else:
        return sq.get_all_brds()


def get_brd_by_id(project_id: str) -> Dict[str, Any]:
    """
    Gets project details by ID.
    """
    mode = get_db_mode()
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
    mode = get_db_mode()
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
    mode = get_db_mode()
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
