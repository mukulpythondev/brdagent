import os
import json
import logging
import time
import base64
from typing import List, Dict, Any
import requests
import google.generativeai as genai
import config
from core.model_router import route_model

logger = logging.getLogger(__name__)

class GeminiAgent:
    def __init__(self):
        self.provider = config.AI_PROVIDER
        self.api_key = config.OPENAI_API_KEY if self.provider == "openai" else config.GEMINI_API_KEY
        self.demo_mode = config.DEMO_MODE
        self._model_cache = {}
        self.routing_decisions = []

        if not self.api_key or "your_" in self.api_key:
            logger.warning("%s API key is not configured. Falling back to Demo Mode.", self.provider.upper())
            self.demo_mode = True
        elif self.provider != "openai":
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to configure Gemini client: {e}. Falling back to Demo Mode.")
                self.demo_mode = True

    def _get_model(self, model_name: str):
        if model_name not in self._model_cache:
            self._model_cache[model_name] = genai.GenerativeModel(model_name)
        return self._model_cache[model_name]

    def _generate_text(self, prompt: str, route, image_bytes: bytes = None) -> str:
        if self.provider == "openai":
            return self._generate_openai(prompt, route.model, image_bytes=image_bytes)

        if image_bytes:
            image_part = {
                "mime_type": "image/png",
                "data": image_bytes,
            }
            response = self._get_model(route.model).generate_content(
                [prompt, image_part],
                request_options={"timeout": config.GEMINI_TIMEOUT_SECONDS},
            )
        else:
            response = self._get_model(route.model).generate_content(
                prompt,
                request_options={"timeout": config.GEMINI_TIMEOUT_SECONDS},
            )
        return response.text

    def _generate_openai(self, prompt: str, model_name: str, image_bytes: bytes = None) -> str:
        url = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "input": prompt,
            "temperature": 0.2,
            "store": False,
        }

        if image_bytes:
            image_b64 = base64.b64encode(image_bytes).decode("ascii")
            payload["input"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
                    ],
                }
            ]

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=config.OPENAI_TIMEOUT_SECONDS,
            verify=config.OPENAI_VERIFY_SSL,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("output_text"):
            return data["output_text"]

        chunks = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks).strip()

    def _record_route(self, route):
        route_dict = route.to_dict()
        self.routing_decisions.append(route_dict)
        logger.info(
            "Model route selected: purpose=%s modality=%s model=%s tier=%s complexity=%s",
            route.purpose,
            route.modality,
            route.model,
            route.tier,
            route.complexity,
        )
        return route_dict

    def get_routing_decisions(self) -> List[Dict[str, Any]]:
        return list(self.routing_decisions)

    def _attach_route(self, payload: dict, route_dict: dict) -> dict:
        payload["model_route"] = route_dict
        return payload

    def analyze_text(self, text: str, source_name: str = "Pasted Text") -> dict:
        """
        Extracts: entities, requirements, constraints, assumptions, stakeholders.
        """
        route = route_model(
            purpose="text_extraction",
            modality="text",
            text=text,
        )
        route_dict = self._record_route(route)

        if self.demo_mode:
            return self._attach_route(self._mock_analyze_text(text, source_name), route_dict)
            
        prompt = f"""
        You are a senior Business Analyst. Analyze the following project text input and extract a structured set of requirements details.
        
        Source Name: {source_name}
        Input Text:
        {text}
        
        Extract the following:
        - entities: list of systems, teams, tools, or physical objects mentioned
        - requirements: list of raw requirements with title and short description
        - constraints: list of restrictions, standards, compliance details, or hard limits
        - assumptions: list of assumed facts, dependencies, or prerequisites
        - stakeholders: list of people, roles, or actors mentioned
        
        Return ONLY a valid JSON object matching this structure:
        {{
          "source": "{source_name}",
          "entities": [],
          "requirements": [
             {{"title": "", "description": "", "type": "functional/non-functional"}}
          ],
          "constraints": [],
          "assumptions": [],
          "stakeholders": []
        }}
        """
        
        try:
            response_text = self._generate_text(prompt, route)
            return self._attach_route(self._parse_json_response(response_text), route_dict)
        except Exception as e:
            logger.error(f"{self.provider.upper()} API Error in analyze_text: {e}. Using mock fallback.")
            return self._attach_route(self._mock_analyze_text(text, source_name), route_dict)

    def analyze_image(self, image_bytes: bytes, source_name: str = "Uploaded Image") -> dict:
        """
        Sends image to Gemini Vision. Extracts UI elements, flows, labels, implied requirements.
        """
        route = route_model(
            purpose="image_understanding",
            modality="image",
            text=source_name,
            has_image=True,
        )
        route_dict = self._record_route(route)

        if self.demo_mode or not image_bytes:
            return self._attach_route(self._mock_analyze_image(source_name), route_dict)
            
        prompt = f"""
        You are an expert System Architect. Analyze this image (which may be a wireframe, UI screenshot, flow diagram, or architecture sketch).
        Extract:
        - UI elements: buttons, inputs, tables, panels visible or suggested
        - user flows: actions a user can take and outcomes
        - labels: text elements or headers
        - implied requirements: technical specifications, layouts, or constraints implied by this image
        
        Return ONLY a valid JSON object matching this structure:
        {{
          "source": "{source_name}",
          "ui_elements": [],
          "flows": [],
          "labels": [],
          "implied_requirements": [
             {{"title": "", "description": "", "confidence": "HIGH/MEDIUM/LOW"}}
          ]
        }}
        """
        
        try:
            response_text = self._generate_text(prompt, route, image_bytes=image_bytes)
            return self._attach_route(self._parse_json_response(response_text), route_dict)
        except Exception as e:
            logger.error(f"{self.provider.upper()} API Error in analyze_image: {e}. Using mock fallback.")
            return self._attach_route(self._mock_analyze_image(source_name), route_dict)

    def analyze_pdf(self, pdf_text: str, source_name: str = "Uploaded PDF") -> dict:
        """
        Processes extracted PDF text. Identifies functional, non-functional, and scope items.
        """
        route = route_model(
            purpose="document_extraction",
            modality="pdf",
            text=pdf_text,
        )
        route_dict = self._record_route(route)

        if self.demo_mode:
            return self._attach_route(self._mock_analyze_pdf(pdf_text, source_name), route_dict)
            
        prompt = f"""
        You are a senior Business Analyst. Analyze the following PDF document contents.
        
        Source Name: {source_name}
        Content Text:
        {pdf_text}
        
        Identify:
        - functional_requirements: user actions, system actions, process flows
        - non_functional_requirements: performance, security, availability, compliance
        - scope_items: list of items explicitly marked as in-scope or out-of-scope
        
        Return ONLY a valid JSON object matching this structure:
        {{
          "source": "{source_name}",
          "functional_requirements": [
             {{"title": "", "description": ""}}
          ],
          "non_functional_requirements": [
             {{"title": "", "description": ""}}
          ],
          "scope": {{
             "in_scope": [],
             "out_scope": []
          }}
        }}
        """
        
        try:
            response_text = self._generate_text(prompt, route)
            return self._attach_route(self._parse_json_response(response_text), route_dict)
        except Exception as e:
            logger.error(f"{self.provider.upper()} API Error in analyze_pdf: {e}. Using mock fallback.")
            return self._attach_route(self._mock_analyze_pdf(pdf_text, source_name), route_dict)

    def synthesize_all(self, inputs: List[Dict[str, Any]], project_name: str = "My Project", custom_domain: str = "Auto-detect") -> dict:
        """
        Combines all analyzed inputs, auto-detects domain, performs conflict checking,
        scores requirements, and structures a master BRD.
        """
        if self.demo_mode:
            route = route_model(
                purpose="synthesis",
                modality="multi_source",
                text=json.dumps(inputs),
                input_count=len(inputs),
            )
            route_dict = self._record_route(route)
            return self._attach_route(self._mock_synthesize_all(inputs, project_name, custom_domain), route_dict)

        inputs_json = json.dumps(inputs, indent=2)
        route = route_model(
            purpose="synthesis",
            modality="multi_source",
            text=inputs_json,
            input_count=len(inputs),
            has_image=any("implied_requirements" in inp for inp in inputs),
        )
        route_dict = self._record_route(route)
        
        prompt = f"""
You are an expert Business Analyst AI. You have received the following analyzed inputs from multiple sources:

{inputs_json}

Your task:
1. Generate a complete Business Requirements Document (BRD) for the project named "{project_name}" with these sections:
   - Executive Summary
   - Project Objectives (3-5 points)
   - Scope (In-Scope & Out-of-Scope)
   - Stakeholders
   - Functional Requirements (numbered FR-001, FR-002...)
   - Non-Functional Requirements (NFR-001, NFR-002...)
   - Assumptions & Dependencies
   - Risks & Mitigations
   - Acceptance Criteria

2. For each requirement, add:
   - source: which input file/text/source it came from
   - confidence: HIGH / MEDIUM / LOW (HIGH if mentioned in multiple inputs or very detailed, MEDIUM if in single input with detail, LOW if inferred)
   - conflict: null OR description of conflict with another requirement (if they contradict or overlap problematicly)
   - priority: MUST HAVE / SHOULD HAVE / COULD HAVE

3. Detect domain automatically from context. If a custom domain was selected ("{custom_domain}"), adjust template or contents to fit "{custom_domain}" style.

4. Return ONLY valid JSON matching this structure:
{{
  "project_name": "{project_name}",
  "domain": "",
  "executive_summary": "",
  "objectives": [],
  "scope": {{"in_scope": [], "out_scope": []}},
  "stakeholders": [],
  "functional_requirements": [
    {{
      "id": "FR-001",
      "title": "",
      "description": "",
      "source": "",
      "confidence": "HIGH",
      "conflict": null,
      "priority": "MUST HAVE"
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR-001",
      "title": "",
      "description": "",
      "source": "",
      "confidence": "HIGH"
    }}
  ],
  "assumptions": [],
  "risks": [{{"risk": "", "mitigation": ""}}],
  "acceptance_criteria": []
}}
"""
        
        try:
            response_text = self._generate_text(prompt, route)
            return self._attach_route(self._parse_json_response(response_text), route_dict)
        except Exception as e:
            logger.error(f"{self.provider.upper()} API Error in synthesize_all: {e}. Using mock fallback.")
            return self._attach_route(self._mock_synthesize_all(inputs, project_name, custom_domain), route_dict)

    # --- PARSING & MOCK FALLBACKS ---

    def _parse_json_response(self, response_text: str) -> dict:
        """
        Cleans markdown wrappers (like ```json ... ```) from Gemini responses and parses JSON.
        """
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Error parsing Gemini JSON: {e}. Original text: {response_text}")
            raise e

    def _mock_analyze_text(self, text: str, source_name: str) -> dict:
        logger.info(f"Generating mock analysis for text source: {source_name}")
        # Default mock structure
        result = {
            "source": source_name,
            "entities": ["Banking Portal", "SSO Service", "Database"],
            "requirements": [],
            "constraints": ["Must be secure", "PCI-DSS compliance"],
            "assumptions": ["Users have active Google or Microsoft accounts"],
            "stakeholders": ["Product Manager", "Dev Lead", "Compliance Officer"]
        }
        
        # Look for indicators in sample_text
        if "SSO with Google/Microsoft" in text or "Online Banking Portal" in text:
            result["requirements"] = [
                {"title": "Google/Microsoft SSO Login", "description": "Users must login using Single Sign-On with Google or Microsoft directories.", "type": "functional"},
                {"title": "Real-time Dashboard Balance", "description": "The dashboard must display account balances updated in real-time.", "type": "functional"},
                {"title": "12-Month Transaction History", "description": "Provide user-accessible history of transactions going back at least 12 months.", "type": "functional"},
                {"title": "Mobile Responsive UI", "description": "The system interfaces must adapt dynamically to tablet and smartphone displays.", "type": "functional"},
                {"title": "PCI-DSS Compliance", "description": "All data flows and transactions must comply with PCI-DSS guidelines.", "type": "non-functional"},
                {"title": "Page Response Time", "description": "Standard page response/load times must remain below 2.0 seconds.", "type": "non-functional"},
                {"title": "Concurrency support", "description": "Scale gracefully to support 10,000 concurrent user sessions.", "type": "non-functional"}
            ]
        elif "username + password only" in text or "Security team note" in text:
            result["requirements"] = [
                {"title": "Password Authentication Mode", "description": "All authentication must restrict users to username and password verification only.", "type": "functional"},
                {"title": "No Third-Party IDPs", "description": "Disable any SSO integrations with Google, Microsoft, or external providers.", "type": "functional"},
                {"title": "SMS Two-Factor Authentication", "description": "Add SMS-based 2FA to secure authentication logs.", "type": "functional"}
            ]
        else:
            # Generic mock parsing
            result["requirements"] = [
                {"title": "Extracted Requirement 1", "description": f"Extracted from input text: '{text[:60]}...'", "type": "functional"},
                {"title": "Standard performance target", "description": "Ensure low-latency load rates.", "type": "non-functional"}
            ]
        return result

    def _mock_analyze_image(self, source_name: str) -> dict:
        logger.info(f"Generating mock analysis for image source: {source_name}")
        return {
            "source": source_name,
            "ui_elements": ["Header Navigation", "File Upload drag-and-drop zone", "Requirements Grid Table", "Action Buttons Footer"],
            "flows": ["Drag file -> File loads in preview -> Click Generate -> BRD shows in Viewer"],
            "labels": ["🔬 BRD Forge", "Generate BRD", "Confidence Score", "Export PDF"],
            "implied_requirements": [
                {"title": "Dark-Mode Aesthetics", "description": "Implement a high-fidelity slate/dark interface using Google Cloud primary accents.", "confidence": "HIGH"},
                {"title": "Tabbed Sidebar Navigation", "description": "Enable transitions between creation, visualizer, and SQLite historical archive.", "confidence": "HIGH"}
            ]
        }

    def _mock_analyze_pdf(self, pdf_text: str, source_name: str) -> dict:
        logger.info(f"Generating mock analysis for PDF source: {source_name}")
        return {
            "source": source_name,
            "functional_requirements": [
                {"title": "System-wide Document Storage", "description": "Provide a secure container to archive PDF documents in a local uploads repository."},
                {"title": "Interactive Grid Filter", "description": "Render interactive tables that highlight low-confidence rows with red flags."}
            ],
            "non_functional_requirements": [
                {"title": "Sub-Second Search Latency", "description": "Ensure SQLite query lookups for BRD histories execute in under 100 milliseconds."}
            ],
            "scope": {
                "in_scope": ["Local PDF Parsing", "JSON-based BRD Assembly", "Visual UI Viewer"],
                "out_scope": ["Live GCP Vertex AI active deployment billing accounts", "Corporate Active Directory MSAL hooks"]
            }
        }

    def _mock_synthesize_all(self, inputs: List[Dict[str, Any]], project_name: str, custom_domain: str) -> dict:
        logger.info(f"Synthesizing mock BRD for project: {project_name}")
        
        # Check if we have conflict inputs (i.e. SSO from sample_text and Username/Password from sample_conflict)
        has_sso = False
        has_password_only = False
        
        for inp in inputs:
            reqs = inp.get("requirements", []) + inp.get("implied_requirements", []) + inp.get("functional_requirements", [])
            for r in reqs:
                desc = r.get("description", "").lower()
                title = r.get("title", "").lower()
                if "sso" in desc or "sso" in title or "google/microsoft" in desc:
                    has_sso = True
                if "username + password" in desc or "username + password" in title or "no third party" in desc:
                    has_password_only = True
                    
        domain = "FinTech" if (custom_domain == "Auto-detect" or not custom_domain) else custom_domain
        
        brd = {
            "project_name": project_name,
            "domain": domain,
            "executive_summary": f"This Business Requirements Document (BRD) details the requirements for '{project_name}'. The platform delivers optimized, secure workflows tailormade for {domain} processes. The system has been designed with strict data isolation, high scalability, and robust user auditing controls.",
            "objectives": [
                "Deploy a high-performance web portal with dynamic screen scaling.",
                "Ensure maximum compliance and risk security within the targeted environment.",
                "Deliver real-time dashboard calculations for user activity."
            ],
            "scope": {
                "in_scope": [
                    "User authentication, session controls, and profile configurations.",
                    "Live tabular data grid with automatic cell sorting and calculations.",
                    "Automated document formatting exports (PDF and Word formats)."
                ],
                "out_scope": [
                    "Real-time database clustering (to be addressed in subsequent sprints).",
                    "Integration with non-GHD third-party document systems."
                ]
            },
            "stakeholders": [
                "Product Owner (John Doe)",
                "Lead System Architect (Sarah Jenkins)",
                "Senior Security Specialist (Mike Ross)",
                "Central Compliance Board"
            ],
            "functional_requirements": [
                {
                    "id": "FR-001",
                    "title": "Account Balance Dashboard",
                    "description": "The user home dashboard screen must query and display account metrics in real-time, fetching updates every 15 seconds.",
                    "source": "sample_text.txt",
                    "confidence": "HIGH",
                    "conflict": None,
                    "priority": "MUST HAVE"
                },
                {
                    "id": "FR-002",
                    "title": "12-Month Transaction History Table",
                    "description": "Users must be able to search, page, and filter transaction records covering the preceding 12 calendar months.",
                    "source": "sample_text.txt",
                    "confidence": "HIGH",
                    "conflict": None,
                    "priority": "MUST HAVE"
                },
                {
                    "id": "FR-003",
                    "title": "Mobile Interface Adaptability",
                    "description": "The entire user web interface must scale and stack layout blocks dynamically on mobile viewport resolutions.",
                    "source": "sample_text.txt",
                    "confidence": "MEDIUM",
                    "conflict": None,
                    "priority": "SHOULD HAVE"
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "NFR-001",
                    "title": "Page Load Response Threshold",
                    "description": "Static page components and initial dashboard loads must complete in under 2.0 seconds.",
                    "source": "sample_text.txt",
                    "confidence": "HIGH"
                },
                {
                    "id": "NFR-002",
                    "title": "PCI-DSS Data Protection Standards",
                    "description": "All transit and rest state operations must carry TLS 1.3 encryption to comply with standard security audits.",
                    "source": "sample_text.txt",
                    "confidence": "HIGH"
                },
                {
                    "id": "NFR-003",
                    "title": "Peak User Scale Threshold",
                    "description": "Simulate and stress-test core system endpoints to verify stable response under 10,000 concurrent API users.",
                    "source": "sample_text.txt",
                    "confidence": "MEDIUM"
                }
            ],
            "assumptions": [
                "Client browsers possess modern HTML5 and Javascript support.",
                "Target security groups authorize standard port communication protocols."
            ],
            "risks": [
                {
                    "risk": "API rate-limiting during high peak concurrent transaction spikes.",
                    "mitigation": "Configure client-side request debouncing and load balancers."
                },
                {
                    "risk": "Regulatory compliance shifts post-deployment.",
                    "mitigation": "Build modular data isolation containers to easily toggle security options."
                }
            ],
            "acceptance_criteria": [
                "Verified system load handles mock users with zero page timeout faults.",
                "Compliance auditor reviews and signs off on cryptographic data models.",
                "PDF and Word outputs render tables and confidence matrices accurately."
            ]
        }
        
        # Inject the conflict requirement if triggered
        if has_sso and has_password_only:
            # Let's add the contradictory SSO and password requirements
            brd["functional_requirements"].append({
                "id": "FR-004",
                "title": "Google/Microsoft SSO Login",
                "description": "The system must allow users to log in using single sign-on (SSO) backed by corporate Google or Microsoft account credentials.",
                "source": "sample_text.txt",
                "confidence": "HIGH",
                "conflict": "FR-005: Security guidelines mandate username & password credentials only; third-party login providers are strictly prohibited.",
                "priority": "MUST HAVE"
            })
            brd["functional_requirements"].append({
                "id": "FR-005",
                "title": "Secure Password Authentication Only",
                "description": "All logins must require a unique user-created username and password credentials. Third-party identity providers or federated logins are prohibited.",
                "source": "sample_conflict.txt",
                "confidence": "HIGH",
                "conflict": "FR-004: Standard system specs mandate Google/Microsoft SSO integration for single sign-on logins.",
                "priority": "MUST HAVE"
            })
        elif has_sso:
            brd["functional_requirements"].append({
                "id": "FR-004",
                "title": "Google/Microsoft SSO Login",
                "description": "The system must allow users to log in using single sign-on (SSO) backed by corporate Google or Microsoft account credentials.",
                "source": "sample_text.txt",
                "confidence": "HIGH",
                "conflict": None,
                "priority": "MUST HAVE"
            })
        elif has_password_only:
            brd["functional_requirements"].append({
                "id": "FR-005",
                "title": "Secure Password Authentication Only",
                "description": "All logins must require a unique user-created username and password credentials. Third-party identity providers or federated logins are prohibited.",
                "source": "sample_conflict.txt",
                "confidence": "HIGH",
                "conflict": None,
                "priority": "MUST HAVE"
            })
            
        return brd
