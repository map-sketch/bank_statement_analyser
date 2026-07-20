from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class SessionModel(Base):
    __tablename__ = "sessions"
    id          = Column(String, primary_key=True)        # UUID
    filename    = Column(String, nullable=False)
    bank_name   = Column(String, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    expires_at  = Column(DateTime)
    transactions = relationship("TransactionModel", back_populates="session")
    analytics = relationship("AnalyticsCacheModel", back_populates="session")

class TransactionModel(Base):
    __tablename__ = "transactions"
    id                     = Column(Integer, primary_key=True, autoincrement=True)
    session_id             = Column(String, ForeignKey("sessions.id"))
    date                   = Column(Date, nullable=False)
    description            = Column(String, nullable=False)
    amount                 = Column(Float, nullable=False)
    type                   = Column(String, nullable=False)          # CREDIT / DEBIT
    balance                = Column(Float, nullable=True)
    category               = Column(String, nullable=True)
    category_confidence    = Column(Float, nullable=True)
    categorization_method  = Column(String, nullable=True)           # rule / ml
    is_avoidable           = Column(Boolean, default=True)
    is_user_overridden     = Column(Boolean, default=False)
    is_salary              = Column(Boolean, default=False)
    is_anomaly             = Column(Boolean, default=False)
    
    session                = relationship("SessionModel", back_populates="transactions")

class AnalyticsCacheModel(Base):
    __tablename__ = "analytics_cache"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(String, ForeignKey("sessions.id"))
    key         = Column(String, nullable=False)
    value_json  = Column(String, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    session     = relationship("SessionModel", back_populates="analytics")
