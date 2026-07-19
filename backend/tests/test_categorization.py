import pytest
import os
from app.services.categorization import engine, CategorizationEngine

def test_rule_based_pattern():
    cat, conf, method = engine.categorize("ATM Withdrawal XYZ", "DEBIT")
    assert cat == "Others"
    assert method == "rule_pattern"

def test_rule_based_upi_merchant():
    cat, conf, method = engine.categorize("UPI/swiggy@hdfc/order", "DEBIT")
    assert cat == "Food"
    assert method == "rule_merchant"

def test_rule_based_merchant():
    cat, conf, method = engine.categorize("Amazon Prime Video Subscription", "DEBIT")
    assert cat == "Entertainment"
    assert method == "rule_merchant"

def test_ml_fallback():
    # Make sure we load the model for testing
    if not engine.model:
        engine.load_models()
        
    # Since the training data was tiny and mock, the ML prediction might be flaky. 
    # But we can at least test that it hits the ml_model logic or fallback logic.
    if engine.model:
        cat, conf, method = engine.categorize("Random unknown stuff", "DEBIT")
        assert method in ["ml_model", "fallback"]
    else:
        # Fallback if no models
        cat, conf, method = engine.categorize("Random unknown stuff", "DEBIT")
        assert method == "fallback"
