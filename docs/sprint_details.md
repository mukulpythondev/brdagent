# Sprint Backlog & Progress Tracker

This document tracks the tasks completed in **Sprint 1 & 2** and lists the remaining configuration items so that the team leader can finalize the live deployment.

---

## 🏃 Sprint 1 (Prototype Core & Refinements) — Completed ✅

All core prototype components for the first release of **BRD Forge** have been successfully built and verified.

### Core Features
- [x] **Project Ingestion Setup**: Created `core/ingestion.py` to handle file uploads and save them to the `uploads/` directory.
- [x] **File Parsers**: Built `utils/pdf_parser.py` using PyPDF2 and configured text/docx readers.
- [x] **Gemini Agent Integration**: Built `core/gemini_agent.py` to analyze documents and wireframe images using Gemini 1.5 Pro. Added high-fidelity mock fallback responses if the API key is not present.
- [x] **Conflict Detector**: Created `core/conflict_detector.py` to search for requirement contradictions.
- [x] **Traceability Engine**: Built `core/explainability.py` to link requirements to their source file and line context.
- [x] **Industry Customizer**: Built `core/domain_classifier.py` to auto-detect the industry domain and suggest compliance templates.
- [x] **Database Storage**: Built `database/db_handler.py` to manage SQLite schemas, versions, and projects.
- [x] **Styled PDF Exporter**: Developed ReportLab PDF generation with custom cover pages, tables, and page numbers.
- [x] **Styled Word Exporter**: Developed DOCX generation using python-docx.
- [x] **Streamlit UI Interface**: Configured `app.py` with multi-page navigation, custom CSS, live preview panels, and interactive page triggers.

### Refinements & Quick Fixes
- [x] **Streamlit API Fix**: Replaced unexpected `kind` parameters with `type="secondary"` for button components.
- [x] **Visualizer Layout Fix**: Replaced space characters in the README Mermaid diagram code to enable GitHub rendering.
- [x] **Agent Connectivity Banner**: Added a sidebar banner indicating whether the app is running in Demo or Gemini Live mode.
- [x] **Folder Security**: Configured `.gitignore` to prevent committing databases, scratch uploads, and `.env` files.

---

## 🏃 Sprint 2 (React + FastAPI SaaS Architecture) — Completed ✅

All Sprint 2 architecture and integration features have been implemented.

### React Frontend (Vite + Tailwind)
- [x] **Interactive Dashboards & Analytics**: Recharts-based PieChart, BarChart, RadarChart for requirements stats.
- [x] **Premium Themes & Layouts**: Full Light/Dark modes, glassmorphic login, resizable sidebar, tactile 3D buttons.
- [x] **Split-Pane BRD Visualizer**: Pinned headers, independently scrolling columns, bulk actions toolbar.
- [x] **Bulk Actions Support**: Checkbox selection in Functional Requirements table for bulk-delete and bulk-priority updates.

### FastAPI Backend Server
- [x] **REST API Endpoints**: Auth (login/signup/logout), Project CRUD, AI Generation, Conflict Resolution, Version History.
- [x] **Styled Exporters**: PDF (ReportLab), Word (.docx), Excel (.xlsx) binary stream download endpoints.
- [x] **Email Sharing**: SMTP-based PDF attachment delivery to stakeholder emails.
- [x] **Vite Proxy Mapping**: Frontend to backend proxy on port 8000 for CORS-free API access.

### Sprint 2 — GCP Integrations (Implemented, Awaiting Credentials)
- [x] **GCP Cloud Storage Adapter**: Built `core/gcs_storage.py` — uploads, downloads, lists, and deletes files from GCS buckets. Graceful fallback to local `/uploads` if GCS is not configured.
- [x] **BigQuery Database Adapter**: Built `database/bigquery_handler.py` — full CRUD (save, get all, get by ID, delete, versions) with BigQuery tables. Falls back to SQLite/Firestore if not configured.
- [x] **Vertex AI Pipeline**: Built `core/vertex_pipeline.py` — wraps Gemini calls into Vertex AI managed pipeline. Falls back to standard google-generativeai SDK if not configured.
- [x] **Firebase Authentication**: Built `database/firebase_handler.py` — full Firestore CRUD + Firebase Auth token verification. Falls back to local JWT if `firebase-key.json` is not present.
- [x] **Tri-Mode Database Manager**: Updated `database/db_manager.py` — BigQuery > Firestore > SQLite priority chain with transparent routing.

### Sprint 2 — AI Upgrades
- [x] **Gemini Semantic Conflicts**: Upgraded `conflict_detector.py` — multi-layer pipeline with rule-based heuristics (always active) + Gemini LLM semantic analysis (when API key is set).
- [x] **WebSocket Progress Tracking**: Added `/ws/progress` WebSocket endpoint for real-time pipeline status broadcasts.
- [x] **System Integration Status API**: Added `/api/system/integrations` endpoint showing all connected service states.

### Sprint 2 — Export & Sharing
- [x] **Excel Exporter**: Built `utils/excel_exporter.py` using openpyxl for requirements grid download.
- [x] **Custom Style Templates**: Config settings in `config.py` for theme color customization in PDF exports.

---

## 🔧 Remaining Configuration (For Team Leader)

All code is implemented. The following items only require **credential configuration** (no coding needed):

### A. GCP Credentials Setup
- [ ] **GCS Bucket**: Create GCS bucket, add bucket name to `backend/.env` as `GCS_BUCKET_NAME`. Place service account JSON key path in `GCS_CREDENTIALS_PATH`.
- [ ] **BigQuery**: Enable BigQuery API, set `BQ_PROJECT_ID` in `backend/.env`. Place service account JSON key path in `BQ_CREDENTIALS_PATH`.
- [ ] **Vertex AI**: Enable Vertex AI API, set `VERTEX_PROJECT_ID` in `backend/.env`. Place service account JSON key path in `VERTEX_CREDENTIALS_PATH`.
- [ ] **Firebase**: Create Firebase project, download `firebase-key.json` to `backend/` root. Add Firebase Web SDK config to `frontend/.env.local`.

### B. API Keys
- [ ] **Gemini API Key**: Set `GEMINI_API_KEY` in `backend/.env` to enable live AI synthesis (demo mode works without it).
- [ ] **SMTP Email**: Set `SMTP_USERNAME` and `SMTP_PASSWORD` in `backend/.env` for email sharing feature.

