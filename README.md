# Vault & Vignette Ledger (AI Bank Statement Analyzer)

A privacy-first, locally-hosted AI bank statement analyzer that automatically detects your bank format, categorizes transactions (using a hybrid Rule + Machine Learning engine), and visualizes your spending habits in a beautiful "Luxury Nostalgia" comic-panel dashboard.

## Features
- **Privacy-First**: No data leaves your machine. 100% offline parsing and machine learning inference.
- **Auto-Detection**: Upload HDFC, SBI, ICICI, Axis, or Kotak statements and it automatically identifies the bank.
- **Hybrid Categorization Engine**: Employs Regex parsing, Merchant keyword mappings, and an NLP Machine Learning model (TF-IDF + Naive Bayes) as a fallback.
- **Avoidability Engine**: Segregates "Avoidable" spending (e.g., Food, Shopping) from "Unavoidable" spending (Rent, EMI).
- **Salary & Anomaly Detection**: Automatically flags your salary deposits and anomalously high expenditures.

## Architecture
- **Backend**: FastAPI, SQLite, SQLAlchemy, Scikit-Learn
- **Frontend**: Streamlit, Plotly
- **Design System**: "Illustrated Neo-Vintage" with Custom CSS

## Quick Start (Windows)

The easiest way to run the application is to use the provided batch script:

1. Double-click `run.bat` in the project root.
   *(This will automatically create a virtual environment, install all dependencies, and launch both the backend and frontend).*



## How to Train the ML Model
If you want to fine-tune the categorization engine:
1. Open `backend/data/training/transactions.csv` and add more labeled transaction descriptions.
2. Run the trainer script:
```powershell
cd backend
python -m app.ml.trainer
```
3. Restart the FastAPI server to load the fresh models.
