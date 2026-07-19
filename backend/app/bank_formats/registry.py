import importlib
import pkgutil
import pandas as pd
from typing import List, Tuple
from app.bank_formats.base import BaseBankParser

class UnknownBankFormatError(Exception):
    pass

class BankFormatRegistry:
    def __init__(self):
        self.parsers: List[BaseBankParser] = []

    def register(self, parser: BaseBankParser):
        self.parsers.append(parser)

    def detect_and_parse(self, df: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        best_score = 0.0
        best_parser = None

        for parser in self.parsers:
            try:
                score = parser.detect(df)
                if score > best_score:
                    best_score = score
                    best_parser = parser
            except Exception:
                continue
                
        # Handle tied scores using secondary heuristics? 
        # For now, pick the first best score. We can refine this later (Edge Case 2.2).
        
        if best_score < 0.5 or not best_parser:
            # Gather some diagnostic info to see what columns were actually read
            diagnostic_cols = [str(c).strip() for c in df.columns]
            raise UnknownBankFormatError(f"Could not identify the bank format with confidence. Top score: {best_score}. Detected columns: {diagnostic_cols[:10]}")

        normalized_df = best_parser.normalize(df)
        return best_parser.bank_name, normalized_df

registry = BankFormatRegistry()

# Auto-register parsers
import app.bank_formats
for loader, module_name, is_pkg in pkgutil.walk_packages(app.bank_formats.__path__):
    if module_name not in ["base", "registry"]:
        module = importlib.import_module(f"app.bank_formats.{module_name}")
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, BaseBankParser) and attribute is not BaseBankParser:
                registry.register(attribute())
