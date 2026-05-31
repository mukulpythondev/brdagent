import os
import time
import json
import logging
import streamlit as st
import pandas as pd
import config
from core.ingestion import process_file_upload, clear_uploads
from core.brd_generator import generate_brd
from database.db_handler import save_brd, get_all_brds, get_brd_by_id, delete_brd
from utils.export import export_to_pdf, export_to_word

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="BRD Forge — Turn Chaos into Clarity",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "brd_data" not in st.session_state:
    st.session_state.brd_data = {}
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = [] # list of processed files dicts
if "current_project" not in st.session_state:
    st.session_state.current_project = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "🔬 Upload & Ingest"
if "project_id" not in st.session_state:
    st.session_state.project_id = None
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = "Auto-detect"
if "pasted_text" not in st.session_state:
    st.session_state.pasted_text = ""

# Inject custom stylesheet for dark Google Cloud colors
st.markdown("""
<style>
  /* App backgrounds */
  .stApp { 
    background-color: #1E1E2E; 
    color: #FFFFFF; 
  }
  
  /* Text and standard links styling */
  h1, h2, h3, p, span, label, div {
    color: #FFFFFF !important;
  }
  
  /* Sidebar styles */
  [data-testid="stSidebar"] {
    background-color: #13131E !important;
    border-right: 1px solid #2A2A3E;
  }
  
  /* Inputs backgrounds */
  div[data-baseweb="select"] > div, 
  div[data-baseweb="input"] > div, 
  textarea {
    background-color: #2A2A3E !important;
    color: #FFFFFF !important;
    border: 1px solid #4285F4 !important;
  }
  
  /* Buttons styling */
  .stButton>button { 
    background-color: #4285F4 !important; 
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
    width: 100%;
  }
  .stButton>button:hover {
    background-color: #357ae8 !important;
    box-shadow: 0px 4px 10px rgba(66, 133, 244, 0.4) !important;
  }
  
  /* Secondary/Danger buttons */
  .stButton>button[type="secondary"] {
    background-color: #EA4335 !important;
  }
  
  /* Custom containers and cards */
  .card-container {
    background-color: #2A2A3E;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    border-left: 5px solid #4285F4;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
  }
  
  .badge-col {
    background-color: #2A2A3E;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #33334A;
  }
  
  .badge-val {
    font-size: 2rem;
    font-weight: bold;
    color: #4285F4 !important;
  }
  
  /* Confidence Badges */
  .confidence-high { 
    background-color: #34A853; 
    color: #FFFFFF !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.75rem;
    display: inline-block;
  }
  .confidence-medium { 
    background-color: #FBBC04; 
    color: #000000 !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.75rem;
    display: inline-block;
  }
  .confidence-low { 
    background-color: #EA4335;
    color: #FFFFFF !important; 
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.75rem;
    display: inline-block;
  }
  
  .conflict-badge {
    background-color: #EA4335;
    color: #FFFFFF !important;
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.75rem;
    display: inline-block;
  }
  
  /* Expander styling */
  .streamlit-expanderHeader {
    background-color: #222235 !important;
    border-radius: 5px;
    border: 1px solid #33334F !important;
  }
</style>
""", unsafe_allow_html=True)


# Sidebar Menu navigation
st.sidebar.markdown(f"<h2 style='text-align: center; color: #4285F4;'>🔬 BRD FORGE</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; font-size: 0.85rem; color: #888;'>Useless AI | Version {config.APP_VERSION}</p>", unsafe_allow_html=True)
st.sidebar.divider()

# Navigation selector
menu_selection = st.sidebar.radio(
    "Navigation", 
    ["🔬 Upload & Ingest", "📊 BRD Visualizer", "📜 Project Archive"],
    label_visibility="collapsed"
)

# Synchronize menu selection with active page state
if st.session_state.active_page != menu_selection:
    st.session_state.active_page = menu_selection

# Display Gemini Status Badge in Sidebar
st.sidebar.divider()
st.sidebar.markdown("### Agent Connectivity")
if config.DEMO_MODE:
    st.sidebar.info("🤖 **Mode: DEMO** (Simulated fallback active)")
else:
    st.sidebar.success("⚡ **Mode: GEMINI LIVE** (Active connection)")

# --- PAGE 1: UPLOAD & INGEST ---
if st.session_state.active_page == "🔬 Upload & Ingest":
    st.markdown("<h1>🔬 BRD Forge</h1>", unsafe_allow_html=True)
    st.markdown("<h5>Turn Chaos Into Clarity — AI-Powered Multi-Modal BRD Generation</h5>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns([2, 3], gap="large")
    
    with col1:
        st.markdown("### 📥 Project Setup & Ingestion")
        
        # Project inputs
        proj_name = st.text_input("Project Name", value=st.session_state.current_project, placeholder="e.g. Online Banking Portal")
        st.session_state.current_project = proj_name
        
        domain_list = ["Auto-detect", "FinTech", "HealthTech", "E-Commerce", "Enterprise", "Government", "EdTech"]
        st.session_state.selected_domain = st.selectbox("Industry Domain", domain_list, index=domain_list.index(st.session_state.selected_domain))
        
        # Pasted raw requirements
        st.session_state.pasted_text = st.text_area("Paste Raw Requirements / Emails", value=st.session_state.pasted_text, height=180, placeholder="Type or paste unstructured meeting notes, emails, or requirements list...")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Documents or Wireframes", 
            type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
            accept_multiple_files=True
        )
        
        # Ingestion loader button
        # Process files when they change
        if uploaded_files:
            for uf in uploaded_files:
                # Avoid duplicates
                if not any(f["filename"] == uf.name for f in st.session_state.uploaded_files):
                    # Process
                    with st.spinner(f"Ingesting {uf.name}..."):
                        file_data = process_file_upload(uf)
                        st.session_state.uploaded_files.append(file_data)
                        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Action Buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            try_demo_btn = st.button("🎯 Try Demo", help="Load banking sample documents instantly and run requirements synthesis.")
            
        with btn_col2:
            generate_btn = st.button("⚙️ Generate BRD")
            
        # Try Demo Logic
        if try_demo_btn:
            # Clear previous runs
            st.session_state.uploaded_files = []
            clear_uploads()
            
            # Load sample text
            sample_txt_path = os.path.join(config.SAMPLE_INPUTS_DIR, "sample_text.txt")
            sample_conf_path = os.path.join(config.SAMPLE_INPUTS_DIR, "sample_conflict.txt")
            
            # Ensure sample files exist
            if not os.path.exists(sample_txt_path):
                # Write standard content if missing
                with open(sample_txt_path, "w") as f:
                    f.write("Project: Online Banking Portal\nStakeholders: Product Manager (John), Dev Lead (Sarah), Compliance Officer (Mike)\nRequirements:\n- Users must login using SSO with Google/Microsoft\n- Dashboard should show account balance in real-time\n- Transaction history for last 12 months\n- Mobile responsive design mandatory\n- Must comply with PCI-DSS standards\n- Page load time under 2 seconds\n- Support 10,000 concurrent users")
            if not os.path.exists(sample_conf_path):
                with open(sample_conf_path, "w") as f:
                    f.write("Security team note:\n- All authentication must use username + password only\n- No third party SSO providers allowed per security policy\n- Two factor authentication via SMS is mandatory")
            
            # Load mock inputs into session state
            with open(sample_txt_path, "r") as f:
                content_text = f.read()
            st.session_state.uploaded_files.append({
                "filename": "sample_text.txt",
                "extension": ".txt",
                "size_mb": 0.01,
                "type": "text",
                "content": content_text
            })
            
            with open(sample_conf_path, "r") as f:
                content_conf = f.read()
            st.session_state.uploaded_files.append({
                "filename": "sample_conflict.txt",
                "extension": ".txt",
                "size_mb": 0.01,
                "type": "text",
                "content": content_conf
            })
            
            st.session_state.current_project = "Online Banking Portal"
            st.session_state.selected_domain = "FinTech"
            st.rerun()

        # Run Synthesis logic
        if generate_btn:
            # Check validation
            all_inputs = []
            for f in st.session_state.uploaded_files:
                all_inputs.append(f)
            if st.session_state.pasted_text.strip():
                all_inputs.append({
                    "filename": "pasted_text_input",
                    "extension": ".txt",
                    "size_mb": 0.01,
                    "type": "text",
                    "content": st.session_state.pasted_text
                })
                
            if not all_inputs:
                st.error("Please paste text or upload at least one file before generating a BRD.")
            elif not st.session_state.current_project.strip():
                st.error("Please enter a Project Name.")
            else:
                # Trigger process simulation spinner sequence
                status_box = st.empty()
                
                with status_box.container():
                    with st.spinner("🔍 Ingesting inputs..."):
                        time.sleep(0.5)
                    with st.spinner("🔍 Analyzing your inputs..."):
                        time.sleep(0.8)
                    with st.spinner("🧠 Gemini is processing..."):
                        time.sleep(0.8)
                    with st.spinner("⚙️ Generating requirements..."):
                        time.sleep(0.6)
                    with st.spinner("🔍 Detecting conflicts..."):
                        time.sleep(0.5)
                
                status_box.success("✅ BRD generated successfully!")
                time.sleep(0.5)
                status_box.empty()
                
                # Call generator
                with st.spinner("Assembling final document payload..."):
                    brd_res = generate_brd(
                        st.session_state.current_project,
                        st.session_state.selected_domain,
                        all_inputs
                    )
                    st.session_state.brd_data = brd_res
                    st.session_state.project_id = None # New unsaved project
                    
                # Auto route to visualizer
                st.session_state.active_page = "📊 BRD Visualizer"
                st.rerun()

    with col2:
        st.markdown("### 📄 Ingested Document Preview")
        
        # Text and files count statistics
        has_pasted = 1 if st.session_state.pasted_text.strip() else 0
        total_sources = len(st.session_state.uploaded_files) + has_pasted
        total_size = sum(f.get("size_mb", 0) for f in st.session_state.uploaded_files)
        
        preview_meta_cols = st.columns(3)
        preview_meta_cols[0].metric("Total Inputs", total_sources)
        preview_meta_cols[1].metric("Uploaded Files", len(st.session_state.uploaded_files))
        preview_meta_cols[2].metric("Total File Size", f"{total_size:.2f} MB")
        
        st.divider()
        
        if total_sources == 0:
            st.info("No documents uploaded or text pasted yet. Upload wireframes or briefs in the left panel to begin, or click 'Try Demo'.")
        else:
            # Clean All button
            if st.button("🧹 Clear All Inputs", type="secondary"):
                st.session_state.uploaded_files = []
                st.session_state.pasted_text = ""
                clear_uploads()
                st.rerun()
                
            # Pasted text item
            if st.session_state.pasted_text.strip():
                with st.expander("📝 Raw Pasted Text Input", expanded=True):
                    st.text_area("Pasted Content Snippet", st.session_state.pasted_text[:500] + ("..." if len(st.session_state.pasted_text) > 500 else ""), height=150, disabled=True)
                    
            # Uploaded files items list
            for f in st.session_state.uploaded_files:
                ext = f.get("extension", "")
                icon = "📝"
                if ext == ".pdf":
                    icon = "📄"
                elif ext in [".png", ".jpg", ".jpeg"]:
                    icon = "🖼️"
                elif ext == ".docx":
                    icon = "📘"
                    
                with st.expander(f"{icon} {f.get('filename')} ({f.get('size_mb')} MB)", expanded=False):
                    st.write(f"**File Type:** {f.get('type').upper()}")
                    if f.get("type") == "image":
                        st.image(f.get("bytes"), caption=f.get("filename"), use_column_width=True)
                    else:
                        st.text_area("File Content Preview", f.get("content", "")[:800] + ("..." if len(f.get("content", "")) > 800 else ""), height=180, disabled=True)


# --- PAGE 2: BRD VISUALIZER ---
elif st.session_state.active_page == "📊 BRD Visualizer":
    st.markdown("<h1>📊 Requirements Visualizer</h1>", unsafe_allow_html=True)
    
    brd = st.session_state.brd_data
    
    if not brd:
        st.info("No BRD has been generated yet. Please upload requirements documents on the [Upload Page] or load a sample via 'Try Demo'.")
    else:
        # Title meta section
        proj_title = brd.get("project_name", "Untitled Project")
        domain_val = brd.get("domain", "General")
        
        col_title, col_badge = st.columns([4, 1])
        with col_title:
            st.markdown(f"### Project Name: **{proj_title}**")
        with col_badge:
            st.markdown(f"<div style='text-align: right;'><span style='background-color: #4285F4; padding: 6px 15px; border-radius: 20px; font-weight: bold;'>🏷️ {domain_val}</span></div>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='color: #888; font-size: 0.85rem; margin-top: -10px;'>Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
        st.divider()
        
        # Stats summary indicators
        frs = brd.get("functional_requirements", [])
        nfrs = brd.get("non_functional_requirements", [])
        total_reqs = len(frs) + len(nfrs)
        
        high_conf_count = sum(1 for req in frs + nfrs if req.get("confidence") == "HIGH")
        conflicts_count = len(brd.get("detected_conflicts", []))
        
        # Coverage calculation
        coverage_score = round((high_conf_count / max(total_reqs, 1)) * 100, 1)
        
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.markdown(f"<div class='badge-col'><p style='color: #888;'>Total Requirements</p><p class='badge-val'>{total_reqs}</p></div>", unsafe_allow_html=True)
        with stat_cols[1]:
            st.markdown(f"<div class='badge-col'><p style='color: #888;'>High Confidence</p><p class='badge-val' style='color: #34A853 !important;'>{high_conf_count}</p></div>", unsafe_allow_html=True)
        with stat_cols[2]:
            st.markdown(f"<div class='badge-col'><p style='color: #888;'>Conflicts Found</p><p class='badge-val' style='color: #EA4335 !important;'>{conflicts_count}</p></div>", unsafe_allow_html=True)
        with stat_cols[3]:
            st.markdown(f"<div class='badge-col'><p style='color: #888;'>Coverage Score</p><p class='badge-val'>{coverage_score}%</p></div>", unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Split screen for Conflict panel sidebar
        col_main, col_conflict = st.columns([3, 1], gap="medium")
        
        with col_main:
            # 1. Executive Summary Accordion
            with st.expander("📋 1. Executive Summary", expanded=True):
                st.markdown(f"<div class='card-container'><p>{brd.get('executive_summary')}</p></div>", unsafe_allow_html=True)
                
            # 2. Objectives Accordion
            with st.expander("🎯 2. Project Objectives", expanded=False):
                st.markdown("#### Key Objectives")
                for idx, obj in enumerate(brd.get("objectives", [])):
                    st.markdown(f"**{idx + 1}.** {obj}")
                    
            # 3. Scope Accordion
            with st.expander("🔭 3. Scope Boundaries", expanded=False):
                scope_cols = st.columns(2)
                with scope_cols[0]:
                    st.markdown("#### ✅ In-Scope")
                    for s in brd.get("scope", {}).get("in_scope", []):
                        st.markdown(f"- {s}")
                with scope_cols[1]:
                    st.markdown("#### ❌ Out-of-Scope")
                    for s in brd.get("scope", {}).get("out_scope", []):
                        st.markdown(f"- {s}")
                        
            # 4. Stakeholders Accordion
            with st.expander("👥 4. Stakeholders Matrix", expanded=False):
                st.markdown("#### Key Project Stakeholders")
                sh_cols = st.columns(3)
                for i, sh in enumerate(brd.get("stakeholders", [])):
                    col_idx = i % 3
                    with sh_cols[col_idx]:
                        st.markdown(f"<div style='background-color: #2A2A3E; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>👤 {sh}</div>", unsafe_allow_html=True)
                        
            # 5. Functional Requirements Table Accordion
            with st.expander("⚙️ 5. Functional Requirements", expanded=True):
                if not frs:
                    st.info("No functional requirements specified.")
                else:
                    for fr in frs:
                        # Construct a grid element
                        fid = fr.get("id")
                        title = fr.get("title")
                        desc = fr.get("description")
                        src = fr.get("source")
                        conf = fr.get("confidence", "MEDIUM")
                        priority = fr.get("priority", "MUST HAVE")
                        conflict_desc = fr.get("conflict")
                        
                        # Style based on confidence
                        badge_html = ""
                        if conf == "HIGH":
                            badge_html = "<span class='confidence-high'>🟢 HIGH</span>"
                        elif conf == "MEDIUM":
                            badge_html = "<span class='confidence-medium'>🟡 MEDIUM</span>"
                        else:
                            badge_html = "<span class='confidence-low'>🔴 LOW</span>"
                            
                        # Build container style
                        border_color = "#34A853" if conf == "HIGH" else ("#FBBC04" if conf == "MEDIUM" else "#EA4335")
                        if conflict_desc:
                            border_color = "#EA4335" # Red border for conflict
                            
                        html_content = f"""
                        <div style="background-color: #2A2A3E; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; border-left: 5px solid {border_color};">
                          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: bold; font-size: 1.1rem; color: #4285F4 !important;">{fid}: {title}</span>
                            <div>
                              <span style="background-color: #1E1E2E; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px;">⚡ {priority}</span>
                              {badge_html}
                            </div>
                          </div>
                          <p style="margin-bottom: 0.8rem;">{desc}</p>
                          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888 !important; border-top: 1px solid #33334A; padding-top: 5px;">
                            <span><b>Source:</b> {src}</span>
                            <span><b>Trace explanation:</b> {fr.get('source_trace', 'Derived from input file.')}</span>
                          </div>
                        """
                        if conflict_desc:
                            html_content += f"""
                            <div style="margin-top: 10px; padding: 8px; background-color: rgba(234, 67, 53, 0.1); border: 1px solid #EA4335; border-radius: 4px;">
                              <span class="conflict-badge">⚠️ CONFLICT</span>
                              <span style="margin-left: 5px; color: #FFD2D2 !important;">{conflict_desc}</span>
                            </div>
                            """
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
                        
            # 6. Non-Functional Requirements Table Accordion
            with st.expander("🔒 6. Non-Functional Requirements", expanded=True):
                if not nfrs:
                    st.info("No non-functional requirements specified.")
                else:
                    for nfr in nfrs:
                        nid = nfr.get("id")
                        title = nfr.get("title")
                        desc = nfr.get("description")
                        src = nfr.get("source")
                        conf = nfr.get("confidence", "MEDIUM")
                        
                        badge_html = ""
                        if conf == "HIGH":
                            badge_html = "<span class='confidence-high'>🟢 HIGH</span>"
                        elif conf == "MEDIUM":
                            badge_html = "<span class='confidence-medium'>🟡 MEDIUM</span>"
                        else:
                            badge_html = "<span class='confidence-low'>🔴 LOW</span>"
                            
                        border_color = "#34A853" if conf == "HIGH" else ("#FBBC04" if conf == "MEDIUM" else "#EA4335")
                        
                        st.markdown(f"""
                        <div style="background-color: #2A2A3E; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; border-left: 5px solid {border_color};">
                          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: bold; font-size: 1.1rem; color: #4285F4 !important;">{nid}: {title}</span>
                            {badge_html}
                          </div>
                          <p style="margin-bottom: 0.8rem;">{desc}</p>
                          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888 !important; border-top: 1px solid #33334A; padding-top: 5px;">
                            <span><b>Source:</b> {src}</span>
                            <span><b>Trace explanation:</b> {nfr.get('source_trace', 'Derived from input file.')}</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
            # 7. Risks & Mitigations Accordion
            with st.expander("⚠️ 7. Risks & Mitigations", expanded=False):
                r_list = brd.get("risks", [])
                if not r_list:
                    st.info("No risks defined.")
                else:
                    for idx, r in enumerate(r_list):
                        st.markdown(f"""
                        <div class='card-container' style='border-left: 5px solid #EA4335;'>
                          <h5>Risk {idx + 1}: {r.get('risk')}</h5>
                          <p style='margin-bottom: 0px;'><b>Mitigation Strategy:</b> {r.get('mitigation')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
            # 8. Assumptions Accordion
            with st.expander("📝 8. Assumptions & Dependencies", expanded=False):
                for idx, a in enumerate(brd.get("assumptions", [])):
                    st.markdown(f"**{idx + 1}.** {a}")
                    
            # 9. Acceptance Criteria
            with st.expander("✅ 9. Acceptance Criteria Checklist", expanded=False):
                for idx, c in enumerate(brd.get("acceptance_criteria", [])):
                    st.checkbox(f"{c}", value=False, key=f"ac_check_{idx}")
                    
            # Industry adjustments template summary
            with st.expander("💡 10. Industry-Specific Suggestions (BRD Adjustments)", expanded=False):
                adj = brd.get("domain_adjustments", {})
                st.markdown(f"##### Recommended Compliance Standards for **{domain_val}**:")
                for standard in adj.get("compliance_standards", []):
                    st.markdown(f"- `{standard}`")
                st.markdown(f"##### Key Non-Functional Focus:")
                st.write(adj.get("nfr_focus", ""))
                st.markdown(f"##### Recommended Glossary terms:")
                st.write(", ".join(adj.get("glossary", [])))
                
        # --- Sidebar / Right Column Conflict Panel ---
        with col_conflict:
            st.markdown("### ⚠️ Conflicts Panel")
            st.write("Identifies overlapping contradictions between your files.")
            
            if conflicts_count == 0:
                st.success("No contradictions identified in the requirements!")
            else:
                for idx, conf in enumerate(brd.get("detected_conflicts", [])):
                    st.markdown(f"""
                    <div style="background-color: rgba(234, 67, 53, 0.15); border: 1px solid #EA4335; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
                      <p style="margin-bottom: 4px; font-weight: bold; color: #EA4335 !important;">Conflict #{idx+1}: {conf.get('req1_id')} vs {conf.get('req2_id')}</p>
                      <p style="font-size: 0.85rem; margin-bottom: 5px;">{conf.get('description')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Conflict resolution button
                st.write("Choose a resolution path:")
                resolution_choice = st.selectbox(
                    "Resolve conflict by:",
                    ["Federated/Corporate SSO with MFA (Recommended)", "Password login only with 2FA", "Support Both modes independently"],
                    label_visibility="collapsed"
                )
                
                resolve_btn = st.button("🔧 Apply Resolution & Merge")
                if resolve_btn:
                    with st.spinner("🧠 Resolving and updating BRD..."):
                        time.sleep(1.0)
                        
                        # Merge conflict logic in session state
                        frs_new = []
                        # Filter out the conflicting requirements and replace with merged requirement
                        for fr in brd.get("functional_requirements", []):
                            if fr.get("id") not in ["FR-004", "FR-005"]:
                                frs_new.append(fr)
                                
                        # Insert merged requirement
                        if "SSO with MFA" in resolution_choice:
                            frs_new.append({
                                "id": "FR-004",
                                "title": "Corporate SSO with MFA Enforcement",
                                "description": "The system must allow users to authenticate using Single Sign-On (SSO) integrated with Google/Microsoft directories, enforced with mandatory SMS or Authenticator app multi-factor authentication (MFA) to satisfy both access convenience and strict security guidelines.",
                                "source": "Merged Resolution",
                                "confidence": "HIGH",
                                "conflict": None,
                                "priority": "MUST HAVE",
                                "source_trace": "Resolved from conflicting SSO requirements (FR-004) and Password authentication (FR-005)."
                            })
                        elif "Password login only" in resolution_choice:
                            frs_new.append({
                                "id": "FR-005",
                                "title": "Secure Password Logins with SMS 2FA",
                                "description": "All system logins must authenticate via traditional user credentials (username and password) with mandatory SMS two-factor authentication, strictly blocking external federated IDP authentications per security standards.",
                                "source": "Merged Resolution",
                                "confidence": "HIGH",
                                "conflict": None,
                                "priority": "MUST HAVE",
                                "source_trace": "Resolved by prioritizing Security note requirements over standard user briefs."
                            })
                        else:
                            # Both
                            frs_new.append({
                                "id": "FR-004",
                                "title": "Multi-mode authentication framework",
                                "description": "Support dual authentication flows: secure Google/Microsoft SSO for general corporate users, and local username/password with SMS 2FA for administrative and external portal partners.",
                                "source": "Merged Resolution",
                                "confidence": "HIGH",
                                "conflict": None,
                                "priority": "MUST HAVE",
                                "source_trace": "Resolved by enabling modular logins for different user groups."
                            })
                            
                        # Update session state and reset conflict counters
                        st.session_state.brd_data["functional_requirements"] = frs_new
                        st.session_state.brd_data["detected_conflicts"] = []
                        
                        # Also remove conflict flags in requirements
                        for fr in frs_new:
                            fr["conflict"] = None
                            
                        st.success("Conflict resolved successfully!")
                        time.sleep(0.5)
                        st.rerun()

        # --- Bottom Action Bar ---
        st.divider()
        action_cols = st.columns(4)
        
        # PDF exporter
        pdf_data = export_to_pdf(brd)
        with action_cols[0]:
            st.download_button(
                label="📥 Export as PDF",
                data=pdf_data,
                file_name=f"{proj_title.replace(' ', '_')}_BRD.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        # DOCX exporter
        docx_data = export_to_word(brd)
        with action_cols[1]:
            st.download_button(
                label="📄 Export as Word",
                data=docx_data,
                file_name=f"{proj_title.replace(' ', '_')}_BRD.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        # Save to Database history
        with action_cols[2]:
            save_hist_btn = st.button("💾 Save to History")
            if save_hist_btn:
                # Save to database
                brd_json_str = json.dumps(brd)
                project_id = save_brd(proj_title, brd_json_str, project_id=st.session_state.project_id)
                st.session_state.project_id = project_id
                st.success("Project saved successfully to Archive!")
                
        # Reset / Regenerate
        with action_cols[3]:
            regen_btn = st.button("🔄 Regenerate")
            if regen_btn:
                st.session_state.active_page = "🔬 Upload & Ingest"
                st.rerun()


# --- PAGE 3: HISTORY ARCHIVE ---
elif st.session_state.active_page == "📜 Project Archive":
    st.markdown("<h1>📜 Project Archive</h1>", unsafe_allow_html=True)
    st.markdown("<h5>Manage and load previously generated requirements documents</h5>", unsafe_allow_html=True)
    st.divider()
    
    # Load all items from SQLite
    brds = get_all_brds()
    
    if not brds:
        st.info("No projects saved in the archive database yet. Go to the generator and save a BRD.")
    else:
        # Search & Filter
        search_query = st.text_input("🔍 Search project archive by name", "")
        
        # Filter table
        filtered_brds = []
        for b in brds:
            if not search_query.strip() or search_query.lower() in b["project_name"].lower():
                filtered_brds.append(b)
                
        if not filtered_brds:
            st.warning("No projects matched your search criteria.")
        else:
            # Build list
            for b in filtered_brds:
                # Format dates nicely
                dt_obj = b.get("created_at", "")
                try:
                    # ISO string to nice representation
                    dt_str = pd.to_datetime(dt_obj).strftime("%B %d, %Y at %I:%M %p")
                except Exception:
                    dt_str = dt_obj
                    
                card_title = b.get("project_name", "Untitled")
                domain = b.get("domain", "General")
                
                with st.container():
                    col_card, col_actions = st.columns([4, 1])
                    
                    with col_card:
                        st.markdown(f"""
                        <div class='card-container'>
                          <h4>📁 {card_title}</h4>
                          <p style='margin-bottom: 2px;'><b>Domain:</b> {domain} | <b>Total Requirements:</b> {b.get('total_requirements')} | <b>Conflicts:</b> {b.get('conflict_count')}</p>
                          <p style='font-size: 0.8rem; color: #888; margin-bottom: 0px;'>Saved on: {dt_str}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_actions:
                        st.markdown("<br/>", unsafe_allow_html=True)
                        # Load and delete buttons per row
                        load_btn = st.button("📂 Load Visualizer", key=f"load_btn_{b['id']}")
                        delete_btn = st.button("🗑️ Delete Project", key=f"delete_btn_{b['id']}", type="secondary")
                        
                        if load_btn:
                            with st.spinner("Loading project details..."):
                                detail = get_brd_by_id(b["id"])
                                if detail:
                                    st.session_state.brd_data = json.loads(detail["brd_json"])
                                    st.session_state.current_project = detail["project_name"]
                                    st.session_state.selected_domain = detail["domain"]
                                    st.session_state.project_id = detail["id"]
                                    st.session_state.active_page = "📊 BRD Visualizer"
                                    st.success("Project loaded!")
                                    time.sleep(0.3)
                                    st.rerun()
                                    
                        if delete_btn:
                            with st.spinner("Deleting project..."):
                                delete_brd(b["id"])
                                st.success("Project deleted from archive!")
                                time.sleep(0.3)
                                st.rerun()
