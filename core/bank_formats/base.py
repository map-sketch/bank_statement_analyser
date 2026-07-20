from abc import ABC, abstractmethod
import pandas as pd

class BaseBankParser(ABC):
    @abstractmethod
    def detect(self, df: pd.DataFrame) -> float:
        """Return confidence 0.0-1.0 that this DataFrame matches this bank format."""
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return DataFrame with standard columns: date, description, amount, type, balance."""
        pass

    @property
    @abstractmethod
    def bank_name(self) -> str:
        """Name of the bank this parser handles."""
        pass
