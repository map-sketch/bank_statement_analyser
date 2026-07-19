import pytest
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.bank_formats.registry import registry, UnknownBankFormatError

client = TestClient(app)

def test_hdfc_detection():
    data = {
        "Date": ["01/01/2025"],
        "Narration": ["Test txn"],
        "Withdrawal Amt": [100.0],
        "Deposit Amt": [None],
        "Closing Balance": [5000.0]
    }
    df = pd.DataFrame(data)
    bank_name, norm_df = registry.detect_and_parse(df)
    assert bank_name == "HDFC"
    assert len(norm_df) == 1
    assert "date" in norm_df.columns
    assert "amount" in norm_df.columns

def test_sbi_detection():
    data = {
        "Txn Date": ["01-01-2025"],
        "Description": ["Test txn"],
        "Debit": [None],
        "Credit": [200.0],
        "Balance": [5200.0]
    }
    df = pd.DataFrame(data)
    bank_name, norm_df = registry.detect_and_parse(df)
    assert bank_name == "SBI"
    assert len(norm_df) == 1

def test_unknown_format_error():
    data = {
        "Col1": ["data"],
        "Col2": ["data"]
    }
    df = pd.DataFrame(data)
    with pytest.raises(UnknownBankFormatError):
        registry.detect_and_parse(df)

# We can also test the upload endpoint by mocking the file
def test_invalid_extension():
    response = client.post("/api/upload", files={"file": ("test.png", b"fake image content", "image/png")})
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]
