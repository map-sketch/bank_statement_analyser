import pandas as pd
from core.bank_formats.base import BaseBankParser

class KotakParser(BaseBankParser):
    @property
    def bank_name(self) -> str:
        return "Kotak"

    def detect(self, df: pd.DataFrame) -> float:
        expected_cols = {"date", "description", "debit", "credit", "balance"}
        
        actual_cols = {str(c).strip().lower() for c in df.columns}
        overlap = len(expected_cols & actual_cols)
        
        if overlap < len(expected_cols):
            for i, row in df.head(25).iterrows():
                row_vals = {str(val).strip().lower() for val in row.values}
                if len(expected_cols & row_vals) >= 4:
                    return (len(expected_cols & row_vals) / len(expected_cols)) * 0.9

        return overlap / len(expected_cols)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        expected_cols = {"date", "description", "debit", "credit", "balance"}
        actual_cols = {str(c).strip().lower() for c in df.columns}
        
        if len(expected_cols & actual_cols) < 4:
            for i, row in df.head(25).iterrows():
                row_vals = {str(val).strip().lower() for val in row.values}
                if len(expected_cols & row_vals) >= 4:
                    df = df.iloc[i+1:].reset_index(drop=True)
                    df.columns = row.values
                    break
                    
        df.columns = [str(c).strip().lower() for c in df.columns]

        result = pd.DataFrame()
        result["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce')
        result["description"] = df["description"].astype(str)
        
        def clean_amt(val):
            if pd.isna(val) or val == "":
                return 0.0
            if isinstance(val, str):
                val = val.replace(",", "")
            try:
                return float(val)
            except ValueError:
                return 0.0

        w_amt = df.get("debit", pd.Series([0]*len(df))).apply(clean_amt)
        d_amt = df.get("credit", pd.Series([0]*len(df))).apply(clean_amt)
        
        result["amount"] = w_amt + d_amt
        result["type"] = df.apply(
            lambda r: "DEBIT" if clean_amt(r.get("debit", 0)) > 0 else "CREDIT", axis=1
        )
        
        result["balance"] = df.get("balance", pd.Series(dtype=float)).apply(clean_amt)
        
        result = result.dropna(subset=["date"])
        result = result[result["date"].notnull()]
        
        return result
