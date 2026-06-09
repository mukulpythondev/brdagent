# BRD Forge — Project Overview

**BRD Forge** (by team **Useless AI**) is an Intelligent Multi-Modal Business Requirements Document (BRD) Generation Agent. The platform is designed to streamline the work of product managers, business analysts, and system engineers by transforming unstructured inputs into professional, ready-to-use specifications.

---

## 🎯 Purpose and Goals

The primary goal of BRD Forge is to resolve the overhead and errors caused by fragmented documentation. Typically, requirements are scattered across meeting notes, chat logs, email briefs, and image wireframes. 

BRD Forge resolves this by:
1. **Consolidating Inputs**: Synthesizing diverse data types into a structured, unified schema.
2. **Conflict Resolution**: Detecting design and logical discrepancies (e.g., conflicting security protocols) early in the development lifecycle.
3. **Traceability**: Providing transparency by showing the direct source attribution for every requirement.
4. **Export Readiness**: Allowing team members to export the output to styled formats (PDF/Word) immediately.

---

## 💻 Tech Stack

- **Frontend User Interface**: Streamlit (Python 3.11+)
- **Large Language Model API**: Google Gemini 1.5 Pro
- **Persistence Engine**: SQLite (Simulating cloud BigQuery databases)
- **Document Rendering & Exporters**:
  - `ReportLab` (PDF exporter with custom templates)
  - `python-docx` (Word exporter with custom header styling)
- **Ingestion & Parsers**:
  - `PyPDF2` (PDF text extraction)
  - `Pillow` (Image decoding and Vision inputs)
