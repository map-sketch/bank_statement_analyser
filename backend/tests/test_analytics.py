import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

from app.models.db_models import Base, SessionModel, TransactionModel, AnalyticsCacheModel
from app.services.analytics import compute_analytics

# In-memory SQLite for fast testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_salary_detection(db):
    session_id = "test-session"
    db.add(SessionModel(id=session_id, filename="test.csv", bank_name="HDFC"))
    db.flush()

    # Add a salary transaction
    db.add(TransactionModel(
        session_id=session_id,
        date=date(2025, 1, 1),
        description="Salary for Jan",
        amount=50000.0,
        type="CREDIT",
        category="Salary/Income"
    ))
    db.commit()

    compute_analytics(db, session_id)
    
    # Check if is_salary was set
    txn = db.query(TransactionModel).first()
    assert txn.is_salary == True

def test_anomaly_filtering(db):
    session_id = "test-session"
    db.add(SessionModel(id=session_id, filename="test.csv", bank_name="HDFC"))
    db.flush()

    # Add standard daily spends (~500/day)
    for i in range(1, 11):
        db.add(TransactionModel(
            session_id=session_id,
            date=date(2025, 1, i),
            description=f"Food {i}",
            amount=500.0,
            type="DEBIT",
            category="Food"
        ))
    
    # Add an anomaly (e.g. 5000)
    db.add(TransactionModel(
        session_id=session_id,
        date=date(2025, 1, 11),
        description="Big purchase",
        amount=5000.0,
        type="DEBIT",
        category="Shopping"
    ))
    db.commit()

    compute_analytics(db, session_id)
    
    # The big purchase should be flagged as an anomaly since avg spend is ~500 and 5000 > 1500 (3x)
    anomaly_txns = db.query(TransactionModel).filter(TransactionModel.is_anomaly == True).all()
    assert len(anomaly_txns) == 1
    assert anomaly_txns[0].amount == 5000.0

def test_avoidability_engine(db):
    session_id = "test-session"
    db.add(SessionModel(id=session_id, filename="test.csv", bank_name="HDFC"))
    db.flush()

    db.add(TransactionModel(session_id=session_id, date=date(2025, 1, 1), description="Pizza", amount=100.0, type="DEBIT", category="Food"))
    db.add(TransactionModel(session_id=session_id, date=date(2025, 1, 2), description="Rent", amount=1000.0, type="DEBIT", category="Rent"))
    db.commit()

    compute_analytics(db, session_id)

    food_txn = db.query(TransactionModel).filter(TransactionModel.category == "Food").first()
    rent_txn = db.query(TransactionModel).filter(TransactionModel.category == "Rent").first()

    assert food_txn.is_avoidable == True
    assert rent_txn.is_avoidable == False
