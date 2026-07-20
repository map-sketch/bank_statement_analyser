import pandas as pd
from core.bank_formats.base import BaseBankParser

class SbiParser(BaseBankParser):
    @property
    def bank_name(self) -> str:
        return "SBI"

    def _clean_col(self, col: str) -> str:
        return str(col).strip().lower().replace('.', '').replace('\n', ' ')

    def _find_col(self, df: pd.DataFrame, aliases: set) -> str:
        for orig in df.columns:
            cleaned = self._clean_col(orig)
            if cleaned in aliases:
                return orig
        for orig in df.columns:
            cleaned = self._clean_col(orig)
            for alias in aliases:
                if alias in cleaned:
                    return orig
        return None

    def detect(self, df: pd.DataFrame) -> float:
        actual = {self._clean_col(c) for c in df.columns}
        sbi_core = {"txn date", "value date", "description", "ref no/cheque no", "debit", "credit"}
        
        # Check overlap
        overlap = len(sbi_core.intersection(actual)) / len(sbi_core)
        if overlap > 0.6:
            return overlap
        return 0.0

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        date_col = self._find_col(df, {"txn date", "date", "transaction date"})
        desc_col = self._find_col(df, {"description", "particulars", "narration"})
        debit_col = self._find_col(df, {"debit", "withdrawal"})
        credit_col = self._find_col(df, {"credit", "deposit"})
        bal_col = self._find_col(df, {"balance"})
        
        result = pd.DataFrame()
        result["date"] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        result["description"] = df[desc_col].astype(str)
        
        def clean_amt(val):
            if pd.isna(val) or val == "" or str(val).strip() == "": return 0.0
            if isinstance(val, str): val = val.replace(",", "").strip()
            try: return float(val)
            except ValueError: return 0.0

        w_amt = df[debit_col].apply(clean_amt) if debit_col else pd.Series([0.0]*len(df))
        d_amt = df[credit_col].apply(clean_amt) if credit_col else pd.Series([0.0]*len(df))
        
        result["amount"] = w_amt + d_amt
        result["type"] = w_amt.apply(lambda x: "DEBIT" if x > 0 else "CREDIT")
        
        if bal_col:
            result["balance"] = df[bal_col].apply(clean_amt)
        else:
            result["balance"] = None
            
        result = result.dropna(subset=["date"])
        result = result[result["date"].notnull()]
        result = result[result["date"].dt.year > 2000]
        
        return result
