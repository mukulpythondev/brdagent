# High-Impact Demo Input Pack

Use these three files together in the Upload & Ingest page:

1. `high_impact_paste_text.txt`
   Paste this into the raw text box.

2. `securepay_stakeholder_memo.docx`
   Upload this as the stakeholder document.

3. `securepay_lending_wireframe.png`
   Upload this as the image/wireframe input.

## What This Demo Proves

This pack is designed to show the problem statement clearly:

- Multimodal: text + DOCX + image/wireframe.
- Fragmented: product, risk, operations, legal, and compliance notes are split across sources.
- Context-aware: FinTech lending domain with KYC, audit logs, risk approval, and encryption.
- Conflict detection: product asks for SSO, risk asks for username/password + SMS only.
- Explainability: generated requirements should show source trace, confidence, priority, and conflicts.
- Scalability: the model router should use fast extraction for simple text and advanced/multimodal reasoning for synthesis and image understanding.

## Expected Strong Output

The generated BRD should include:

- Executive summary for an SME lending portal.
- Objectives around faster loan processing, secure document handling, and internal review workflows.
- Functional requirements for login, KYC upload, document validation, review queue, sanction letter generation, notifications, and exports.
- Non-functional requirements for availability, encryption, audit retention, search latency, and role-based access.
- Risk items for sensitive data handling, policy conflict, approval bypass, and compliance gaps.
- Acceptance criteria blocking sanction letters until mandatory checks are complete.
- A detected conflict between SSO and password-only authentication.
- AI routing decisions showing why text/image/synthesis used different model tiers.

## Prompt Quality Story For Pitch

Our generation prompt is not a generic "summarize this" prompt.

It is optimized around four controls:

1. Schema control:
   The model is instructed to return only valid JSON with fixed BRD sections. This reduces frontend parsing errors and makes export reliable.

2. Token optimization:
   The pipeline first analyzes each input separately, then sends compact extracted signals into final synthesis. This avoids repeatedly sending full raw files into every step.

3. Routing optimization:
   The model router estimates tokens, checks modality, counts input sources, and scans risk/compliance terms. Simple extraction can use a fast model, while image understanding, long documents, conflict reasoning, and final synthesis use advanced models.

4. Quality guardrails:
   The prompt asks for source, confidence, priority, conflicts, risks, assumptions, and acceptance criteria. This makes the output explainable and reviewable by a team lead.

## How To Explain Scalability

Say this:

"Scalability here is not only server scaling. It is AI cost and latency scaling. If we send every request to the largest model, the system becomes expensive and slow. Our router estimates token length, checks risk terms like compliance and audit, detects image inputs, and chooses the right model tier. That means small tasks stay fast, while complex multimodal reasoning gets the stronger model."

## Generation Improvements We Can Add

Good near-term improvements:

1. Web/RAG research mode:
   Add an optional research toggle that retrieves domain rules or compliance references before BRD generation. For example, FinTech could retrieve KYC, PCI-DSS, AML, or data-retention references.

2. Vertex AI Search / Enterprise Search:
   Instead of open internet search, connect company policy documents and previous BRDs to a private retrieval index. This is safer for enterprise demos.

3. BigQuery analytics feedback:
   Store generated requirement quality metrics, conflict rates, model usage, and domain patterns in BigQuery. Use this to show leadership dashboards.

4. Prompt versioning:
   Store prompt template version, model name, route reason, token estimate, and output score for every generation. This helps debugging and governance.

5. Requirement quality scoring:
   Add checks for ambiguity, missing actor, missing measurable acceptance criterion, and unverifiable wording.

6. Human review workflow:
   Add approve/reject/comment status for each requirement, with team lead sign-off before export.

7. Grounded citations:
   For uploaded documents, show exact source file and text snippet. For web/RAG mode, show retrieved source title and policy section.

## Should We Add Web Search?

Yes, but as an optional "Research Assist" mode, not always-on.

Why optional:

- Always-on web search can add latency.
- Public web results can be noisy.
- Some enterprise requirements should only use private documents.

Best approach:

- Default mode: use uploaded inputs only for deterministic BRD generation.
- Research mode: retrieve trusted sources, summarize them into compact notes, then pass only those notes into BRD synthesis.
- Enterprise mode: use Vertex AI Search or a private RAG index over company policies and previous BRDs.

