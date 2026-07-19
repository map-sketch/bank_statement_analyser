import pandas as pd
from app.bank_formats.base import BaseBankParser

class HdfcParser(BaseBankParser):
    @property
    def bank_name(self) -> str:
        return "HDFC"

    def detect(self, df: pd.DataFrame) -> float:
        expected_cols_v1 = {"date", "narration", "withdrawal amt", "deposit amt", "closing balance"}
        expected_cols_v2 = {"date", "narration", "debit amount", "credit amount", "closing balance"}
        
        actual_cols = {str(c).strip().lower().replace('.', '') for c in df.columns}
        
        overlap_v1 = len(expected_cols_v1 & actual_cols) / len(expected_cols_v1)
        overlap_v2 = len(expected_cols_v2 & actual_cols) / len(expected_cols_v2)
        overlap = max(overlap_v1, overlap_v2)
        
        if overlap < 1.0:
            for i, row in df.head(50).iterrows():
                row_vals = {str(val).strip().lower().replace('.', '') for val in row.values}
                o_v1 = len(expected_cols_v1 & row_vals) / len(expected_cols_v1)
                o_v2 = len(expected_cols_v2 & row_vals) / len(expected_cols_v2)
                best_o = max(o_v1, o_v2)
                if best_o >= 0.8:
                    return best_o * 0.9 

        return overlap

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        expected_cols_v1 = {"date", "narration", "withdrawal amt", "deposit amt", "closing balance"}
        expected_cols_v2 = {"date", "narration", "debit amount", "credit amount", "closing balance"}
        
        actual_cols = {str(c).strip().lower().replace('.', '') for c in df.columns}
        
        if len(expected_cols_v1 & actual_cols) < 4 and len(expected_cols_v2 & actual_cols) < 4:
            for i, row in df.head(50).iterrows():
                row_vals = {str(val).strip().lower().replace('.', '') for val in row.values}
                if len(expected_cols_v1 & row_vals) >= 4 or len(expected_cols_v2 & row_vals) >= 4:
                    df = df.iloc[i+1:].reset_index(drop=True)
                    df.columns = row.values
                    break
                    
        df.columns = [str(c).strip().lower().replace('.', '') for c in df.columns]

        result = pd.DataFrame()
        result["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce')
        result["description"] = df["narration"].astype(str)
        
        def clean_amt(val):
            if pd.isna(val) or val == "":
                return 0.0
            if isinstance(val, str):
                val = val.replace(",", "")
            try:
                return float(val)
            except ValueError:
                return 0.0

        if "withdrawal amt" in df.columns or "deposit amt" in df.columns:
            w_col, d_col = "withdrawal amt", "deposit amt"
        else:
            w_col, d_col = "debit amount", "credit amount"

        w_amt = df.get(w_col, pd.Series(dtype=float)).apply(clean_amt)
        d_amt = df.get(d_col, pd.Series(dtype=float)).apply(clean_amt)
        
        result["amount"] = w_amt + d_amt
        result["type"] = df.apply(
            lambda r: "DEBIT" if clean_amt(r.get(w_col, 0)) > 0 else "CREDIT", axis=1
        )
        
        result["balance"] = df.get("closing balance", pd.Series(dtype=float)).apply(clean_amt)
        
        result = result.dropna(subset=["date"])
        result = result[result["date"].notnull()]
        result = result[result["date"].dt.year > 2000]
        
        return result
