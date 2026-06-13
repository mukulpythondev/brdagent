import logging
import google.generativeai as genai
import config

logger = logging.getLogger(__name__)

DOMAIN_METADATA = {
    "FinTech": {
        "compliance": ["PCI-DSS", "SOX", "AML/KYC guidelines"],
        "nfr_focus": "Transaction security, audit logging, multi-factor authentication, low-latency transaction processing",
        "glossary": ["SSO (Single Sign-On)", "KYC (Know Your Customer)", "MFA (Multi-Factor Authentication)", "GLBA (Gramm-Leach-Bliley Act)"]
    },
    "HealthTech": {
        "compliance": ["HIPAA Compliance", "HL7 Standards", "GDPR (Health Data Annex)"],
        "nfr_focus": "Patient data privacy, EHR integration stability, HIPAA-compliant audit trails, high system availability",
        "glossary": ["EHR (Electronic Health Record)", "HIPAA", "PHI (Protected Health Information)", "HL7"]
    },
    "E-Commerce": {
        "compliance": ["PCI-DSS", "GDPR (Consumer Data Privacy)"],
        "nfr_focus": "Cart checkout page load speed, concurrent shopping session scaling, database inventory consistency",
        "glossary": ["SKU (Stock Keeping Unit)", "Payment Gateway", "SSL Encryption", "SLA"]
    },
    "Enterprise": {
        "compliance": ["SOC 2 Type II", "ISO 27001"],
        "nfr_focus": "Single Sign-On integration, RBAC authorization matrices, historical activity logging, directory synching",
        "glossary": ["RBAC (Role-Based Access Control)", "SSO", "SAML (Security Assertion Markup Language)", "IAM"]
    },
    "Government": {
        "compliance": ["FedRAMP", "Section 508 Accessibility", "NIST SP 800-53"],
        "nfr_focus": "High encryption security, user accessibility (ADA compliance), federal cloud security standards",
        "glossary": ["FedRAMP", "Section 508", "FIPS (Federal Information Processing Standards)"]
    },
    "EdTech": {
        "compliance": ["FERPA", "COPPA compliance"],
        "nfr_focus": "Video/Content delivery scalability, student privacy protection, interactive classroom response latency",
        "glossary": ["LMS (Learning Management System)", "FERPA", "COPPA", "SCORM"]
    },
    "General": {
        "compliance": ["Standard Data Privacy Principles"],
        "nfr_focus": "Standard response times, system availability, backup restore loops",
        "glossary": ["BRD", "SME", "KPI"]
    }
}

def classify_domain(text: str) -> dict:
    """
    Classify project domain from input text.
    Returns classified domain name and domain-specific template adjustments.
    """
    domain = "General"
    
    # 1. Rule-based checks (works offline & inside demo mode)
    text_lower = text.lower()
    if any(k in text_lower for k in ["bank", "transaction", "fintech", "payment", "pci-dss", "balance", "credit", "ledger"]):
        domain = "FinTech"
    elif any(k in text_lower for k in ["health", "patient", "medical", "ehr", "hipaa", "clinic", "hospital"]):
        domain = "HealthTech"
    elif any(k in text_lower for k in ["cart", "shop", "checkout", "ecommerce", "payment gateway", "retail", "catalog", "sku"]):
        domain = "E-Commerce"
    elif any(k in text_lower for k in ["government", "federal", "municipal", "agency", "civic", "compliance regulation"]):
        domain = "Government"
    elif any(k in text_lower for k in ["student", "classroom", "school", "education", "course", "lms", "teacher", "learning"]):
        domain = "EdTech"
    elif any(k in text_lower for k in ["enterprise", "sso", "rbac", "soc 2", "directory", "hr system", "employee"]):
        domain = "Enterprise"
        
    # 2. Try Gemini classification if not in demo mode
    if config.AI_PROVIDER != "openai" and not config.DEMO_MODE and config.GEMINI_API_KEY:
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            prompt = f"""
            Analyze the text snippet below and determine which business domain it corresponds to.
            Choose exactly one of: FinTech, HealthTech, E-Commerce, Enterprise, Government, EdTech, General.
            
            Text Content:
            {text[:800]}
            
            Return ONLY the classified domain word. Do not add punctuation.
            """
            response = model.generate_content(
                prompt,
                request_options={"timeout": config.GEMINI_TIMEOUT_SECONDS},
            )
            classified = response.text.strip()
            if classified in DOMAIN_METADATA:
                domain = classified
        except Exception as e:
            logger.error(f"Failed LLM domain classification: {e}. Falling back to rule-based classification.")
            
    # Retrieve metadata based on domain
    metadata = DOMAIN_METADATA.get(domain, DOMAIN_METADATA["General"])
    
    return {
        "domain": domain,
        "compliance_standards": metadata["compliance"],
        "nfr_focus": metadata["nfr_focus"],
        "glossary": metadata["glossary"]
    }
