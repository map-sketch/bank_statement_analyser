@echo off
echo ==============================================
echo   Starting Vault ^& Vignette Ledger
echo ==============================================

cd /d "%~dp0"

echo [1] Checking/Creating Virtual Environment...
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo [3] Installing Frontend Dependencies...
cd frontend
pip install streamlit plotly requests pandas
cd ..

echo [4] Starting Services...
start "Backend" cmd /k "cd backend && ..\venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && ..\venv\Scripts\activate.bat && python -m streamlit run app.py"

echo Done! The app should open in your browser shortly.
