import re

TRANSACTION_PATTERNS = [
    # (pattern, category, description)
    (re.compile(r'ATM[-/\s]', re.I), "Others", "ATM Withdrawal"),
    (re.compile(r'NEFT[-/\s]', re.I), "Self-Transfers", "Bank Transfer"),
    (re.compile(r'RTGS[-/\s]', re.I), "Self-Transfers", "Bank Transfer"),
    (re.compile(r'IMPS[-/\s]', re.I), "Self-Transfers", "Bank Transfer"),
    (re.compile(r'EMI[-/\s]', re.I), "EMI/Loans", "EMI Payment"),
    (re.compile(r'NACH[-/\s]', re.I), "EMI/Loans", "Auto-Debit"),
    (re.compile(r'INT\.?\s*PAID', re.I), "EMI/Loans", "Interest"),
    (re.compile(r'DIVIDEND', re.I), "Investments", "Dividend"),
]
