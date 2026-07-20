import joblib
import os
from sqlalchemy.orm import Session
from core.models.db_models import TransactionModel
from core.rules.upi_parser import extract_upi_payee
from core.rules.merchant_dict import match_merchant
from core.rules.patterns import TRANSACTION_PATTERNS
from core.ml.preprocessor import preprocess_text
from core.config import settings

class CategorizationEngine:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        
    def load_models(self):
        if os.path.exists(settings.ML_MODEL_PATH) and os.path.exists(settings.ML_VECTORIZER_PATH):
            self.model = joblib.load(settings.ML_MODEL_PATH)
            self.vectorizer = joblib.load(settings.ML_VECTORIZER_PATH)
            
    def categorize(self, description: str, txn_type: str) -> tuple[str, float, str]:
        """Returns (Category, Confidence, Method)"""
        # 1. Rule-based: Pattern Matching
        for pattern, cat, _ in TRANSACTION_PATTERNS:
            if pattern.search(description):
                return cat, 1.0, "rule_pattern"

        # 2. Rule-based: UPI Payee extraction
        payee = extract_upi_payee(description)
        search_text = payee if payee else description
        
        # 3. Rule-based: Merchant Dictionary
        cat = match_merchant(search_text)
        if cat:
            return cat, 0.9, "rule_merchant"

        # 4. ML Fallback
        if self.model and self.vectorizer:
            clean_text = preprocess_text(description)
            if clean_text:
                X = self.vectorizer.transform([clean_text])
                pred_cat = self.model.predict(X)[0]
                probs = self.model.predict_proba(X)[0]
                confidence = max(probs)
                
                # Confidence thresholding
                if confidence >= 0.3:
                    return pred_cat, round(confidence, 2), "ml_model"
                    
        return "Others", 0.0, "fallback"

engine = CategorizationEngine()
engine.load_models()

def categorize_all(db: Session, session_id: str):
    txns = db.query(TransactionModel).filter(TransactionModel.session_id == session_id).all()
    
    for txn in txns:
        if txn.category is None:
            cat, conf, method = engine.categorize(txn.description, txn.type)
            txn.category = cat
            txn.category_confidence = conf
            txn.categorization_method = method
            
    db.commit()
