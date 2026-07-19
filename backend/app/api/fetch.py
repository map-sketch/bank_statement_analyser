from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.db_models import TransactionModel, AnalyticsCacheModel
import json

router = APIRouter()

@router.get("/analyze/{session_id}")
def get_analytics(session_id: str, db: Session = Depends(get_db)):
    cache = db.query(AnalyticsCacheModel).filter(AnalyticsCacheModel.session_id == session_id).first()
    if not cache:
        raise HTTPException(status_code=404, detail="Analytics not found for session")
    return json.loads(cache.value_json)

@router.get("/transactions/{session_id}")
def get_transactions(session_id: str, db: Session = Depends(get_db)):
    txns = db.query(TransactionModel).filter(TransactionModel.session_id == session_id).all()
    return txns
