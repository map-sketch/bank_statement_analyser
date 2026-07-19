# Deployment Plan: Vault & Vignette

The current architecture consists of a **Streamlit frontend** and a **FastAPI backend**. Deploying this architecture requires careful consideration because Streamlit Community Cloud is designed to host single-port Streamlit applications, not multi-service architectures with background FastAPI servers.

Below are the two viable approaches to deploy both the frontend and backend.

---

## Option 1: The Unified Architecture (Recommended for Streamlit Cloud)

If your strict requirement is to deploy **everything within Streamlit Community Cloud**, you must merge the backend and frontend into a single monolithic Streamlit app. 

### Why?
Streamlit Cloud exposes only one public port (usually 8501) for the Streamlit app. If you run FastAPI on port 8000 in the background, the frontend browser cannot reach `localhost:8000` because "localhost" in the browser refers to the user's local machine, not the Streamlit server.

### Migration Steps
1. **Remove FastAPI Network Layer:** 
   Bypass the `requests.get()` and `requests.post()` calls in `frontend/app.py`.
2. **Direct Function Calls:** 
   Import the service functions (e.g., `compute_analytics()`, `categorize()`, `parse_file()`) directly into `app.py`.
3. **State Management:** 
   Instead of uploading the file to FastAPI and saving to SQLite, read the uploaded file directly into a Pandas DataFrame in Streamlit, process it in-memory, and store it in `st.session_state`.
4. **Deployment:** 
   Push the merged code to a GitHub repository and connect it to Streamlit Community Cloud. 

**Pros:** Free hosting on Streamlit Cloud, simpler single-repo deployment.
**Cons:** Requires refactoring the current decoupled FastAPI architecture. State is lost if the Streamlit app goes to sleep (though for a session-based analyzer, this is usually acceptable).

---

## Option 2: The Decoupled Architecture (Recommended for Scalability)

If you wish to preserve the current FastAPI + SQLite architecture, you must deploy the frontend and backend to separate hosting providers.

### 1. Backend Deployment (Railway)
- **Host:** Railway.
- **Environment Variables:** Set `DATABASE_URL` (use PostgreSQL instead of SQLite if you want persistent storage across deploys, as Railway containers have ephemeral disks unless a volume is attached).
- **Result:** You will get a public URL like `https://vault-backend.up.railway.app`.

### 2. Frontend Deployment (Streamlit Community Cloud)
- **Host:** Streamlit Community Cloud.
- **Environment Variables:** Update `frontend/app.py` to use an environment variable for the API URL:
  ```python
  import os
  API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
  ```
- **Configuration:** In your Streamlit Cloud dashboard, set the Secret `API_BASE_URL` to your Railway backend URL (e.g. `https://vault-backend.up.railway.app/api`).
- **Result:** You will get a public URL like `https://vault-vignette.streamlit.app`.

**Pros:** Preserves existing architecture; backend can scale independently; can handle heavier ML loads without blocking the UI.
**Cons:** Requires managing two separate deployment platforms.

---

## Next Steps

**Decision Point:** 
Do you want to refactor the code to merge FastAPI into Streamlit (Option 1) for a single Streamlit deployment, or do you want to keep them separate and deploy the backend to a service like Railway (Option 2)?

Once decided, we can proceed with updating the codebase to support the chosen deployment strategy.
