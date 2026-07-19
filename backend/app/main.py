from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB, load ML model
    init_db()
    yield
    # Shutdown: cleanup

app = FastAPI(
    title="Bank Statement Analyzer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Privacy-First AI Bank Statement Analyzer API"}

from app.api.upload import router as upload_router
from app.api.fetch import router as fetch_router
app.include_router(upload_router, prefix="/api")
app.include_router(fetch_router, prefix="/api")
