# 🔬 BRD Forge — Project Overview & Winning Probability Report

**BRD Forge** is an AI-powered Multi-Modal Business Requirements Document (BRD) Generation Agent designed for the Google AI Hackathon. It solves the critical problem of fragmented requirements in product management by converting unstructured, multi-modal project inputs into professional, audit-ready, and conflict-checked specification documents.

---

## 🎯 1. Why Are We Building This? (The Problem)

In modern software development, product requirements are rarely clean. They are scattered across:
*   **Meeting Notes / Emails:** Unstructured, conversational, and conversational text.
*   **Reference Documents:** PDFs or Word briefs with regulatory constraints.
*   **Visual Mockups / Diagrams:** UI wireframes, PNGs of whiteboard flows, and system architecture sketches.

Product Managers (PMs) and Business Analysts (BAs) spend a significant amount of time:
1.  **Ingesting & Organizing:** Manually parsing and consolidating these multi-modal formats.
2.  **Aligning & Translating:** Mapping high-level client wishes to functional requirements while ensuring regulatory compliance (e.g., HIPAA, PCI-DSS).
3.  **Conflict Checking:** Finding contradictions (e.g., the security team wants *username + password only*, but the business team wants *Google SSO*). These are often missed and discovered late, costing time and money.
4.  **Attribution/Traceability:** Proving *where* a requirement came from during audit stages.

**BRD Forge** automates this entire pipeline, turning hours of manual labor into a few seconds of AI-driven synthesis.

---

## 🛠️ 2. Current vs. Potential Features

### 🟢 Current Features (Implemented in Prototype)
1.  **Multi-Modal Ingestion:** Supports text copy-paste, TXT files, PDFs, DOCX, and images (PNG/JPG).
2.  **Domain Classification:** Automatically identifies the industry domain (FinTech, HealthTech, EdTech, E-Commerce, Government, Enterprise) and suggests relevant compliance lists (e.g., HIPAA, PCI-DSS) and glossary terms.
3.  **AI-Powered Requirements Synthesis:** Uses Google Gemini 1.5 Pro to extract, structure, and merge features into standard Functional Requirements (FR) and Non-Functional Requirements (NFR).
4.  **Heuristic Conflict Detection:** Evaluates requirements pairwise to detect security and storage contradictions (e.g., SSO vs. Password only, Offline vs. Cloud Sync).
5.  **Traceability Engine:** Attaches confidence ratings (High/Medium/Low) and sources trace explanations showing which file a requirement came from.
6.  **Interactive Streamlit UI:** Features a dark-themed sidebar menu, live preview overlays, and an active database connection monitor.
7.  **Styled Document Exporters:** Exports the final BRD to a styled ReportLab PDF (with page numbers and cover page) or an editable DOCX format.
8.  **Project Archive & Versioning:** Saves history in a local SQLite database, allowing users to view, load, delete, and version-track saved BRDs.

### 🟡 Potential Winning Features (Sprint 2 & Beyond)
To make this project a true hackathon winner, we should implement the following:
1.  **Intelligent LLM-Based Conflict Detection:** Move from hardcoded regex keywords to a live Gemini-driven semantic conflict engine that reasons *why* two requirements clash.
2.  **Interactive Requirement Mapping (Visual Graph):** Instead of simple tables, display requirements as an interactive flow or mind-map using React Flow / Mermaid.js to visually show tracing and conflicts.
3.  **Advanced Gemini Vision parsing:** Feed UI wireframes and architecture diagrams directly to Gemini's multimodal window to auto-generate UI components, field validations, and user flow stories.
4.  **Google Cloud Infrastructure Integration:** Connect Streamlit to live GCP services:
    *   **Google Cloud Storage (GCS)** for file uploads instead of local folders.
    *   **Google BigQuery** for historical enterprise data storage simulation.
    *   **Vertex AI Agent Builder** to orchestrate agent reasoning chains.
    *   **Firebase Authentication** for secure user login.
5.  **Interactive Requirement Editor:** Allow users to edit, add, or reject requirements directly in the UI before exporting, with the AI recalculating conflicts and confidence scores in real time.

---

## 🏆 3. Winning Probability Assessment

| Metric | Current Prototype (Sprint 1) | Fully Upgraded Project (Sprint 2 Targets) |
| :--- | :--- | :--- |
| **Concept & Utility** | ⭐⭐⭐⭐ (Solid BA utility) | ⭐⭐⭐⭐⭐ (Enterprise-grade BA assistant) |
| **GCP / Gemini Integration** | ⭐⭐ (Basic API calls & Fallbacks) | ⭐⭐⭐⭐⭐ (Full Vertex AI, BigQuery, GCS integration) |
| **UI/UX Aesthetics** | ⭐⭐⭐ (Clean Streamlit layout) | ⭐⭐⭐⭐⭐ (Next.js premium dark glassmorphism) |
| **Technical Depth** | ⭐⭐ (Heuristic rules & SQLite) | ⭐⭐⭐⭐ (Intelligent AI Agent + Vector DB) |
| **Winning Probability** | **35% - 40%** | **80% - 85%** |

### Why is the Current Winning Probability 35-40%?
1.  **Heavy Reliance on Hardcoded Mocks:** The conflict detector, explainability engine, and domain classifier use basic string matches or hardcoded text rather than dynamic Gemini reasoning. If a user uploads real documents, the conflict check won't work unless it happens to match the word "SSO" or "Offline".
2.  **Local Architecture:** The app is a standard local Python script using SQLite. Hackathon judges look for scalable cloud architectures, preferably utilizing Google Cloud Platform (GCP) technologies (BigQuery, GCS, Vertex AI, Firebase).
3.  **Streamlit Visual Limitation:** While neat, Streamlit applications are very common in AI hackathons and look like internal data science tools rather than ready-to-sell startup products.

### How to Achieve an 80%+ Winning Probability:
1.  **Make the AI Agent "Real":** Replace the hardcoded regex conflict check and domain lookup with structured Gemini API calls (using JSON Schemas/Structured Output).
2.  **Integrate Google Cloud Services:** Connect the app to GCS and BigQuery to demonstrate a production-ready GCP architecture.
3.  **Add Interactive Collaborative Editing:** Allow users to edit the requirements on screen and see conflicts resolve in real-time.
