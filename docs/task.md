# Progress Checklist - FastAPI & React Integration (Sprint 2)

- [/] **Phase 1: Reorganization & Setup**
  - [x] Create `backend` directory and reorganize python files
  - [x] Update `backend/requirements.txt` with new packages (`fastapi`, `uvicorn`, `python-multipart`, `firebase-admin`, `openpyxl`)
  - [x] Update `backend/config.py` paths and SMTP credentials settings
- [x] **Phase 2: Database & Sharing Utilities**
  - [x] Implement Firebase service-account checker and `database/firebase_handler.py`
  - [x] Update `database/db_handler.py` (or db manager) for dual-mode Firestore/SQLite storage
  - [x] Create requirements Excel exporter utility in `backend/utils/`
  - [x] Create SMTP email sharing utility in `backend/utils/`
- [x] **Phase 3: FastAPI Server Development**
  - [x] Create `backend/main.py` entry point with CORS and local JWT/Firebase auth validation middleware
  - [x] Implement authentication endpoints (`/api/auth/login`, `/api/auth/signup`, `/api/auth/logout`)
  - [x] Implement project endpoints (`GET /api/projects`, `GET /api/projects/{id}`, `DELETE /api/projects/{id}`, `PUT /api/projects/{id}`)
  - [x] Implement requirements synthesis endpoint `POST /api/projects` (processing pasted text, files, and multi-modal analysis via `generate_brd`)
  - [x] Implement conflict resolution `POST /api/projects/{id}/resolve` and versions listing `/api/projects/{id}/versions`
  - [x] Implement PDF, DOCX, and Excel file export streams
  - [x] Implement SMTP email sharing route `/api/projects/{id}/share`
- [x] **Phase 4: Frontend AppContext Synchronization**
  - [x] Update `frontend/src/context/AppContext.jsx` authentication and session persistence (connecting login/signup to API)
  - [x] Update project operations (fetching active lists, loading project detail view, calling synthesis API with files/form data)
  - [x] Wire up canvas edit saving and bulk requirements actions to API updates
  - [x] Redirect file exports (PDF, Word, Excel) to server download endpoints
  - [x] Wire up share email modal to API
- [x] **Phase 5: Verification & Testing**
  - [x] Verify local SQLite fallback mode works out-of-the-box (creating projects, deleting, updating, exporting)
  - [x] Verify visual states and layout controls in frontend (resizable sidebar, scroll margins, analytics charts)

---

## Mentor Change - Adaptive Multi-Model AI Routing

- [x] Add adaptive model router for modality, input length, complexity, and risk.
- [x] Route short/simple text extraction to `GEMINI_FAST_MODEL`.
- [x] Route long PDFs/documents, multi-source synthesis, and conflict reasoning to `GEMINI_ADVANCED_MODEL`.
- [x] Route image/wireframe analysis to `GEMINI_VISION_MODEL`.
- [x] Store model route reasons in generated BRD payload as `model_routing_decisions`.
- [x] Store demo-ready architecture summary in generated BRD payload as `ai_architecture`.
- [x] Add AI Routing section in the React visualizer.
- [x] Add env-tunable model settings and token thresholds.

## Full Demo Remaining TODO

- [ ] Restart backend after credential/env changes.
- [x] Verify live OpenAI generation with one short pasted text input.
- [ ] Verify adaptive routing with mixed inputs: pasted text + PDF/DOCX + image.
- [ ] Verify GCS bucket access for `brd-forge-uploads`.
- [ ] Verify BigQuery project save/list/detail flow for `brdagent-499304`.
- [ ] Verify optional Vertex AI credentials/API access only if Google Cloud runtime is shown.
- [ ] Generate one polished demo project and confirm AI Routing section appears.
- [ ] Test conflict detection using SSO vs password-only sample.
- [ ] Export PDF, DOCX, and XLSX from the same generated project.
- [ ] Add Gmail App Password to `SMTP_PASSWORD` if email sharing must be shown.
- [ ] Upgrade Node from `20.16.0` to `20.19+` or `22.12+` before final demo.
- [ ] Decide whether to implement or remove docs reference to `/api/system/integrations`.
