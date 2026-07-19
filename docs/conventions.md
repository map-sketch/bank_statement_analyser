# Project Conventions: Privacy-First AI Bank Statement Analyzer

> Coding, design, and architecture conventions derived from the project context and implementation plan.

---

## 1. Architectural Conventions

- **Monorepo Structure**: The project is organized as a monorepo with explicit separation between the `frontend/` (React/Vite) and `backend/` (FastAPI) directories.
- **Privacy-First (Air-gapped by Design)**: No module is permitted to make external network calls to third-party services (e.g., no OpenAI, no cloud databases). All ML inference and data parsing must happen strictly on the local machine.
- **Stateless/Session-Based Processing**: The system operates on a temporary `session_id` basis. Uploads generate a UUID session. State is not bound to persistent user accounts in Phase 1.

## 2. Python & Backend Conventions

- **Framework**: FastAPI with Uvicorn.
- **Typing**: Strict Python 3.10+ type hinting is required for all function signatures. Use Pydantic models for all API requests and responses.
- **ORM & Database**: SQLAlchemy 2.0+ with SQLite. 
  - File path: `./data/bank_statement.db`
  - All database models should reside in `app.models.db_models`.
  - Use `check_same_thread=False` for SQLite to work with FastAPI async workers.
- **Data Processing**: Use `pandas` for all tabular data manipulation.
- **Error Handling**: Use standard FastAPI `HTTPException` with clear, user-friendly messages.
- **Dependency Injection**: Use FastAPI's `Depends()` for database session injection (`get_db`).

## 3. Frontend & UI Conventions

- **Framework**: Streamlit.
- **State Management**: Streamlit Session State (st.session_state) (sessions, analytics data, transaction filters).
- **Styling**: Streamlit themes & native styling (CSS variables) in `variables.css`. No Tailwind CSS unless explicitly migrated later.
- **Aesthetic**:
  - **Dark Mode Primary**: Deep navy/charcoal backgrounds.
  - **Glassmorphism**: Cards use `backdrop-filter: blur()` with subtle translucent borders.
  - **Typography**: Google Fonts (Inter, Roboto, or Outfit).
  - **Micro-animations**: Use `Streamlit native transitions` for page transitions, hover states, and entrance animations.
- **Charting**: Use `Plotly or st.bar_chart` for all data visualization (time-series, pie charts, donut charts).
- **Category Colors**: Must use a standard color map across the entire app (e.g., Food = Red, Investments = Green) defined in CSS variables.

## 4. API & Routing Conventions

- **Base Path**: All backend routes must be prefixed with `/api`.
- **RESTful Principles**:
  - `POST /api/upload` - Create new session
  - `GET /api/analyze/{session_id}` - Fetch analytics
  - `GET /api/transactions/{session_id}` - Fetch paginated transactions
  - `PATCH /api/transactions/{session_id}/{txn_id}` - Update a single transaction (e.g., avoidable toggle)
  - `GET /api/export/{session_id}` - Download CSV, XLS, XLSX, TXT, Delimited
- **Pagination**: Server-side pagination is mandatory for transaction lists (default size: 50, max: 200).

## 5. Machine Learning Conventions

- **Model Storage**: Pre-trained `.pkl` files must be stored in `backend/ml_models/`.
- **Training Scripts**: Training logic must be strictly separated into `backend/app/ml/` and should not be loaded in the main API server memory.
- **Model Loading**: Models must be loaded exactly once during the FastAPI `@asynccontextmanager lifespan` startup event to avoid cold-start latency on requests.

## 6. Testing Conventions

- **Backend**: `pytest` for all unit and integration tests.
- **Coverage**: Minimum 80% coverage required on `app/services/` and `app/rules/`.
- **Fixtures**: Use dummy CSV, XLS, XLSX, TXT, Delimited files in `tests/fixtures/` for testing the parsing engines without uploading real PII.
