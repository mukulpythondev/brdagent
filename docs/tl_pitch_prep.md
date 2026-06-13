# BRD Forge TL Pitch Prep

## One-Line Project Understanding

BRD Forge is a scalable, multimodal AI system that converts fragmented business inputs such as text notes, images, wireframes, and documents into a structured, explainable Business Requirements Document with confidence scores, source tracing, conflict detection, and adaptive model routing.

## Problem Statement Breakdown

Original idea:

Build a scalable, multi-modal AI system using Google Gemini AI and integrated cloud tools that can process real-time, fragmented data and deliver accurate, context-aware, explainable decisions in complex and dynamic environments.

How we map it:

| Keyword | What It Means | What We Show In Our System |
|---|---|---|
| Scalable | Can handle small and large inputs without same-cost processing | Adaptive model router selects fast or advanced model based on input length, modality, and risk |
| Multimodal | Understands more than plain text | Accepts pasted text, `.txt`, PDFs/docs, and images/wireframes |
| Fragmented Data | Inputs may come from multiple teams and formats | Combines uploaded files plus pasted notes into one unified BRD |
| Real-Time | User can upload and get generated result quickly | Live ingestion pipeline, progress overlay, instant visualizer |
| Context-Aware | Understands domain, compliance, and business meaning | Domain classifier detects FinTech/Health/etc. and adjusts compliance focus |
| Accurate | Uses better models when content is long, risky, or visual | Routes simple extraction to fast model, synthesis/image/conflict checks to advanced model |
| Explainable | User can see why requirement exists | Source trace, confidence score, conflict drawer, model route reasons |
| Complex Environments | Inputs can conflict or contain compliance concerns | Conflict detector finds contradictions and flags risky requirements |
| Dynamic | Project can be edited, exported, saved, and reviewed | Visualizer, archive, export to PDF/DOCX/XLSX, version-like saved project flow |

## Our Solution Architecture

1. Input Layer:
   Users provide project notes, documents, and images.

2. Multimodal Processing Layer:
   Text is extracted from documents. Images are analyzed for UI elements, flows, and implied requirements.

3. Adaptive AI Routing:
   The router checks modality, token estimate, risk/compliance language, and input count.

4. BRD Generation:
   AI creates executive summary, objectives, scope, stakeholders, functional requirements, non-functional requirements, risks, assumptions, and acceptance criteria.

5. Explainability Layer:
   Each requirement gets source trace, confidence, priority, and conflict information.

6. Storage and Demo Layer:
   The target architecture uses Google Cloud Storage for uploaded files, Firebase for authentication/workspace access, and BigQuery for generated BRD analytics, requirement history, and dashboard reporting.

## Google Products And Use Cases

| Google Product | Use Case In BRD Forge | Pitch Line |
|---|---|---|
| Gemini AI | Multimodal reasoning over text, documents, and images | "Gemini understands fragmented inputs and helps synthesize them into structured BRD sections." |
| Vertex AI | Managed AI runtime, model governance, scalable inference | "Vertex AI gives us an enterprise-ready layer for deploying and monitoring AI workflows." |
| Google Cloud Storage | Stores uploaded PDFs, text files, images, and generated exports | "GCS becomes the durable file lake for every source document and artifact." |
| BigQuery | Stores structured BRD analytics, requirement metrics, confidence trends, and conflict reports | "BigQuery lets leaders analyze requirement quality across projects, teams, and domains." |
| Firebase Authentication | Login and identity management for team members | "Firebase Auth gives secure access control for team leads, analysts, and reviewers." |
| Firestore / Firebase Database | Real-time workspace sync and collaborative project metadata | "Firebase can keep project state, edits, and review status synced across users." |
| Firebase Hosting | Hosts the frontend demo/application | "Firebase Hosting can serve the React app globally with simple deployment." |
| Cloud Functions | Event-driven processing after uploads or project generation | "Cloud Functions can trigger parsing, validation, or notifications automatically." |
| Cloud Run | Scalable backend deployment for the FastAPI service | "Cloud Run scales the API from zero to many users without managing servers." |
| IAM | Role-based permissions for storage, BigQuery, and AI access | "IAM ensures each service account only has the permissions it needs." |
| Secret Manager | Secure storage for API keys and service credentials | "Secret Manager keeps credentials out of code and environment files." |
| Cloud Logging / Monitoring | Tracks API errors, latency, model calls, and system health | "Logging and monitoring make the system observable for production readiness." |

## Google Cloud Data Flow

1. User logs in through Firebase Authentication.
2. User uploads text, document, or image inputs.
3. Files are stored in Google Cloud Storage.
4. The backend sends text/image content to Gemini or the configured AI model through the routing layer.
5. Generated BRD JSON, confidence metrics, routing decisions, and conflict reports are stored in BigQuery.
6. Firebase/Firestore can store workspace state, user ownership, and collaboration metadata.
7. The frontend visualizer reads the structured BRD and displays requirements, risks, conflicts, and exports.

## Demo Story

Use this story during demo:

1. Start with fragmented input:
   "In real projects, requirements are not clean. They come from calls, emails, screenshots, PDFs, and stakeholder notes."

2. Upload text and image:
   "Here we upload a long payment-app text note and a wireframe image."

3. Show AI routing:
   "The system does not send everything blindly to the largest model. It estimates complexity and routes text extraction to a fast model, while image understanding and synthesis go to advanced multimodal reasoning."

4. Show generated BRD:
   "Now the fragmented inputs become a structured BRD with functional requirements, non-functional requirements, risks, assumptions, and acceptance criteria."

5. Show explainability:
   "Each requirement has source trace and confidence, so the team lead can defend where it came from."

6. Show conflicts:
   "If two stakeholders give contradictory requirements, the system flags them instead of hiding the ambiguity."

7. Show export:
   "Finally, the BRD can be exported for stakeholders and archived for future review."

## 4-Minute Pitch Script Draft

Opening:

"The problem statement asks us to build a scalable, multimodal, context-aware, and explainable AI system for fragmented real-time data. We focused on a very practical high-impact use case: turning messy stakeholder inputs into a reliable Business Requirements Document."

Scalable:

"The first keyword is scalable. In many AI apps, every input is sent to the biggest model, which increases cost and latency. Our system uses adaptive model routing. It estimates token length, checks risk terms like audit, compliance, bank, payment, and detects whether the input is text or image. Simple text extraction goes to a faster model, while long documents, multimodal inputs, and synthesis go to an advanced model. This gives us cost optimization, latency control, and better accuracy where it matters."

Multimodal:

"The second keyword is multimodal. Real project data does not only come as clean text. A team lead may receive screenshots, wireframes, PDFs, meeting notes, and raw requirement text. Our system accepts text and image inputs, extracts useful requirements, and combines them into one BRD."

Context-Aware:

"The third keyword is context-aware. The system detects the project domain, for example FinTech, and adjusts the BRD with compliance focus such as PCI-DSS, audit logging, encryption, and KYC. This makes the output business-aware, not just a generic summary."

Explainable:

"The fourth keyword is explainable. A team lead cannot simply say 'AI generated this.' They need to defend it. So every requirement has confidence, priority, source trace, and conflict status. The system also shows the model routing decision, so we can explain why a fast or advanced model was selected."

Demo Close:

"In short, BRD Forge turns fragmented multimodal data into a structured, explainable, exportable BRD. It reduces manual requirement analysis time, improves consistency, catches conflicts early, and uses AI models responsibly through routing and cost optimization."

## Likely Cross Questions And Answers

Q1. Why use multiple models instead of one powerful model?

A. Because not every task needs the most expensive model. Short text extraction can use a fast model, while visual input, long documents, compliance-heavy content, and final synthesis need stronger reasoning. This improves cost, latency, and scalability.

Q2. How is your system multimodal?

A. It processes text and image/wireframe inputs. The image path extracts UI elements, flows, labels, and implied requirements, then combines them with text and document requirements.

Q3. How do you ensure explainability?

A. We show source trace, confidence score, priority, conflict flags, and AI routing reasons. This helps a team lead understand where each requirement came from and why the AI made that decision.

Q4. What is scalable in your solution?

A. Scalability is handled at two levels: model-level routing for cost and latency optimization, and cloud-level architecture using Cloud Storage for files, BigQuery for analytics, Firebase for identity/workspace state, and Cloud Run for backend scaling.

Q5. Why BRD generation as the use case?

A. BRDs are a real bottleneck in software projects. Requirements arrive from many fragmented sources, and team leads spend time merging, validating, and explaining them. This is a strong fit for multimodal, context-aware AI.

Q6. How do you handle conflicts?

A. The system runs conflict detection across requirements. It checks contradictions such as "SSO required" versus "no third-party login allowed" and shows conflicts in a dedicated panel.

Q7. What if the AI output is wrong?

A. We do not present AI as blindly final. We provide confidence levels, source trace, editable visualizer sections, and export only after team review.

Q8. How do you optimize cost?

A. Through token estimation and risk-based routing. Small/simple tasks use a fast model. Advanced models are reserved for long, risky, multimodal, or reasoning-heavy tasks.

Q9. What cloud services are involved?

A. The Google Cloud architecture uses Cloud Storage for uploaded source files, BigQuery for BRD analytics and requirement records, Firebase Authentication for login, Firestore/Firebase for workspace state, Vertex AI/Gemini for multimodal AI, Cloud Run for backend deployment, IAM for access control, Secret Manager for credentials, and Cloud Logging/Monitoring for observability. AI runtime can be swapped depending on organizer requirement, but the system design remains cloud-native.

Q10. What makes this different from a normal chatbot?

A. A chatbot gives conversation. Our system gives a structured workflow: ingestion, model routing, BRD synthesis, explainability, conflict detection, visualization, archive, and export.

## Strong Final Line

"Our solution is not just generating text. It is creating an explainable decision pipeline for requirements engineering, where every input, model choice, requirement, risk, and conflict can be reviewed by a team lead."
