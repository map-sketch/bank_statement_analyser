from typing import Optional

MERCHANT_CATEGORIES = {
    "Food": [
        "swiggy", "zomato", "dominos", "mcdonalds", "kfc",
        "burger king", "pizza hut", "restaurant", "cafe", "bakery",
        "dunkin", "subway", "biryani", "food"
    ],
    "Coffee": [
        "starbucks", "cafe coffee day", "third wave", "blue tokai", "coffee"
    ],
    "Grocery": [
        "blinkit", "zepto", "instamart", "bigbasket", "swiggy instamart",
        "supermarket", "grocery", "dmart", "reliance fresh"
    ],
    "Entertainment": [
        "netflix", "hotstar", "prime video", "bookmyshow", "spotify",
        "gaana", "youtube premium", "gaming", "playstation", "xbox",
        "inox", "pvr", "zee5", "sonyliv"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa",
        "tata cliq", "croma", "reliance digital", "decathlon"
    ],
    "Travel": [
        "makemytrip", "goibibo", "agoda", "cleartrip", "irctc", "flight",
        "indigo", "spicejet", "vistara", "hotel", "airbnb", "yatra",
        "redbus", "abhibus", "ixigo"
    ],
    "local commute": [
        "uber", "ola", "rapido", "metro", "petrol", "fuel",
        "hp pump", "indian oil", "bharat petroleum", "toll", "parking", "namma metro"
    ],
    "Utilities": [
        "electricity", "broadband", "jio", "airtel", "vodafone", "vi",
        "water bill", "gas bill", "bsnl", "act fibernet", "tata sky",
        "dish tv"
    ],
    "Investments": [
        "mutual fund", "zerodha", "groww", "upstox", "kuvera", "sip",
        "fixed deposit", "fd", "ppf", "nps", "stocks", "coin"
    ],
    "Rent": [
        "rent", "house rent", "landlord", "property", "pg", "hostel"
    ],
    "EMI/Loans": [
        "emi", "loan", "bajaj finserv", "hdfc loan", "personal loan",
        "home loan", "car loan", "education loan"
    ],
    "Donation": [
        "donation", "charity", "ngo", "giveindia", "ketto", "milaap"
    ],
    "Personal": [
        "salon", "spa", "haircut", "pharmacy", "medical", "hospital", "clinic"
    ],
    "Self-Transfers": [
        "self transfer", "own account", "sweep", "neft self",
        "imps self", "fund transfer self"
    ],
    "Salary/Income": [
        "salary", "payroll", "stipend", "freelance", "consulting fee"
    ],
    "Others": []
}

import re

def match_merchant(description: str) -> Optional[str]:
    # Edge case 4.2.6: overlap handling, prioritize longer phrases or exact boundaries if needed.
    # For now, simplistic matching.
    desc_lower = description.lower()
    for category, keywords in MERCHANT_CATEGORIES.items():
        if category == "Others":
            continue
        for keyword in keywords:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, desc_lower):
                return category
    return None
