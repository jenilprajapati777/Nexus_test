from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api import auth, ingestion, search, evaluation, admin
from app.models.models import Document
from app.nlp.pipeline import SanskritNLPPipeline
from app.search.indexer import search_indexer

# Initialize DB tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan hook to index all existing database documents into search indexer on startup."""
    db = SessionLocal()
    pipeline = SanskritNLPPipeline()
    try:
        documents = db.query(Document).all()
        for doc in documents:
            if doc.original_text:
                nlp_res = doc.nlp_data or pipeline.process_document(doc.original_text)
                meta = {
                    "doc_id": doc.id,
                    "corpus_id": doc.corpus_id,
                    "title": doc.title,
                    "author": doc.author,
                    "chapter": doc.chapter,
                    "file_name": doc.file_name,
                    "file_type": doc.file_type,
                    "original_text": doc.original_text
                }
                search_indexer.index_document(doc_id=doc.id, doc_metadata=meta, nlp_result=nlp_res)
    except Exception as e:
        print(f"Startup indexing warning: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sanskrit Information Retrieval Enhancement Platform with Deterministic Rule-Based NLP Pipeline, Offset Match Highlighting, and Ablation Study Suite.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(ingestion.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(evaluation.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Sanskrit Retrieval Enhancement Platform API",
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
