# Sanskrit Retrieval Enhancement Platform - Deep Architecture & Technical Work File

## Executive Summary & Core Principle

The **Sanskrit Retrieval Enhancement Platform** is a production-grade, full-stack Information Retrieval (IR) web application engineered specifically for classical Sanskrit literature. 

Standard IR search engines struggle with Sanskrit because of its rich inflectional morphology (subanta noun declensions, tinanta verb conjugations) and heavy euphonic combinations (sandhi) and compound words (samasa). 

The platform operates on the cardinal principle:
> **"Normalize for search, preserve for display."**

- **Preserve for Display**: The exact, immutable original text uploaded by users (across TXT, JSON, CSV, XML, and EPUB formats) is stored untouched. Enforced via the strict system invariant:
  $$\text{stored\_original\_text} == \text{uploaded\_original\_text}$$
- **Normalize for Search**: Text is processed through a **deterministic rule-based Sanskrit NLP pipeline** (no black-box LLMs or non-deterministic hallucinations) that derives linguistic representations (Unicode NFC, IAST/SLP1 transliterations, Sandhi split candidate tokens, Morphological lemmas, and Samasa compound constituents). Every derived token maintains an exact `(start_char, end_char)` character offset mapping pointing directly back into the unaltered original text.

---

## 1. System Workflow & End-to-End User Flow

```mermaid
flowchart TD
    A[User Registration / Login] -->|JWT Token Issued| B[Corpus Management]
    B -->|Upload TXT / JSON / CSV / XML / EPUB| C[File Parser & Ingestion]
    C -->|Store Immutable original_text| D[Database Storage SQLite / Postgres]
    C -->|Trigger Pipeline| E[Deterministic Sanskrit NLP Engine]
    
    subgraph NLP Pipeline
        E --> E1[Unicode Normalization & Transliteration]
        E1 --> E2[Tokenization & Offset Calculation]
        E2 --> E3[Rule-Based Sandhi Engine]
        E3 --> E4[Subanta / Tinanta Morphology Lemmatizer]
        E4 --> E5[Samasa Compound Decomposition]
    end
    
    NLP Pipeline --> F[Multi-Layer Offset Inverted Indexer]
    
    subgraph Search & Retrieval
        G[User Search Query] --> H{Search Strategy}
        H -->|Baseline| I[Exact Surface Matching]
        H -->|Enhanced| J[Multi-Field BM25 Scoring Across Surface, Sandhi, Lemma, Samasa]
        I --> K[Ranked Hits & Offset Highlighting]
        J --> K
        K --> L["Explain Match" Rule Trace Generator]
    end

    subgraph Research Benchmarking
        M[Ablation Benchmark Runner] --> N[Evaluate Baseline vs. Enhanced Engine]
        N --> O["Calculate Metrics (Precision@K, Recall@K, F1, MRR, nDCG@K)"]
    end
```

### Detailed User Journey Steps:
1. **Authentication & Data Isolation**:
   - User registers or logs in via `/api/v1/auth/register` or `/api/v1/auth/login`.
   - Backend hashes passwords using PBKDF2 HMAC SHA-256 and issues a JWT bearer access token (`HS256`).
   - Every request enforces data isolation: queries and document operations are restricted strictly to corpora owned by `current_user.id`.

2. **Corpus & Document Ingestion**:
   - User creates a Corpus (e.g. "Bhagavad Gita", "Hitopadesha").
   - User uploads literature files (TXT, JSON, CSV, XML, EPUB).
   - Document parser extracts the raw string untouched.
   - Database persists `original_text`, `character_count`, and `word_count`.
   - Real-time ingestion progress tracks stages: `Uploaded` → `Processing` → `Indexing` → `Ready`.

3. **Deterministic NLP Pipeline Processing**:
   - The document string is tokenized using regular expressions capturing Devanagari and Latin/IAST ranges.
   - For every extracted surface token, character start and end offsets `[start_char:end_char]` are computed and verified against `original_text[start_char:end_char] == token.surface`.
   - The token is passed through the Sandhi splitter, Morphological lemmatizer, and Samasa compound decomposer.

4. **Multi-Layer Indexing**:
   - `SanskritSearchIndexer` indexes tokens across 6 distinct fields:
     - `surface`: Exact original surface string.
     - `normalized`: Devanagari Unicode normalized form.
     - `iast`: Transliterated IAST form and ASCII diacritic-stripped form.
     - `sandhi`: Rule-generated split candidate tokens.
     - `lemma`: Stem / root lemma form.
     - `samasa`: Compound constituent stems.

5. **Search Execution & Offset Highlighting**:
   - In **Search Workspace**, user selects **Baseline** or **Enhanced** strategy.
   - Queries can be typed in Devanagari (`हितोपदेशः`), IAST (`hitopadeśa`), or ASCII (`hitopadesa`).
   - **Baseline Mode**: Only queries the `surface` index.
   - **Enhanced Mode**: Expands queries across `surface`, `iast`, `normalized`, `sandhi`, `lemma`, and `samasa` index fields with customized boost weights.
   - Results display snippets of the **unaltered original text** with exact character span highlights rendered using `<mark>` elements mapped to offsets.

6. **Interactive "Explain Match" Resolution**:
   - Clicking **"Explain Match"** opens a drawer detailing why each passage hit.
   - Displays exact matched sub-tokens, character offset span `[start_char:end_char]`, applied rule code (e.g., `SANDHI_SVARA_02`, `MORPH_SUB_GEN_SG`), and detailed grammatical explanation.

7. **Ablation Study Benchmarking**:
   - Researchers execute ablation studies via the **Ablation Benchmark** suite.
   - Computes Precision@5, Recall@5, F1-Score, MRR, and nDCG@5 comparing Baseline Search vs Enhanced Engine across gold-standard benchmark queries.

8. **Admin Panel Telemetry**:
   - Monitors active users, total documents, total indexed terms, background ingestion job logs, and inspects active NLP rules.

---

## 2. Technical Architecture & Tech Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons | Single-Page Application (SPA) with dark glassmorphism theme, Google Fonts (`Noto Serif Devanagari` & `Inter`), responsive routing (`react-router-dom`). |
| **Backend API** | Python 3.11/3.13, FastAPI, Pydantic v2 | High-performance asynchronous REST API framework, CORS middleware, JWT authentication, background processing. |
| **Database** | SQLAlchemy 2.0, SQLite / PostgreSQL | Dual DB adapter setup: Zero-config SQLite default for immediate local running, PostgreSQL for production docker deployment. |
| **Search Engine** | In-Process Multi-Layer Inverted BM25 Search Engine / OpenSearch | Custom in-memory inverted indexer with offset tracking matrices out-of-the-box, OpenSearch / Elasticsearch adapter via `docker-compose`. |
| **Testing & QA** | Pytest, HTTPX TestClient | 100% passing automated test suite covering auth, ingestion invariants, NLP pipeline, search scoring, and evaluation metrics. |
| **Containerization**| Docker, Docker Compose | Multi-stage Dockerfiles (`Dockerfile.backend`, `Dockerfile.frontend`) and orchestrator with PostgreSQL and OpenSearch containers. |

---

## 3. Sanskrit NLP Pipeline Engineering & Techniques

The Sanskrit NLP Pipeline (`backend/app/nlp/`) is strictly rule-based and deterministic:

### A. Unicode Normalization & Script Transliteration (`normalizer.py`)
- **Unicode NFC**: Applies `unicodedata.normalize("NFC", text)` to merge decomposed Devanagari characters.
- **Punctuation & Dandas**: Normalizes single dandas (`।`) and double dandas (`॥`), avagrahas (`ऽ`), anusvara (`ं`), visarga (`ः`), and virama (`्`).
- **Transliteration**: Provides bidirectional conversion between Devanagari, IAST (International Alphabet of Sanskrit Transliteration), SLP1, and diacritic-stripped ASCII fallback (`strip_diacritics`).

### B. Character Offset-Preserving Tokenization (`tokenizer.py`)
- Uses regular expressions (`[\u0900-\u097F\wāīūṛṝḷḹṃḥṅñṭḍṇśṣ]+`) to find contiguous word spans.
- Captures `start_char` and `end_char` for each token match `match.start()` and `match.end()`.
- Verifies local assertion: `original_text[start_char:end_char] == token.surface`.

### C. Sandhi Engine (`sandhi.py`)
Sanskrit Sandhi involves phonetic sound changes at word boundaries. The Sandhi Engine applies pattern rules to generate split candidate tokens and rule IDs:

1. **Svara Sandhi (Vowels)**:
   - **Guṇa Sandhi**: $a/\bar{a} + i/\bar{i} \rightarrow e$ (e.g. `hitom` + `upadeśa` $\rightarrow$ `hitopadeśa`), $a/\bar{a} + u/\bar{u} \rightarrow o$.
   - **Dīrgha Sandhi**: $a/\bar{a} + a/\bar{a} \rightarrow \bar{a}$ (e.g. `vidyā` + `ālaya` $\rightarrow$ `vidyālaya`).
   - **Yaṇ Sandhi**: $i/\bar{i} + \text{vowel} \rightarrow y$ (e.g. `yadi` + `api` $\rightarrow$ `yadyapi`), $u/\bar{u} + \text{vowel} \rightarrow v$ (e.g. `su` + `āgatam` $\rightarrow$ `swāgatam`).
   - **Purvarupa Sandhi**: $e/o + a \rightarrow e/o + \text{ऽ}$ (e.g. `te` + `api` $\rightarrow$ `te'pi`).

2. **Visarga Sandhi**:
   - $\text{ḥ} + t \rightarrow st$ (e.g. `namaḥ` + `te` $\rightarrow$ `namaste`).
   - $\text{ḥ} + c \rightarrow śc$ (e.g. `namaḥ` + `candraḥ` $\rightarrow$ `namaścandraḥ`).
   - $\text{aḥ} + \text{voiced} \rightarrow o$.

3. **Vyanjana Sandhi (Consonants)**:
   - $t + ś \rightarrow cch$ (e.g. `tat` + `śruta` $\rightarrow$ `tacchruta`).
   - $t + c \rightarrow cc$ (e.g. `sat` + `cit` $\rightarrow$ `saccit`).

### D. Morphological Lemmatizer (`morphology.py`)
Maps inflected Sanskrit forms to root lemmas:
- **Subanta (Noun Declensions)**: Parses cases 1–7 (Nominative, Accusative, Instrumental, Dative, Ablative, Genitive, Locative) across Singular, Dual, and Plural.
  - e.g., `rāmeṇa` / `रामेण` $\rightarrow$ lemma `rāma` / `राम` (Instrumental Singular).
  - e.g., `kṛṣṇasya` / `कृष्णस्य` $\rightarrow$ lemma `kṛṣṇa` / `कृष्ण` (Genitive Singular).
  - e.g., `dharmāt` / `धर्मात्` $\rightarrow$ lemma `dharma` / `धर्म` (Ablative Singular).
- **Tinanta (Verb Conjugations)**: Parses verb tenses and persons.
  - e.g., `gacchati`, `gacchanti`, `gacchāmi` $\rightarrow$ root lemma `gam` (`गम्`).
  - e.g., `karoti`, `kurvanti` $\rightarrow$ root lemma `kṛ` (`कृ`).

### E. Samasa Compound Decomposition (`samasa.py`)
Decomposes compound words into constituent stems:
- e.g., `rājalakṣmī` $\rightarrow$ `rāja` + `lakṣmī` (Rāja Tatpuruṣa).
- e.g., `mahādevī` $\rightarrow$ `mahā` + `devī` (Mahā Karmadhāraya).

---

## 4. Search & Scoring Mechanics

The search engine (`backend/app/search/engine.py`) computes relevance scores based on multi-field term weights:

$$\text{Score}(D, Q) = \sum_{t \in Q} \sum_{f \in \text{Fields}} \text{TF}(t, f, D) \times W_f$$

Where field weight multipliers $W_f$ are:
- **Exact Surface Match**: $W_{\text{surface}} = 3.0$
- **Transliteration / Normalization**: $W_{\text{norm}} = 2.5$
- **Morphological Lemma Match**: $W_{\text{lemma}} = 2.0$
- **Sandhi Split Expansion Match**: $W_{\text{sandhi}} = 1.8$
- **Samasa Constituent Match**: $W_{\text{samasa}} = 1.5$

---

## 5. Evaluation Framework & Mathematical Metrics

The Evaluation Engine (`backend/app/evaluation/metrics.py`) computes standard IR metrics:

### A. Precision@K ($P@K$)
$$P@K = \frac{|\text{Retrieved Documents in Top } K \cap \text{Relevant Documents}|}{K}$$

### B. Recall@K ($R@K$)
$$R@K = \frac{|\text{Retrieved Documents in Top } K \cap \text{Relevant Documents}|}{|\text{Total Relevant Documents}|}$$

### C. F1-Score
$$F1 = 2 \times \frac{P@K \times R@K}{P@K + R@K}$$

### D. Mean Reciprocal Rank (MRR)
$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$

### E. Normalized Discounted Cumulative Gain (nDCG@K)
$$\text{DCG}@K = \sum_{i=1}^{K} \frac{rel_i}{\log_2(i + 1)}$$
$$\text{nDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

Where $\text{IDCG}@K$ is the Ideal DCG score sorted by true ground-truth relevance.

---

## 6. Verification & Test Results

All 8 backend automated Pytest tests pass 100%:
- `test_auth.py`: User registration, login, JWT token verification, data security.
- `test_ingestion.py`: File parsing (TXT, JSON, CSV, XML) and text preservation assertion (`stored == uploaded`).
- `test_nlp.py`: Unicode normalization, Sandhi splitting rules, Morphological lemmatization, and exact character offset mapping.
- `test_search.py`: Baseline vs. Enhanced search retrieval accuracy & offset match highlights.
- `test_evaluation.py`: Precision, Recall, F1, MRR, and nDCG metric calculations.

Frontend production bundle build (`npm run build`):
- Transformed 1498 modules cleanly into `dist/assets/index-BxgMowNR.js` and compiled Tailwind CSS stylesheet `dist/assets/index-XWAlLTWt.css`.
