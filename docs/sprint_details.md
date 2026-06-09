# Sprint Backlog & Progress Tracker

This document tracks the tasks completed in **Sprint 1** and lists the remaining/upcoming items in the backlog for **Sprint 2** so that other team members can easily pick up work.

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

## 📋 Sprint 2 Backlog (Upcoming & Remaining Tasks) — Pending ⏳

These items are remaining in the backlog. Team members can assign themselves to these tasks for subsequent implementation.

### High Priority
- [ ] **GCP Cloud Storage Integration**: Replace the local `/uploads` folder with actual GCP Cloud Storage bucket connections.
- [ ] **BigQuery Integration**: Migrate the local SQLite persistence layer (`brd_forge.db`) to standard Google BigQuery tables.
- [ ] **Vertex AI Pipeline**: Wrap the Gemini integration into a formal Vertex AI agent pipeline.
- [ ] **Firebase Authentication**: Connect Streamlit login forms to live Firebase Authentication services (replacing simulated session state logs).

### Medium Priority
- [ ] **Interactive Visualizations**: Build native analytical dashboards inside Streamlit using `recharts` or `matplotlib` to graph requirements stats.
- [ ] **Bulk Actions Support**: Add checkboxes in the Functional Requirements table allowing users to bulk-resolve or bulk-delete multiple items at once.
- [ ] **Custom Style Templates**: Add configuration settings in `config.py` allowing users to upload corporate CSS sheets for PDF exports.

### Low Priority
- [ ] **Collaborative Sharing**: Support public-sharing links or email triggers using Nodemailer to send generated BRDs directly to stakeholders.
- [ ] **Excel Exporter**: Install `xlsx` to support downloading the requirements grid as an Excel spreadsheet.
