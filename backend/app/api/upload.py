import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.config import settings
from app.services.ingestion import process_upload
from app.models.schemas import UploadResponse
from app.bank_formats.registry import UnknownBankFormatError

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_statement(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Edge Case 1.1.3: Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xls", ".xlsx"]:
        raise HTTPException(status_code=400, detail="Invalid file extension. Only .csv, .xls, .xlsx allowed.")

    # Edge Case 15.1: Sanitize filename (basic prevention)
    filename = os.path.basename(file.filename)
    
    # Check max file size via seeking (or let fastapi handle it with max length, 
    # but simplest is just checking length on read or using middleware, 
    # we can do it by reading a chunk or checking content length header)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # File size check
        if os.path.getsize(temp_path) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            os.remove(temp_path)
            raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit.")
            
        if os.path.getsize(temp_path) == 0:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        response = process_upload(temp_path, filename, db)
        return response

    except UnknownBankFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Edge Case 14.4: Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
