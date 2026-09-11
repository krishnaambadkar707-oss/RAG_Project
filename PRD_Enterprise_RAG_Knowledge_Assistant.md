# Product Requirements Document (PRD)
## Enterprise RAG Knowledge Assistant

| | |
|---|---|
| **Document Owner** | You (Project Author) |
| **Status** | Draft v1.0 |
| **Last Updated** | September 2026 |
| **Project Type** | Portfolio / Academic Capstone — Full-Stack AI Application |

---

## 1. Overview

### 1.1 Problem Statement
Employees at a company waste significant time searching across scattered PDFs and documents (HR policies, technical documentation, project records) to find answers to simple questions like *"What is the leave policy?"* or *"How do I request a VPN certificate?"*. Existing search is keyword-based, doesn't understand intent, and returns whole documents instead of direct answers.

### 1.2 Solution
Build an **Enterprise RAG (Retrieval-Augmented Generation) Knowledge Assistant** — a chatbot-style internal tool where employees ask natural-language questions and receive accurate, source-cited answers generated from the company's own document corpus (~100–150 PDFs/docs across HR, Engineering, and Projects).

### 1.3 Goals
- Reduce time-to-answer for internal knowledge questions from minutes to seconds
- Ground every answer in real company documents (no hallucinated policy info)
- Provide full traceability — every answer must cite its source document/section
- Demonstrate a production-grade RAG pipeline with **measurable quality**, not just a demo

### 1.4 Non-Goals (v1)
- Not a general-purpose chatbot (no open-domain Q&A)
- Not a document editing/authoring tool
- Not real-time multi-user collaborative chat (single-user sessions only)
- No fine-tuning of the LLM — retrieval-based grounding only

---

## 2. Target Users / Personas

| Persona | Need |
|---|---|
| **Employee** | Ask questions, get quick cited answers, view past conversations |
| **HR/Admin (Document Owner)** | Upload/manage documents, organize into collections |
| **Engineering Evaluator (you, as project author)** | Measure and improve RAG pipeline quality over time |

---

## 3. System Architecture

```
                    ┌─────────────────────┐
                    │   React Frontend     │
                    │ (Chat UI, Upload UI) │
                    └──────────┬───────────┘
                               │ REST API (JWT auth)
                    ┌──────────▼───────────┐
                    │     FastAPI Backend   │
                    ├───────────────────────┤
                    │ Auth Service          │
                    │ Document Service      │
                    │ Chunking Service      │
                    │ Embedding Service     │
                    │ Retrieval Service     │
                    │ Generation Service    │
                    │ Evaluation Service    │
                    └──────────┬────────────┘
                 ┌─────────────┼──────────────┐
                 ▼             ▼              ▼
        ┌───────────────┐ ┌──────────┐ ┌──────────────┐
        │ Vector DB      │ │PostgreSQL│ │  LLM API      │
        │ (Chroma/pgvector)│ (metadata,│ │ (Anthropic/   │
        │                │ │users,hist)│ │  OpenAI)      │
        └───────────────┘ └──────────┘ └──────────────┘
```

**Pipeline flow:**
`Document Upload → Parsing → Chunking → Embedding → Vector Store → Query → Retrieval (top-k) → LLM Generation (context + query) → Answer + Cited Sources → Logged for Evaluation`

---

## 4. Functional Requirements

### 4.1 Document Ingestion
- FR1: Admin can upload PDF/DOCX files via UI or `POST /documents/upload`
- FR2: System extracts text (and preserves page numbers / section headers where possible)
- FR3: Documents are assigned to a **collection** (e.g. `HR`, `Engineering`, `Projects`)
- FR4: Failed parses are logged with reason (corrupt file, scanned image w/o OCR, etc.)

### 4.2 Chunking & Embedding
- FR5: Text is split into chunks (~500–1000 tokens, ~10–20% overlap)
- FR6: Each chunk stores metadata: `document_id`, `page_number`, `section_title`, `collection_id`
- FR7: Chunks are embedded via an embedding model and stored in the vector DB with metadata

### 4.3 Query & Retrieval
- FR8: User submits a natural-language question, optionally scoped to a collection
- FR9: System embeds the query and retrieves top-k (default k=5) most similar chunks
- FR10: Retrieval supports metadata filtering (e.g. restrict to `HR` collection)

### 4.4 Answer Generation
- FR11: Retrieved chunks + query are passed to the LLM with a grounding prompt (*"Answer only using the provided context; say 'I don't know' if not covered"*)
- FR12: Response includes the generated answer **and** a list of source citations (document name, page/section, snippet)
- FR13: If no relevant chunks are found (low similarity score), system returns a fallback "no answer found" response instead of guessing

### 4.5 Conversation & History
- FR14: Each user session is stored; follow-up questions retain prior conversation context
- FR15: Users can view/search their past conversations
- FR16: Conversations are scoped per authenticated user

### 4.6 Authentication & Access
- FR17: Login/signup with JWT-based auth
- FR18: Role-based access: `admin` (upload/manage docs) vs `employee` (query only)
- FR19: Collections can have access restrictions (e.g. only HR role sees HR-only docs, if desired as stretch)

### 4.7 Multi-Collection Support
- FR20: Documents are grouped into named collections
- FR21: Users can query a specific collection or "all collections"

### 4.8 REST API
- FR22: All core functions exposed via documented REST endpoints (OpenAPI/Swagger auto-docs via FastAPI)

### 4.9 Evaluation System (⭐ Differentiator)
- FR23: Maintain a labeled test set of Q&A pairs (question, expected answer, expected source doc)
- FR24: Automated evaluation run computes and logs:
  - **Retrieval accuracy** — Precision@k / Recall@k (did the correct chunk get retrieved?)
  - **Answer relevance** — similarity or LLM-judge score between generated and reference answer
  - **Hallucination rate** — % of generated claims not supported by retrieved context (faithfulness/groundedness check, e.g. via LLM-as-judge or NLI model)
  - **Response latency** — retrieval time, generation time, and total time per query
- FR25: Evaluation results are viewable via a dashboard/report (table or simple charts)
- FR26: Evaluation can be re-run after pipeline changes (chunk size, k, prompt) to compare versions

---

## 5. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Query response (retrieval + generation) under ~5 seconds for typical query |
| **Scalability** | Support 100–150 documents, thousands of chunks, without redesign |
| **Reliability** | Graceful failure on bad uploads, LLM API errors, empty retrieval results |
| **Security** | Passwords hashed, JWT expiry, no plaintext secrets, API keys via env vars |
| **Portability** | Fully containerized via Docker Compose (backend + frontend + Postgres + vector DB) |
| **Observability** | Logs for ingestion, queries, latency, and evaluation runs |

---

## 6. Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Python + FastAPI |
| LLM | Anthropic Claude or OpenAI GPT (via API) |
| Embeddings | OpenAI `text-embedding-3-small`, or open-source `sentence-transformers` |
| Vector DB | Chroma (simplest) or `pgvector` extension on Postgres (unifies DB) |
| Relational DB | PostgreSQL (users, documents metadata, conversations, eval results) |
| Frontend | React (chat UI + upload/admin panel) |
| Auth | JWT (e.g. `fastapi-users` or custom) |
| Deployment | Docker + Docker Compose |
| Evaluation | Custom scripts, optionally `ragas` library for standardized RAG metrics |

---

## 7. Data Model (Core Entities)

- **User**: id, email, password_hash, role, created_at
- **Collection**: id, name, description
- **Document**: id, filename, collection_id, upload_date, status, page_count
- **Chunk** (in vector DB): id, document_id, text, embedding, page_number, section
- **Conversation**: id, user_id, created_at
- **Message**: id, conversation_id, role (user/assistant), content, sources (JSON), created_at
- **EvalRun**: id, run_date, config (chunk_size, k, prompt_version)
- **EvalResult**: id, eval_run_id, question, retrieval_score, relevance_score, hallucination_flag, latency_ms

---

## 8. Key API Endpoints (Illustrative)

```
POST   /auth/signup
POST   /auth/login
POST   /documents/upload
GET    /documents
GET    /collections
POST   /collections
POST   /query                → { answer, sources[], conversation_id }
GET    /conversations
GET    /conversations/{id}
POST   /evaluation/run
GET    /evaluation/results
```

---

## 9. Success Metrics

| Metric | Target (v1) |
|---|---|
| Retrieval Precision@5 | ≥ 80% on test set |
| Hallucination rate | < 10% of answers |
| Avg. response latency | < 5 seconds |
| Answer relevance score | ≥ 4/5 (LLM-judge or human eval) |

---

## 10. Milestones / Build Order

1. **M1 — Core Pipeline (Week 1–2):** Document upload, parsing, chunking, embeddings, vector store, basic retrieval script (CLI/notebook level)
2. **M2 — RAG Q&A (Week 2–3):** LLM generation with grounding + citations, wrap in FastAPI endpoint
3. **M3 — App Layer (Week 3–4):** Postgres models, auth, conversation history, collections
4. **M4 — Frontend (Week 4–5):** React chat UI + document upload/admin panel
5. **M5 — Evaluation System (Week 5–6):** Build labeled test set, implement 4 metrics, results dashboard
6. **M6 — Dockerize & Polish (Week 6):** Docker Compose, README, demo video/screenshots

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Scanned/image-only PDFs won't parse | Add OCR fallback (e.g. Tesseract) or note as known limitation |
| LLM hallucinates despite grounding | Strict prompt constraints + hallucination metric to quantify and iterate |
| Vector search misses relevant chunks | Tune chunk size/overlap, try hybrid search (keyword + vector) |
| Evaluation feels arbitrary | Use an established framework like `ragas` for credibility |

---

## 12. Stretch Goals (If Time Permits)
- Hybrid search (BM25 + vector)
- Streaming responses (token-by-token)
- Admin analytics dashboard (most-asked questions, unanswered queries)
- Feedback loop (thumbs up/down on answers feeding back into eval set)
