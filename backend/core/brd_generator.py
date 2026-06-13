import logging
import json
import uuid
from typing import List, Dict, Any
from core.gemini_agent import GeminiAgent
from core.conflict_detector import detect_conflicts
from core.explainability import get_source_trace, calculate_confidence
from core.domain_classifier import classify_domain
from core.model_router import summarize_routes
import config

logger = logging.getLogger(__name__)

def _first_present(data: Dict[str, Any], keys: List[str], default=None):
    for key in keys:
        if key in data and data.get(key) not in (None, ""):
            return data.get(key)
    return default

def _as_list(value) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [line.strip(" -\t") for line in value.splitlines() if line.strip()]
    return [value]

def _normalize_requirement(item, prefix: str, index: int, req_type: str) -> Dict[str, Any]:
    if isinstance(item, str):
        item = {"title": item, "description": item}
    elif not isinstance(item, dict):
        item = {"title": f"{req_type.title()} Requirement {index}", "description": str(item)}

    req_id = _first_present(item, ["id", "req_id", "requirement_id", "requirementId"])
    title = _first_present(item, ["title", "name", "requirement"], f"{req_type.title()} Requirement {index}")
    description = _first_present(
        item,
        ["description", "details", "detail", "requirement_text", "requirementText", "requirement"],
        title,
    )

    return {
        **item,
        "id": req_id or f"{prefix}-{index:03d}",
        "title": title,
        "description": description,
        "source": _first_present(item, ["source", "source_file", "sourceFile"], "AI synthesis"),
        "confidence": str(_first_present(item, ["confidence"], "MEDIUM")).upper(),
        "conflict": item.get("conflict"),
        "priority": str(_first_present(item, ["priority"], "SHOULD HAVE")).upper(),
    }

def _normalize_risk(item) -> Dict[str, str]:
    if isinstance(item, str):
        return {"risk": item, "mitigation": "Review and validate during solution design."}
    if not isinstance(item, dict):
        return {"risk": str(item), "mitigation": "Review and validate during solution design."}
    return {
        "risk": _first_present(item, ["risk", "title", "description", "issue"], "Unspecified risk"),
        "mitigation": _first_present(item, ["mitigation", "mitigation_plan", "mitigationPlan", "response"], "Review and validate during solution design."),
    }

def normalize_brd_payload(payload: Dict[str, Any], project_name: str, selected_domain: str) -> Dict[str, Any]:
    """
    Normalizes model JSON into the exact contract consumed by the visualizer/exporters.
    OpenAI/Gemini may obey the prompt semantically while varying field names.
    """
    if not isinstance(payload, dict):
        payload = {}

    scope = payload.get("scope") if isinstance(payload.get("scope"), dict) else {}
    functional = _first_present(
        payload,
        ["functional_requirements", "functionalRequirements", "functional", "requirements", "features"],
        [],
    )
    non_functional = _first_present(
        payload,
        ["non_functional_requirements", "nonFunctionalRequirements", "non_functional", "nfrs", "quality_requirements"],
        [],
    )

    normalized = {
        **payload,
        "project_name": _first_present(payload, ["project_name", "projectName", "name"], project_name),
        "domain": _first_present(payload, ["domain", "industry"], selected_domain),
        "executive_summary": _first_present(payload, ["executive_summary", "executiveSummary", "summary", "overview"], ""),
        "objectives": _as_list(_first_present(payload, ["objectives", "project_objectives", "projectObjectives", "goals"], [])),
        "scope": {
            "in_scope": _as_list(_first_present(scope, ["in_scope", "inScope", "in", "included"], [])),
            "out_scope": _as_list(_first_present(scope, ["out_scope", "outScope", "out", "excluded"], [])),
        },
        "stakeholders": _as_list(_first_present(payload, ["stakeholders", "actors", "users"], [])),
        "functional_requirements": [
            _normalize_requirement(item, "FR", idx, "functional")
            for idx, item in enumerate(_as_list(functional), start=1)
        ],
        "non_functional_requirements": [
            _normalize_requirement(item, "NFR", idx, "non-functional")
            for idx, item in enumerate(_as_list(non_functional), start=1)
        ],
        "assumptions": _as_list(_first_present(payload, ["assumptions", "dependencies", "assumptions_dependencies", "assumptionsAndDependencies"], [])),
        "risks": [
            _normalize_risk(item)
            for item in _as_list(_first_present(payload, ["risks", "risksAndMitigations", "risks_mitigations", "risk_mitigations"], []))
        ],
        "acceptance_criteria": _as_list(_first_present(payload, ["acceptance_criteria", "acceptanceCriteria", "success_criteria", "successCriteria"], [])),
    }

    if not normalized["executive_summary"]:
        normalized["executive_summary"] = f"BRD generated for {project_name} from the submitted multimodal inputs."

    return normalized

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
    brd_payload = normalize_brd_payload(brd_payload, project_name, selected_domain)
    
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
    conflicts = detect_conflicts(frs, use_ai=not agent.demo_mode)

    # Normalize model-provided inline conflicts into the structured conflict drawer.
    existing_conflict_ids = {
        item
        for conf in conflicts
        for item in (conf.get("req1_id"), conf.get("req2_id"))
        if item
    }
    for fr in frs:
        inline_conflict = fr.get("conflict")
        if inline_conflict and fr.get("id") not in existing_conflict_ids:
            conflicts.append({
                "id": f"CONFLICT-{str(uuid.uuid4())[:8].upper()}",
                "req1_id": fr.get("id"),
                "req2_id": "AI-INFERRED",
                "description": inline_conflict,
                "severity": "MEDIUM",
                "detection_method": "model_inline",
            })
            existing_conflict_ids.add(fr.get("id"))
    
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
    routing_decisions = agent.get_routing_decisions()
    conflict_routes = [
        conf.get("model_route")
        for conf in conflicts
        if conf.get("model_route")
    ]
    all_routes = routing_decisions + conflict_routes
    ai_runtime = "OpenAI Responses API with adaptive model routing"
    if config.AI_PROVIDER != "openai":
        ai_runtime = "Vertex AI / Gemini with SDK fallback"
    brd_payload["model_routing_decisions"] = all_routes
    brd_payload["ai_architecture"] = {
        **summarize_routes(all_routes),
        "input_modalities": sorted({inp.get("type", "text") for inp in inputs}),
        "input_count": len(inputs),
        "cloud_services": {
            "ai_runtime": ai_runtime,
            "file_storage": "Google Cloud Storage with local filesystem fallback",
            "analytics_storage": "BigQuery with Firestore/SQLite fallback",
            "explainability": "Source trace, confidence scoring, conflict reasons, and model route reasons",
        },
    }

    logger.info("BRD generation pipeline completed successfully.")
    return brd_payload
