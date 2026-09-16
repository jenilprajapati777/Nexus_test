from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db, SessionLocal
from app.models.models import User, Corpus, Document, ProcessingJob
from app.schemas.schemas import CorpusCreate, CorpusResponse, DocumentResponse, JobStatusResponse
from app.api.deps import get_current_user
from app.ingestion.parsers import DocumentFileParser
from app.nlp.pipeline import SanskritNLPPipeline
from app.search.indexer import search_indexer

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])
nlp_pipeline = SanskritNLPPipeline()

def process_document_background(job_id: str, doc_id: str):
    """Background/Direct task handling NLP processing and Search Indexing with isolated DB session."""
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        doc = db.query(Document).filter(Document.id == doc_id).first()

        if not job or not doc:
            return

        # Step 1: Processing NLP
        job.status = "Processing"
        job.current_step = "Deterministic NLP Pipeline (Sandhi, Morphology, Samasa)"
        job.progress_pct = 40
        db.commit()

        nlp_result = nlp_pipeline.process_document(doc.original_text)

        # Update Document NLP data
        doc.nlp_data = nlp_result
        doc.character_count = nlp_result["character_count"]
        doc.word_count = nlp_result["word_count"]
        db.commit()

        # Step 2: Indexing
        job.status = "Indexing"
        job.current_step = "Multi-Layer Offset Index Construction"
        job.progress_pct = 85
        db.commit()

        doc_metadata = {
            "doc_id": doc.id,
            "corpus_id": doc.corpus_id,
            "title": doc.title,
            "author": doc.author,
            "chapter": doc.chapter,
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "original_text": doc.original_text
        }

        search_indexer.index_document(doc_id=doc.id, doc_metadata=doc_metadata, nlp_result=nlp_result)

        # Step 3: Complete
        job.status = "Ready"
        job.current_step = "Ingestion Complete"
        job.progress_pct = 100
        db.commit()

    except Exception as e:
        if job:
            job.status = "Failed"
            job.current_step = "Processing Error"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/corpora", response_model=CorpusResponse)
def create_corpus(corpus_in: CorpusCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    corpus = Corpus(
        title=corpus_in.title,
        description=corpus_in.description,
        owner_id=current_user.id
    )
    db.add(corpus)
    db.commit()
    db.refresh(corpus)
    return CorpusResponse(
        id=corpus.id,
        title=corpus.title,
        description=corpus.description,
        owner_id=corpus.owner_id,
        document_count=0,
        created_at=corpus.created_at
    )

@router.get("/corpora", response_model=List[CorpusResponse])
def list_corpora(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    corpora = db.query(Corpus).filter(Corpus.owner_id == current_user.id).all()
    res = []
    for c in corpora:
        doc_count = db.query(Document).filter(Document.corpus_id == c.id).count()
        res.append(CorpusResponse(
            id=c.id,
            title=c.title,
            description=c.description,
            owner_id=c.owner_id,
            document_count=doc_count,
            created_at=c.created_at
        ))
    return res

@router.post("/upload", response_model=JobStatusResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    corpus_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form("Unknown"),
    chapter: Optional[str] = Form("General"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not corpus_id:
        corpus = db.query(Corpus).filter(Corpus.owner_id == current_user.id).first()
        if not corpus:
            corpus = Corpus(title="Default Corpus", owner_id=current_user.id)
            db.add(corpus)
            db.commit()
            db.refresh(corpus)
        corpus_id = corpus.id
    else:
        corpus = db.query(Corpus).filter(Corpus.id == corpus_id, Corpus.owner_id == current_user.id).first()
        if not corpus:
            raise HTTPException(status_code=404, detail="Corpus not found or unauthorized")

    file_bytes = await file.read()
    file_name = file.filename
    file_type = file.filename.split('.')[-1].lower() if '.' in file.filename else "txt"

    original_text, metadata = DocumentFileParser.parse_file(file_bytes, file_name, file_type)
    doc_title = title or metadata.get("title") or file_name

    new_doc = Document(
        corpus_id=corpus_id,
        title=doc_title,
        author=author or metadata.get("author", "Unknown"),
        chapter=chapter or metadata.get("chapter", "General"),
        file_name=file_name,
        file_type=file_type,
        original_text=original_text,
        character_count=len(original_text),
        word_count=len(original_text.split())
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    assert new_doc.original_text == original_text, "Invariant Violated: Stored original text does not match uploaded text!"

    job = ProcessingJob(
        document_id=new_doc.id,
        corpus_id=corpus_id,
        user_id=current_user.id,
        status="Uploaded",
        current_step="File Ingested into Database",
        progress_pct=10
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Process immediately & synchronously so document is indexed right away
    process_document_background(job.id, new_doc.id)

    db.refresh(job)
    return JobStatusResponse(
        id=job.id,
        document_id=new_doc.id,
        corpus_id=corpus_id,
        status=job.status,
        current_step=job.current_step,
        progress_pct=job.progress_pct
    )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id, ProcessingJob.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(corpus_id: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Document).join(Corpus).filter(Corpus.owner_id == current_user.id)
    if corpus_id:
        query = query.filter(Document.corpus_id == corpus_id)
    return query.all()
