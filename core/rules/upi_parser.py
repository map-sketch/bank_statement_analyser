import re
from typing import Optional

UPI_PATTERNS = [
    re.compile(r'UPI[-/](?:CR/|DR/)?(?P<payee>[^/@]+?)(?:@[a-z]+)?[-/]', re.I),
    re.compile(r'(?:GPay|PhonePe)[-/](?P<payee>[^/@]+?)(?:@[a-z]+)?[-/]', re.I),
    re.compile(r'UPI/(?:[A-Za-z0-9]+)?/(?P<payee>[^/@]+?)(?:@[a-z]+)?/', re.I),
]

def extract_upi_payee(description: str) -> Optional[str]:
    for pattern in UPI_PATTERNS:
        match = pattern.search(description)
        if match:
            return match.group('payee').strip()
    return None
