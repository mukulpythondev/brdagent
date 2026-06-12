# 🚀 BRD Forge — Setup & Execution Guide

Welcome to the **BRD Forge** Setup and Execution Guide. This document provides clear, step-by-step instructions for teammates and developers to set up, run, and test the BRD Forge application locally on their machines.

---

## 🏗️ Project Architecture Overview
BRD Forge is built as a split **Vite-React (Frontend)** and **FastAPI (Backend)** application:
* **Frontend:** React + Tailwind CSS (Vite dev server handles WebSocket proxying).
* **Backend:** FastAPI (Python 3.12) which processes document text, runs logic checks, and interfaces with databases.
* **Tri-Mode Database Fallback:** The backend dynamically prioritizes cloud storage:
  1. **BigQuery / Firestore** (If cloud credentials are configured).
  2. **Local SQLite Database** (If running offline or credentials are not configured).
* **AI & Storage Fallback:** Works fully offline using a local keyword analyzer and local folder structures if GCP keys are missing.

---

## 🛠️ Prerequisites
Before starting, ensure your machine has:
1. **Python 3.12+** installed and added to your system `PATH`.
2. **Node.js (v18 or higher)** and npm installed.
3. A terminal shell (PowerShell or Bash).

---

## 🖥️ Step-by-Step Local Setup & Run

### 1. Run the Frontend (React UI)
The frontend UI is already built and ready to be served.
1. Open a new terminal window.
2. Navigate to the frontend directory:
   ```bash
   cd d:/HackDelhi_BRD/brdagent/frontend
   ```
3. Install node packages:
   ```bash
   npm install
   ```
4. Run the frontend development server:
   ```bash
   npm run dev
   ```
   *The UI will launch, typically at **`http://localhost:5173`** or **`http://localhost:5174`**.*

---

### 2. Run the Backend (FastAPI Server)
To process files and trigger the AI parser logic, you need to run the Python server.
1. Open another terminal window.
2. Navigate to the backend directory:
   ```bash
   cd d:/HackDelhi_BRD/brdagent/backend
   ```
3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend server:
   ```bash
   python main.py
   ```
   *The backend will run on **`http://127.0.0.1:8000`**.*

---

### 🌟 3. Offline / Demo Mode (No-Server Fallback)
If you cannot run the Python backend on a laptop during the meeting, **the app has a built-in Offline Demo Mode:**
* You can open the frontend (`http://localhost:5174`), click **"Sign In"** directly (it accepts dummy inputs), and a full high-fidelity **Online Banking Portal** workspace will load directly from browser `localStorage`!
* All dashboard cards, requirements grids, analytics charts (quality and priority breakdown), risks, and visualizer modules are fully populated and functional.
* You can delete requirements, change priorities, and resolve contradictions in real-time, and it will sync directly to the browser storage!

---

## 🧪 Testing Your Own Requirements (Copy-Paste Test)
To demonstrate the actual logic-parser and conflict detector in action (with or without cloud keys):
1. Navigate to the **Upload** page in the UI.
2. Input Project Name: `Secure Pay Wallet`
3. Domain Selection: Choose `FinTech` from the dropdown list.
4. Paste the following text into the **"Raw Text Notes"** box:

```text
Project: Secure Pay Wallet Integration Specs

Functional Requirements:
1. SEC-101: The system must automatically lock the user account permanently after exactly 3 consecutive failed login attempts to protect against brute-force attacks.
2. SEC-102: System administrators must be able to bypass any account lockouts immediately at any time using override codes to ensure zero support delays.
3. TXN-201: The mobile dashboard must display user balances updated in real-time, syncing details via web socket connections.
4. NOTIF-301: Send automatic SMS and email notifications to the user for every transaction above $50.

Non-Functional Requirements:
1. PERF-401: All balance queries must return results to the UI with a response latency of under 300 milliseconds.
2. COMP-402: All database writes and transactional data records must comply with PCI-DSS Section 3 security isolation parameters.
```

5. Click **"Generate"**.
6. The app will trigger the processing pipeline and flag a **Logical Contradiction** between **SEC-101** (strict permanent lock) and **SEC-102** (admin instant lockout bypass), showing you the red warning panel where you can resolve the clash live!

---

## 🔑 Cloud Credentials Configuration (For Team Leader)
To move from local SQLite fallback to live Google Cloud Platform (GCP) integration:
1. **Firebase Firestore & Auth:** Place a valid service account credential file named `firebase-key.json` in the root of the `/backend` folder.
2. **Environment Variables:** Create a `.env` file in the `/backend` folder and add:
   ```env
   # Gemini & Vertex AI
   GEMINI_API_KEY=your_gemini_api_key_here
   VERTEX_PROJECT_ID=your_gcp_project_id
   VERTEX_LOCATION=us-central1

   # Cloud Storage & BigQuery
   GCS_BUCKET_NAME=your_gcs_bucket_name
   BQ_PROJECT_ID=your_bq_project_id
   
   # JWT & App
   JWT_SECRET=your_jwt_signing_key_here
   ```

---

## 👥 Hackathon Team: Useless AI
* **Mukul Rana**
* **Manideep Bishnoi**
* **Shanu Prajapati**
