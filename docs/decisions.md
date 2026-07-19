# Architecture Decision Records (ADR)

> Key technical decisions for the Privacy-First AI Bank Statement Analyzer, derived from the project context and architecture plan.

---

## ADR 1: Local-Only Processing (No External APIs)

**Status:** Accepted
**Context:** Users are highly sensitive about uploading bank statements containing PII and financial histories. Traditional LLM-based categorization (e.g., sending rows to OpenAI/Anthropic) compromises privacy.
**Decision:** All parsing, rule processing, and ML categorization must happen 100% locally. 
**Consequences:** 
- We cannot use off-the-shelf cloud LLMs. 
- We must build a custom, lightweight, in-memory ML model (using scikit-learn).
- Guarantees zero data leakage, forming the core value proposition of the product.

## ADR 2: Two-Tier Categorization Engine

**Status:** Accepted
**Context:** Rule-based systems are highly accurate but brittle for new merchants. Pure ML models are adaptable but can hallucinate on straightforward patterns (like ATM withdrawals).
**Decision:** Use a two-layer pipeline. Layer 1 applies strict Regex (UPI parsing) and keyword dictionary matching. If Layer 1 fails to find a match, Layer 2 (Local ML classifier via TF-IDF + Naive Bayes) acts as the fallback.
**Consequences:**
- Achieves high precision on known entities while maintaining high recall on unknown descriptions.
- Requires maintaining both a keyword dictionary and a trained `.pkl` model.

## ADR 3: Pandas for Data Ingestion

**Status:** Accepted
**Context:** Bank statements come in highly varied formats (`.csv`, `.xls`, `.xlsx`), often with messy headers, trailing footers, and strange encoding.
**Decision:** Use Python's `pandas` combined with `openpyxl` and `xlrd` for the ingestion layer.
**Consequences:**
- Provides robust, vector-based data wrangling.
- Handles date parsing and missing value imputation efficiently.
- Slightly higher memory footprint than standard `csv` module, but acceptable for files < 50MB.

## ADR 4: SQLite as the Primary Database

**Status:** Accepted
**Context:** The app needs to store session data, parsed transactions, and cached analytics. However, forcing users to install PostgreSQL or Docker for a local privacy-first app creates excessive friction.
**Decision:** Use SQLite as the database layer via SQLAlchemy ORM.
**Consequences:**
- Zero configuration required. The `.db` file is generated automatically in `./data/`.
- Perfect for single-user local deployment.
- Requires careful handling of concurrent writes if the app is scaled, but sufficient for Phase 1 session-based architecture.

## ADR 5: Streamlit for the Frontend

**Status:** Accepted
**Context:** The application requires complex interactive dashboards with time-series charts, dynamic filtering, and optimistic UI updates for the "Human-in-the-Loop" toggles.
**Decision:** Build the frontend as a Streamlit application, communicating with the backend via REST API.
**Consequences:**
- Decouples the UI from the Python backend, allowing for rich, snappy interactions.
- Leverages Plotly for interactive visualization within Python.
- 100% Python stack, zero Node.js required, but can be built into static files for production delivery.

## ADR 6: UUID-Based Session Management

**Status:** Accepted
**Context:** Since there is no user authentication in Phase 1 (to reduce friction), we need a way to isolate uploads if the app is run on a shared local network or opened in multiple tabs.
**Decision:** Assign a unique UUID to every file upload. All database rows (transactions, analytics cache) belong to this `session_id`.
**Consequences:**
- No login required.
- Easy to implement automated cleanup jobs that delete sessions older than 24 hours.
- State is effectively ephemeral, aligning with the privacy-first ethos.
