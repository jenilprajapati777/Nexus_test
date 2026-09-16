# Sanskrit Retrieval Enhancement Platform

Please Review my code

A production-grade, end-to-end **Sanskrit Information Retrieval (IR) Web Application** designed around the core principle: **"Normalize for search, preserve for display."**

---

## Key Features & Core Principles

1. **Strict Text Preservation & Invariant Verification**:

   - Stores exact, immutable original uploaded text (`original_text`) across TXT, JSON, CSV, XML, and EPUB formats.
   - Enforces the strict invariant `stored_original_text == uploaded_original_text`.
   - All indexed tokens maintain `(start_char, end_char)` offset ranges relative to the original text.

2. **Deterministic Rule-Based Sanskrit NLP Pipeline (No Black-Box LLMs)**:

   - **Unicode & Script Transliteration**: Devanagari Unicode NFC normalization, dandas (`|`, `||`), avagraha (`ऽ`), and bidirectional transliteration across Devanagari, IAST, SLP1, and Velthuis.
   - **Sandhi Engine**: Rule-based candidate generator and splitter for Svara Sandhi (e.g. `hitom` + `upadeśa` -> `hitopadeśa`), Visarga Sandhi (`ḥ` + `t` -> `st`), and Vyanjana Sandhi (`t` + `c` -> `cc`).
   - **Morphological Lemmatizer**: Subanta noun declension stemmer (cases 1-7) and Tinanta verb conjugation parser (e.g. `rāmeṇa` -> `rāma`, `gacchati` -> `gam`).
   - **Samasa Engine**: Rule-based compound decomposition for Tatpuruṣa, Dvandva, Bahuvrīhi, and Karmadhāraya compounds (e.g. `rājalakṣmī` -> `rāja` + `lakṣmī`).

3. **Dual Search Engine & Offset Match Explainer**:

   - **Baseline Search**: Exact lexical surface form matching.
   - **Enhanced Search**: Multi-layered boosted query evaluation across Surface, Transliteration, Sandhi, Morphology, and Samasa index fields.
   - **Match Highlighting & Explainer**: Highlights exact character spans in unchanged original text and generates step-by-step rule resolution traces explaining _why_ a passage matched.

4. **Research Evaluation Framework**:

   - Automated Ablation Study suite computing IR metrics comparing Baseline vs Enhanced search:
     - **Precision@K (P@5, P@10)**
     - **Recall@K (R@5, R@10)**
     - **F1-Score**
     - **Mean Reciprocal Rank (MRR)**
     - **Normalized Discounted Cumulative Gain (nDCG@K)**

5. **Authentication & Data Isolation**:
   - Real user registration, login, JWT token authentication, and strict user data isolation (users only access their owned corpora/documents).

---

## Project Structure

```
Nexsus/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI router endpoints (auth, ingestion, search, evaluation, admin)
│   │   ├── models/       # SQLAlchemy models (User, Corpus, Document, Job, Rule, Benchmark)
│   │   ├── nlp/          # Deterministic NLP modules (normalizer, tokenizer, sandhi, morphology, samasa, pipeline)
│   │   ├── search/       # Inverted indexer, search engine, match explainer
│   │   ├── evaluation/   # Ablation study metrics engine (P@K, R@K, F1, MRR, nDCG)
│   │   └── main.py       # FastAPI application entrypoint
│   ├── tests/            # Pytest test suite (100% passing)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Navbar, Sidebar, HighlightedText, ExplainModal
│   │   ├── pages/        # Login, Register, Library, SearchWorkspace, EvaluationSuite, AdminPanel
│   │   ├── services/     # API fetch client
│   │   └── App.tsx       # Main React router
│   ├── package.json
│   └── vite.config.ts
├── sample_data/          # Sample Sanskrit texts in TXT, JSON, CSV, XML format
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── README.md
```

---

## Quick Start (Local Development)

### 1. Backend Setup

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -v
python -m uvicorn app.main:app --reload --port 8000
```

- API Documentation: `http://localhost:8000/api/v1/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Web Application UI: `http://localhost:3000`

---

## Production Docker Deployment

```bash
docker-compose up --build
```

- Frontend Dashboard: `http://localhost:80`
- Backend API: `http://localhost:8000`
- OpenSearch: `http://localhost:9200`
- PostgreSQL: `localhost:5432`

---

## Test Verification Results

All 8 automated Pytest test suites execute and pass 100%:

- `tests/test_auth.py`: User registration, login, JWT token verification, data security.
- `tests/test_ingestion.py`: File parsing (TXT, JSON, CSV, XML) and text preservation assertion (`stored == uploaded`).
- `tests/test_nlp.py`: Unicode normalization, Sandhi splitting rules, Morphological lemmatization, and exact character offset mapping.
- `tests/test_search.py`: Baseline vs. Enhanced search retrieval accuracy & offset match highlights.
- `tests/test_evaluation.py`: Precision, Recall, F1, MRR, and nDCG metric calculations.
