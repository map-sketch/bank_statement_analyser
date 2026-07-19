import re

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    
    # Mask IFSC codes (4 letters, a zero, 6 alphanumeric)
    text = re.sub(r'[a-z]{4}0[a-z0-9]{6}', ' ifsc_code ', text)
    # Mask phone numbers / long numeric strings (4+ digits)
    text = re.sub(r'\d{4,}', ' num_seq ', text)
    
    text = re.sub(r'[^a-z0-9\s_]', ' ', text)  # Remove special chars (keep underscores for our tokens)
    text = re.sub(r'\s+', ' ', text).strip()    # Normalize whitespace
    
    # Remove common noise words
    noise = {"upi", "neft", "imps", "rtgs", "txn", "ref", "cr", "dr", "to", "from"}
    tokens = [t for t in text.split() if t not in noise and len(t) > 1]
    return ' '.join(tokens)
