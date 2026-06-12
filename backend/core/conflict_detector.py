import os
import json
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def detect_conflicts(requirements: List[Dict[str, Any]], use_ai: bool = True) -> List[Dict[str, Any]]:
    """
    Multi-layer conflict detection pipeline:
    1. Fast rule-based heuristic checks (always runs, instant).
    2. Gemini Semantic Analysis (if API key is configured and use_ai=True).
    
    Returns a list of conflict objects with unique IDs.
    """
    conflicts = []
    seen_pairs = set()

    # ===== LAYER 1: Rule-Based Heuristic Checks (Always Active) =====
    rule_conflicts = _detect_rule_based(requirements)
    for c in rule_conflicts:
        pair_key = tuple(sorted([c["req1_id"], c["req2_id"]]))
        if pair_key not in seen_pairs:
            c["id"] = f"CONFLICT-{str(uuid.uuid4())[:8].upper()}"
            c["detection_method"] = "rule_based"
            conflicts.append(c)
            seen_pairs.add(pair_key)

    # ===== LAYER 2: Gemini Semantic Analysis (If API Key Available) =====
    if use_ai and len(requirements) > 1:
        try:
            ai_conflicts = _detect_gemini_semantic(requirements)
            for c in ai_conflicts:
                pair_key = tuple(sorted([c["req1_id"], c["req2_id"]]))
                if pair_key not in seen_pairs:
                    c["id"] = f"CONFLICT-{str(uuid.uuid4())[:8].upper()}"
                    c["detection_method"] = "gemini_semantic"
                    conflicts.append(c)
                    seen_pairs.add(pair_key)
        except Exception as e:
            logger.warning(f"Gemini semantic analysis skipped: {e}")

    return conflicts


def _detect_rule_based(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rule-based heuristic conflict detection.
    Extremely fast, zero API cost, perfect for demo mode.
    """
    conflicts = []

    for i in range(len(requirements)):
        for j in range(i + 1, len(requirements)):
            req1 = requirements[i]
            req2 = requirements[j]

            id1, desc1 = req1.get("id", ""), req1.get("description", "").lower()
            id2, desc2 = req2.get("id", ""), req2.get("description", "").lower()
            t1, t2 = req1.get("title", "").lower(), req2.get("title", "").lower()

            # Case A: SSO vs Username/Password Only
            sso_keywords = ["sso", "single sign-on", "federated", "google or microsoft", "identity provider"]
            pwd_only_keywords = ["username & password", "username + password", "no third party", "credentials only", "password authentication"]

            is_req1_sso = any(k in desc1 or k in t1 for k in sso_keywords)
            is_req2_pwd = any(k in desc2 or k in t2 for k in pwd_only_keywords)
            is_req1_pwd = any(k in desc1 or k in t1 for k in pwd_only_keywords)
            is_req2_sso = any(k in desc2 or k in t2 for k in sso_keywords)

            if (is_req1_sso and is_req2_pwd) or (is_req1_pwd and is_req2_sso):
                conflicts.append({
                    "req1_id": id1,
                    "req2_id": id2,
                    "description": (
                        f"Authentication mismatch: '{req1.get('title')}' specifies SSO integration, "
                        f"whereas '{req2.get('title')}' mandates username/password credentials with NO third-party providers."
                    ),
                    "severity": "HIGH"
                })

            # Case B: Offline storage vs Online only
            offline_k = ["offline mode", "local storage", "offline operation"]
            online_k = ["live sync", "real-time cloud syncing", "always online", "no offline caching"]

            is_req1_off = any(k in desc1 or k in t1 for k in offline_k)
            is_req2_on = any(k in desc2 or k in t2 for k in online_k)
            is_req1_on = any(k in desc1 or k in t1 for k in online_k)
            is_req2_off = any(k in desc2 or k in t2 for k in offline_k)

            if (is_req1_off and is_req2_on) or (is_req1_on and is_req2_off):
                conflicts.append({
                    "req1_id": id1,
                    "req2_id": id2,
                    "description": (
                        f"Storage policy clash: '{req1.get('title')}' requires offline database support, "
                        f"while '{req2.get('title')}' specifies strict real-time cloud sync with no local copies."
                    ),
                    "severity": "HIGH"
                })

            # Case C: Data retention vs GDPR deletion
            retention_k = ["retain data", "keep records", "data retention", "archive", "permanent storage"]
            deletion_k = ["right to be forgotten", "gdpr deletion", "data erasure", "purge user data", "delete on request"]

            is_req1_ret = any(k in desc1 or k in t1 for k in retention_k)
            is_req2_del = any(k in desc2 or k in t2 for k in deletion_k)
            is_req1_del = any(k in desc1 or k in t1 for k in deletion_k)
            is_req2_ret = any(k in desc2 or k in t2 for k in retention_k)

            if (is_req1_ret and is_req2_del) or (is_req1_del and is_req2_ret):
                conflicts.append({
                    "req1_id": id1,
                    "req2_id": id2,
                    "description": (
                        f"Data policy conflict: '{req1.get('title')}' mandates long-term data retention, "
                        f"while '{req2.get('title')}' requires GDPR-compliant data deletion on request."
                    ),
                    "severity": "HIGH"
                })

    return conflicts


def _detect_gemini_semantic(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Uses Gemini LLM to perform deep semantic conflict analysis.
    Analyzes requirement pairs for logical contradictions that rule-based checks miss.
    Only runs if GEMINI_API_KEY is configured.
    """
    import config
    api_key = config.GEMINI_API_KEY

    if not api_key:
        logger.info("Gemini API key not configured. Skipping semantic conflict analysis.")
        return []

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    except ImportError:
        logger.warning("google-generativeai not installed. Skipping semantic analysis.")
        return []

    # Format requirements for the prompt
    req_text = ""
    for r in requirements:
        req_text += f"- [{r.get('id')}] {r.get('title')}: {r.get('description')}\n"

    prompt = f"""You are an expert Business Analyst AI. Analyze the following business requirements and identify ANY logical contradictions, conflicts, or inconsistencies between them.

**Requirements:**
{req_text}

**Instructions:**
- Only report REAL conflicts where two requirements logically contradict each other.
- Do NOT report minor overlaps or complementary features as conflicts.
- For each conflict, explain WHY they contradict.

**Response Format** (respond in valid JSON array only, or empty array [] if no conflicts):
[
  {{
    "req1_id": "<ID of first conflicting requirement>",
    "req2_id": "<ID of second conflicting requirement>",
    "description": "<Clear explanation of why these requirements conflict>",
    "severity": "HIGH | MEDIUM | LOW"
  }}
]
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean markdown code fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        parsed = json.loads(response_text.strip())
        if isinstance(parsed, list):
            logger.info(f"Gemini semantic analysis found {len(parsed)} additional conflicts.")
            return parsed
        return []
    except json.JSONDecodeError:
        logger.warning("Failed to parse Gemini semantic conflict response as JSON.")
        return []
    except Exception as e:
        logger.warning(f"Gemini semantic conflict analysis error: {e}")
        return []
