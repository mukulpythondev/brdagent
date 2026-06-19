"""
GCS Cloud Storage Adapter for BRD Forge.

If GCS credentials are configured (GCS_BUCKET_NAME + GCS_CREDENTIALS_PATH),
file uploads and exports are stored in Google Cloud Storage.
If not configured, falls back to local filesystem (uploads/ and outputs/ directories).
"""

import os
import logging
import uuid
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing Google Cloud Storage SDK
try:
    from google.cloud import storage as gcs
    GCS_INSTALLED = True
except ImportError:
    GCS_INSTALLED = False
    logger.info("google-cloud-storage not installed. GCS features disabled (local fallback mode).")

gcs_client = None
gcs_bucket = None
gcs_enabled = False
GCS_TIMEOUT_SECONDS = 15

def init_gcs():
    """
    Initialize GCS client if credentials are present.
    Call this once at application startup.
    """
    global gcs_client, gcs_bucket, gcs_enabled

    if not GCS_INSTALLED:
        logger.info("GCS SDK not installed. Using local filesystem for uploads/exports.")
        return

    bucket_name = os.getenv("GCS_BUCKET_NAME", "")
    credentials_path = os.getenv("GCS_CREDENTIALS_PATH", "")

    if not bucket_name:
        logger.info("GCS_BUCKET_NAME not set. Using local filesystem for uploads/exports.")
        return

    try:
        if credentials_path and os.path.exists(credentials_path):
            gcs_client = gcs.Client.from_service_account_json(credentials_path)
        else:
            # Try Application Default Credentials (e.g., running on GCE/Cloud Run)
            gcs_client = gcs.Client()

        gcs_bucket = gcs_client.bucket(bucket_name)
        # Test bucket access
        gcs_bucket.exists(timeout=GCS_TIMEOUT_SECONDS)
        gcs_enabled = True
        logger.info(f"GCS initialized successfully. Bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to initialize GCS: {e}")
        gcs_enabled = False


def is_gcs_enabled() -> bool:
    return gcs_enabled


def upload_file_to_gcs(local_path: str, remote_prefix: str = "uploads") -> Optional[str]:
    """
    Upload a local file to GCS bucket under the specified prefix.
    Returns the GCS blob URI (gs://bucket/path) if successful, else None.
    Falls back to local path if GCS is not enabled.
    """
    if not gcs_enabled:
        init_gcs()
    if not gcs_enabled:
        logger.debug(f"GCS disabled. File remains at local path: {local_path}")
        return local_path

    try:
        filename = os.path.basename(local_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        blob_name = f"{remote_prefix}/{timestamp}_{unique_id}_{filename}"

        blob = gcs_bucket.blob(blob_name)
        blob.upload_from_filename(local_path, timeout=GCS_TIMEOUT_SECONDS)

        gcs_uri = f"gs://{gcs_bucket.name}/{blob_name}"
        logger.info(f"Uploaded to GCS: {gcs_uri}")
        return gcs_uri
    except Exception as e:
        logger.error(f"GCS upload failed for {local_path}: {e}")
        return local_path


def upload_bytes_to_gcs(data: bytes, filename: str, remote_prefix: str = "exports",
                         content_type: str = "application/octet-stream") -> Optional[str]:
    """
    Upload raw bytes to GCS bucket.
    Returns the GCS public URL or blob path if successful.
    """
    if not gcs_enabled:
        init_gcs()
    if not gcs_enabled:
        return None

    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        blob_name = f"{remote_prefix}/{timestamp}_{unique_id}_{filename}"

        blob = gcs_bucket.blob(blob_name)
        blob.upload_from_string(data, content_type=content_type, timeout=GCS_TIMEOUT_SECONDS)

        gcs_uri = f"gs://{gcs_bucket.name}/{blob_name}"
        logger.info(f"Uploaded bytes to GCS: {gcs_uri}")
        return gcs_uri
    except Exception as e:
        logger.error(f"GCS bytes upload failed: {e}")
        return None


def download_file_from_gcs(gcs_uri: str, local_dest: str) -> bool:
    """
    Download a file from GCS to a local path.
    """
    if not gcs_enabled:
        init_gcs()
    if not gcs_enabled:
        return False

    try:
        # Parse gs://bucket/path format
        if gcs_uri.startswith("gs://"):
            path = gcs_uri.replace(f"gs://{gcs_bucket.name}/", "")
        else:
            path = gcs_uri

        blob = gcs_bucket.blob(path)
        blob.download_to_filename(local_dest, timeout=GCS_TIMEOUT_SECONDS)
        logger.info(f"Downloaded from GCS: {gcs_uri} -> {local_dest}")
        return True
    except Exception as e:
        logger.error(f"GCS download failed: {e}")
        return False


def list_files_in_gcs(prefix: str = "uploads") -> list:
    """
    List all files under a prefix in the GCS bucket.
    """
    if not gcs_enabled:
        init_gcs()
    if not gcs_enabled:
        return []

    try:
        blobs = gcs_bucket.list_blobs(prefix=prefix, timeout=GCS_TIMEOUT_SECONDS)
        return [{"name": b.name, "size": b.size, "updated": str(b.updated)} for b in blobs]
    except Exception as e:
        logger.error(f"GCS list failed: {e}")
        return []


def delete_file_from_gcs(blob_name: str) -> bool:
    """
    Delete a file from GCS.
    """
    if not gcs_enabled:
        init_gcs()
    if not gcs_enabled:
        return False

    try:
        blob = gcs_bucket.blob(blob_name)
        blob.delete(timeout=GCS_TIMEOUT_SECONDS)
        logger.info(f"Deleted from GCS: {blob_name}")
        return True
    except Exception as e:
        logger.error(f"GCS delete failed: {e}")
        return False


# GCS initializes lazily on first upload/list/download operation so backend
# startup stays fast even when cloud networking is slow.
