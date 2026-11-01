# ⚖️ CLARA — Compliance & Ledger Analysis Retrieval Assistant

**CLARA** (**C**ompliance & **L**edger **A**nalysis **R**etrieval **A**ssistant) is a production-ready, autonomous AI regulatory persona and Hierarchical Hybrid RAG system designed for enterprise financial controllers, statutory auditors, and compliance officers.

CLARA cross-references complex financial ledger inquiries, statutory accounting frameworks (IFRS, US GAAP, SEC regulations), banking capital standards (Basel III Endgame, FRTB), and ESG sustainability reporting directives (IFRS S1/S2, EU CSRD Wave 2) to provide audit-defensible, citation-grounded intelligence.

---

## 🌟 Key Features & Innovations

### 🤖 1. Autonomous AI Persona
- **Persona Identity**: Positioned as a senior controlling and compliance specialist with a strict zero-hallucination policy.
- **Audit-Defensible Focus**: Evaluates statutory standards and accounting evidence, requiring explicit source references for every material claim.
- **Visual Identity**: Features dedicated persona profile cards, live status indicators (`🟢 Online • Financial Intelligence`), and verified grounding signatures on every response.

### 💬 2. ChatGPT-Style Conversational Interface (`streamlit-shadcn-ui`)
- **Conversational Memory**: Full chat session state management powered by Streamlit's native chat primitives (`st.chat_message`, `st.chat_input`).
- **Modern Design System**: Built with `streamlit-shadcn-ui` components for clean metric cards, entity badges, status tabs, and cards.
- **Empty-State Landing Experience**: Interactive greeting and quick-start inquiry cards for standard 2026 regulatory questions.

### 🔍 3. Transparent & Collapsible RAG Mechanics
To maintain an uncluttered conversation flow like ChatGPT while preserving full enterprise audibility, the interface separates conversational answers from retrieval mechanics:
- **Clean Default Stream**: Users see only the clean user message and the assistant's structured synthesis.
- **Clickable Input Inspection**: An expandable toggle (`🔍 Pre-Retrieval Input Processing & Query Analysis`) reveals spaCy financial NER entity badges, domain query expansions, and retrieval parameters.
- **Clickable Output Inspection**: An expandable toggle (`📊 Inspect RAG Retrieval & Context Details`) reveals:
  - **Source Attributions**: Specific regulatory documents and policy manuals cited.
  - **Retrieved Chunks & Reranker Scores**: Ranked child chunks with Cross-Encoder scores, RRF scores, and Parent IDs.
  - **Full Parent Context**: The exact hierarchical context injected into the LLM prompt.

### 🏗️ 4. Production Hierarchical Hybrid RAG Pipeline
1. **Pre-Retrieval Query Expansion & NER**: Extracts recognized financial entities using spaCy and enriches queries with domain-specific terminology.
2. **Hybrid Search (Dense + Sparse)**:
   - **Dense Vectors (ChromaDB)**: Multilingual semantic embeddings (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).
   - **Sparse BM25 (Elasticsearch / rank_bm25)**: Exact token and standard code matching (`SEC Item 1.05`, `IFRS S2`, `CSRD`, `FRTB`).
   - **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse ranks into a single unified candidate pool.
3. **Cross-Encoder Reranking**: Re-scores candidate chunks with `BAAI/bge-reranker-base` to eliminate false positives.
4. **Hierarchical Parent Expansion**: Top child chunks (300 chars) dynamically expand back into their parent contexts (1,200 chars) to prevent context fragmentation during generation.
5. **Grounded Generation**: Synthesizes verified answers using `ChatGroq` with strict citation constraints.

---

## 📊 Benchmark Regulatory Queries (2026 Standards)

CLARA comes pre-configured with evaluation and sample queries for upcoming 2026 financial compliance frameworks:
- **SEC Item 1.05 Form 8-K**: Mandatory 4-business-day disclosure timeline for material cybersecurity incidents.
- **IFRS S2 Climate Disclosures**: Scope 1, Scope 2, and Scope 3 greenhouse gas measurement methodologies.
- **EU CSRD Wave 2**: Turnover thresholds, balance sheet criteria, and employee limits for non-EU parent groups.
- **Basel III Endgame**: Capital output floor percentage (72.5% phased transition) for risk-weighted assets.
- **FRTB Market Risk**: 97.5% confidence interval requirement for Expected Shortfall (ES).

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/your-org/CLARA.git
cd CLARA

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including streamlit-shadcn-ui
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and supply your credentials:
```bash
cp .env.example .env
```
Ensure your `GROQ_API_KEY` is configured in `.env`.

### 3. Ingest Financial Data & Build Indexes
Parse the raw financial corpus (`data/raw/`) and generate the hierarchical parent store and hybrid indexes:
```bash
python -m src.ingestion.run_ingestion
```

### 4. Launch CLARA Streamlit Chat UI
Run the interactive ChatGPT-style conversational assistant:
```bash
streamlit run ui/streamlit_app.py
```
Open your browser at `http://localhost:8501`.

### 5. Launch FastAPI Backend (Optional)
Start the REST API for programmatic access:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 6. Run RAG Evaluation Benchmark
Evaluate context recall, answer relevancy, and citation fidelity against `data/golden_eval_set.json`:
```bash
python -m src.evaluation.evaluate_rag
```

---

## 🐳 Docker Deployment

You can deploy CLARA and its FastAPI backend using Docker Compose:

```bash
# Build and run containers in detached mode
docker-compose up -d --build

# Verify running services
docker-compose ps
```

- **Streamlit UI**: `http://localhost:8501`
- **FastAPI API**: `http://localhost:8000/docs`

---

## 📁 Directory Structure

```text
CLARA/
├── data/
│   ├── raw/                  # Raw regulatory standards & financial corpus
│   ├── golden_eval_set.json  # Benchmark evaluation dataset
│   ├── parent_docstore.json  # Hierarchical parent document store
│   └── bm25_index.pkl        # Tokenized BM25 index
├── src/
│   ├── config.py             # Global configurations & model parameters
│   ├── ingestion/            # Hierarchical chunking & indexing pipelines
│   ├── retrieval/            # Hybrid retriever, RRF & Cross-Encoder reranker
│   ├── generation/           # Prompts, ChatGroq pipeline & citation validation
│   └── evaluation/           # RAG benchmark evaluation suite
├── api/
│   └── app.py                # FastAPI endpoints (/query, /ingest, /health)
├── ui/
│   └── streamlit_app.py      # CLARA ChatGPT-style UI (streamlit-shadcn-ui)
├── Dockerfile                # Production multi-stage Docker build
├── docker-compose.yml        # Multi-container orchestration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---
