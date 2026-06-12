# Comprehensive Implementation Plan: FastAPI & React Integration with Firebase (Sprint 2)

This plan details transitioning **BRD Forge** into a clean frontend/backend structure, implementing the FastAPI server, and configuring a **Firebase-First Architecture** for free-tier database storage and authentication, with an automatic local fallback (SQLite + session JWTs) for seamless local sandbox testing.

---

## 📂 1. Directory Structure Reorganization
We will group all Python backend modules under a `backend` folder:
- **`brdagent/backend/`**: Contains server code (`main.py`), modules (`core/`, `database/`, `utils/`), configurations (`config.py`, `.env`), and uploads/outputs folders.
- **`brdagent/frontend/`**: Contains React client codebase (`src/`, `package.json`, `vite.config.js`).

---

## 🔒 2. Firebase-First Integration Design

To implement Firebase (which has a generous free tier for Auth and Firestore) without breaking the application if a live Firebase project isn't configured yet, we will implement a dual-mode adapter pattern:

### A. Authentication Architecture
1.  **Frontend (React)**: 
    *   If Firebase credentials (`VITE_FIREBASE_API_KEY`, etc.) are present in `.env.local`, we initialize the Firebase Client SDK.
    *   Authentication (login/signup) is handled via Firebase Auth. The ID token is fetched using `user.getIdToken()` and sent in the `Authorization: Bearer <token>` header to the FastAPI server.
    *   If credentials are missing, we fall back to a local REST-based form submit that generates standard local JWT tokens.
2.  **Backend (FastAPI)**:
    *   When an API request arrives, the security middleware checks the `Authorization` header.
    *   If Firebase is enabled, it validates the token using `firebase_admin.auth.verify_id_token(token)`.
    *   If Firebase is disabled/fallback mode, it decodes the local JWT token using our server secret key.

### B. Database Storage Architecture
1.  **Data Models**:
    *   We will define standard repository interfaces for project CRUD operations.
2.  **Dual Adapters**:
    *   **Firestore Adapter**: If `firebase-service-account.json` or Firebase environment variables are configured, we save and version BRD documents in Google Cloud Firestore collections (`projects` and `versions`).
    *   **SQLite Adapter**: If Firebase is not configured, we write to the local SQLite database (`brd_forge.db`) using the existing `database/db_handler.py`.

---

## ⚡ 3. FastAPI REST API Endpoint Design (`backend/main.py`)

The backend will expose the following endpoints:
*   `POST /api/auth/login`: Handles fallback authentication (if Firebase is disabled).
*   `POST /api/auth/signup`: Handles fallback account creation.
*   `GET /api/projects`: Returns all projects belonging to the authenticated user.
*   `GET /api/projects/{project_id}`: Returns the complete JSON schema for a specific project.
*   `POST /api/projects`: Multi-part endpoint. Uploads specification files, runs the AI synthesis pipeline (`generate_brd(...)`), saves the project to the database, and returns the payload.
*   `PUT /api/projects/{project_id}`: Saves edits made in the visualizer canvas. Creates a new version record.
*   `DELETE /api/projects/{project_id}`: Removes the project and its version logs.
*   `POST /api/projects/{project_id}/resolve`: Accepts `conflict_id` and `resolution_type` to resolve logic conflicts and update requirements.
*   `GET /api/projects/{project_id}/versions`: Returns document revision history.
*   `GET /api/projects/{project_id}/export/pdf`: Generates and downloads the styled PDF with theme parameters.
*   `GET /api/projects/{project_id}/export/docx`: Generates and downloads the Word document.
*   `GET /api/projects/{project_id}/export/xlsx`: Generates and downloads the Excel requirements sheet.
*   `POST /api/projects/{project_id}/share`: Sends the PDF document attachment via SMTP email.

---

## 🎨 4. Frontend AppContext Integration

*   **Initialization**: Reads Firebase configurations from environment variables. If present, initializes Firebase app.
*   **Authentication Flow**: Connects `handleLogin`, `handleSignup`, and `handleLogout` to Firebase user state listeners. Stores the active access token in context state.
*   **API Queries**: Passes the token in the `Authorization: Bearer <token>` header of every API call.
*   **Export Redirects**: Opens file download endpoints in a new tab, passing the token as a query parameter (or header check) to authorize the download.
*   **Bulk Actions & Sharing**: Connected directly to the respective FastAPI endpoints.

---

## 📋 5. Action Items for Execution

1.  **Restructure Folders**: Move python scripts to `backend/`.
2.  **Configure Dependencies**: Update `backend/requirements.txt` to include `firebase-admin`, `fastapi`, `uvicorn`, `python-multipart`, and `openpyxl`.
3.  **Implement DB & Auth Adapters**:
    *   Create `backend/database/firebase_handler.py` to handle Firestore/Authentication validation.
    *   Create a manager in `backend/database/db_manager.py` that decides whether to run Firestore or SQLite based on credentials presence.
4.  **Build FastAPI Server**: Create `backend/main.py` with all routing logic, security middleware, exporters, and sharing tools.
5.  **Refactor React Client Context**: Update `frontend/src/context/AppContext.jsx` to support Firebase initialization and fetch requests.

---

## 🧪 6. Verification Plan

*   **Offline Verification**: Run without configuring Firebase. Verify the server successfully defaults to SQLite + local JWT auth, and the React UI functions perfectly.
*   **Online Verification**: Create a free Firebase project, copy credentials into the `.env` files, and test live sign-in and document syncing to Firestore database collections.
