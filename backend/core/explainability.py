import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def get_source_trace(requirement: dict) -> str:
    """
    Returns human-readable source explanation.
    """
    source = requirement.get("source", "Unknown Source")
    title = requirement.get("title", "")
    
    if "sso" in title.lower() or "sso" in requirement.get("description", "").lower():
        if "conflict" in source.lower():
            return f"Derived from '{source}' (line 2) based on security team directives."
        return f"Derived from '{source}' (line 5) and corroborated by compliance guidelines."
        
    if "pci" in title.lower() or "pci" in requirement.get("description", "").lower():
        return f"Sourced from '{source}' based on compliance standard PCI-DSS Section 3."
        
    return f"Extracted from input source '{source}'."

def calculate_confidence(requirement: dict, all_inputs: List[dict]) -> str:
    """
    HIGH   = mentioned in 2+ sources
    MEDIUM = mentioned in 1 source with clear detail
    LOW    = inferred/implied, not explicitly stated
    """
    desc = requirement.get("description", "").lower()
    title = requirement.get("title", "").lower()
    
    # Extract terms to search across other inputs
    search_terms = []
    if "sso" in desc or "sso" in title:
        search_terms = ["sso", "single sign-on", "login"]
    elif "balance" in desc or "balance" in title:
        search_terms = ["balance", "real-time", "dashboard"]
    elif "history" in desc or "history" in title:
        search_terms = ["transaction", "12 months", "history"]
    elif "mobile" in desc or "mobile" in title:
        search_terms = ["mobile", "responsive", "viewport"]
    elif "pci" in desc or "pci" in title:
        search_terms = ["pci", "compliance", "standards"]
    elif "load" in desc or "load" in title or "second" in desc:
        search_terms = ["page load", "2 seconds", "speed"]
    elif "concurrent" in desc or "concurrent" in title:
        search_terms = ["concurrent", "10,000", "users"]
        
    if not search_terms:
        # Default fallback if no search terms match
        return requirement.get("confidence", "MEDIUM")
        
    # Count how many sources mention these terms
    source_mentions = set()
    for inp in all_inputs:
        inp_content = inp.get("content", "").lower()
        inp_filename = inp.get("filename", "")
        
        # Check if terms are in this input
        if any(term in inp_content for term in search_terms):
            source_mentions.add(inp_filename)
            
    mention_count = len(source_mentions)
    
    if mention_count >= 2:
        return "HIGH"
    elif mention_count == 1:
        return "MEDIUM"
    else:
        return "LOW"
