import os
import uuid
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from core.models.db_models import SessionModel, TransactionModel
from core.bank_formats.registry import registry
from core.models.schemas import UploadResponse, DateRange
from core.services.categorization import categorize_all
from core.services.analytics import compute_analytics

def find_and_set_header(df: pd.DataFrame) -> pd.DataFrame:
    keywords = {'date', 'narration', 'description', 'withdrawal', 'deposit', 'balance', 'chq', 'ref', 'value dt', 'credit', 'debit', 'amount', 'particulars'}
    for i in range(min(50, len(df))):
        row_values = df.iloc[i].fillna("").astype(str).str.lower()
        matches = sum(1 for val in row_values if any(kw in str(val) for kw in keywords))
        if matches >= 3:
            new_header = df.iloc[i].fillna("").astype(str).str.strip()
            cols = []
            seen = {}
            for col in new_header:
                if col == "":
                    col = "Unnamed"
                if col in seen:
                    seen[col] += 1
                    cols.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    cols.append(col)
            df = df.iloc[i+1:].copy()
            df.columns = cols
            df.reset_index(drop=True, inplace=True)
            return df
            
    # Fallback to row 0
    cols = []
    seen = {}
    for col in df.iloc[0].fillna("").astype(str).str.strip():
        if col == "":
            col = "Unnamed"
        if col in seen:
            seen[col] += 1
            cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            cols.append(col)
    df = df.iloc[1:].copy()
    df.columns = cols
    df.reset_index(drop=True, inplace=True)
    return df

def process_upload(file_path: str, filename: str, db: Session) -> UploadResponse:
    # Read file
    if file_path.endswith('.csv'):
        # Edge Case 1.1.10: Handle BOM
        df = pd.read_csv(file_path, encoding='utf-8-sig', sep=None, engine='python', header=None)
    else:
        df = pd.read_excel(file_path, header=None)

    # Edge Case 1.1.2: Check if empty
    if df.empty:
        raise ValueError("No transactions found in the file.")
        
    # Find real header dynamically and drop metadata above it
    df = find_and_set_header(df)

    # Detect and parse
    bank_name, normalized_df = registry.detect_and_parse(df)

    if normalized_df.empty:
        raise ValueError("Parsed file yielded 0 valid transactions.")

    # Create session
    session_id = str(uuid.uuid4())
    db_session = SessionModel(
        id=session_id,
        filename=filename,
        bank_name=bank_name
    )
    db.add(db_session)
    db.flush()

    # Insert transactions
    records = normalized_df.to_dict(orient="records")
    for rec in records:
        txn = TransactionModel(
            session_id=session_id,
            date=rec["date"].date() if pd.notna(rec["date"]) else datetime.now().date(),
            description=str(rec["description"]) if pd.notna(rec["description"]) and str(rec["description"]).strip() != "" and str(rec["description"]).lower() != "nan" else "Unknown Transaction",
            amount=float(rec["amount"]) if pd.notna(rec["amount"]) else 0.0,
            type=str(rec["type"]),
            balance=float(rec["balance"]) if pd.notna(rec.get("balance")) else None
        )
        db.add(txn)
    
    db.commit()

    # Call Phase 1C and 1D logic
    categorize_all(db, session_id)
    compute_analytics(db, session_id)

    # Build response
    min_date = normalized_df["date"].min().date()
    max_date = normalized_df["date"].max().date()
    
    return UploadResponse(
        session_id=session_id,
        bank_name=bank_name,
        transaction_count=len(normalized_df),
        date_range=DateRange(start=min_date, end=max_date),
        status="success"
    )
