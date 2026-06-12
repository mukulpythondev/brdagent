import logging
import json
from typing import List, Dict, Any
from core.gemini_agent import GeminiAgent
from core.conflict_detector import detect_conflicts
from core.explainability import get_source_trace, calculate_confidence
from core.domain_classifier import classify_domain

logger = logging.getLogger(__name__)

def generate_brd(project_name: str, domain_selection: str, inputs: List[Dict[str, Any]]) -> dict:
    """
    Orchestrates the entire BRD generation pipeline:
    1. Parse and analyze each input individually.
    2. Auto-detect or override project domain.
    3. Synthesize the inputs using Gemini.
    4. Calculate requirements metadata (explainability & confidence).
    5. Detect requirement conflicts.
    6. Return a comprehensive structured BRD payload.
    """
    logger.info(f"Starting BRD generation pipeline for project '{project_name}'")
    
    agent = GeminiAgent()
    analyzed_inputs = []
    
    # 1. Analyze each input separately
    for inp in inputs:
        itype = inp.get("type")
        filename = inp.get("filename", "Input Source")
        content = inp.get("content", "")
        
        logger.info(f"Analyzing input: {filename} of type: {itype}")
        
        try:
            if itype == "image":
                analysis = agent.analyze_image(inp.get("bytes"), source_name=filename)
            elif itype == "pdf":
                analysis = agent.analyze_pdf(content, source_name=filename)
            else: # docx, txt, pasted text
                analysis = agent.analyze_text(content, source_name=filename)
                
            analyzed_inputs.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing input {filename}: {e}")
            # Add safe mock item
            analyzed_inputs.append({
                "source": filename,
                "requirements": [{"title": f"Extracted from {filename}", "description": content[:100], "type": "functional"}]
            })

    # 2. Domain classification
    combined_text = "\n".join([inp.get("content", "") for inp in inputs])
    domain_info = classify_domain(combined_text)
    
    selected_domain = domain_selection
    if domain_selection == "Auto-detect":
        selected_domain = domain_info.get("domain", "General")

    # 3. Master Synthesis
    logger.info("Running synthesis across all inputs...")
    brd_payload = agent.synthesize_all(analyzed_inputs, project_name=project_name, custom_domain=selected_domain)
    
    # Ensure domain is set correctly
    brd_payload["domain"] = selected_domain

    # 4. Explainability & Confidence Calculations
    logger.info("Computing source tracing and confidence metrics...")
    
    # Functional Requirements
    frs = brd_payload.get("functional_requirements", [])
    for fr in frs:
        # Calculate confidence
        fr["confidence"] = calculate_confidence(fr, inputs)
        # Get source trace explanation
        fr["source_trace"] = get_source_trace(fr)
        
    # Non-Functional Requirements
    nfrs = brd_payload.get("non_functional_requirements", [])
    for nfr in nfrs:
        nfr["confidence"] = calculate_confidence(nfr, inputs)
        nfr["source_trace"] = get_source_trace(nfr)

    # 5. Conflict Detection
    logger.info("Running conflict checks...")
    conflicts = detect_conflicts(frs)
    
    # Flag conflicts on the requirements
    for conf in conflicts:
        req1_id = conf.get("req1_id")
        req2_id = conf.get("req2_id")
        desc = conf.get("description")
        
        # Apply conflict notice to req1
        for fr in frs:
            if fr.get("id") == req1_id:
                fr["conflict"] = desc
            if fr.get("id") == req2_id:
                fr["conflict"] = desc

    # Store conflicts in main payload for UI visualization
    brd_payload["detected_conflicts"] = conflicts
    brd_payload["domain_adjustments"] = domain_info

    logger.info("BRD generation pipeline completed successfully.")
    return brd_payload
