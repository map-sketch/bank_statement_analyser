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

echo [2] Installing Dependencies...
pip install -r requirements.txt

echo [3] Starting Application...
start "Vault & Vignette" cmd /k "venv\Scripts\activate.bat && streamlit run app.py"

echo Done! The app should open in your browser shortly.
