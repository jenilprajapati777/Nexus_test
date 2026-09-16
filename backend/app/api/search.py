from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import User, Corpus, Document
from app.schemas.schemas import SearchQueryRequest, ExplainRequest
from app.api.deps import get_current_user
from app.search.engine import SearchEngine
from app.search.explainer import MatchExplainer
from app.search.indexer import search_indexer

router = APIRouter(prefix="/search", tags=["Search Engine"])
search_engine = SearchEngine()

@router.post("/query")
def execute_search(
    req: SearchQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve user's owned corpus IDs to enforce strict data isolation
    user_corpora = db.query(Corpus).filter(Corpus.owner_id == current_user.id).all()
    user_corpus_ids = [c.id for c in user_corpora]

    # Filter corpus IDs to user's permissions
    effective_corpus_ids = user_corpus_ids
    if req.corpus_ids:
        effective_corpus_ids = [cid for cid in req.corpus_ids if cid in user_corpus_ids]

    results = search_engine.search(
        query=req.query,
        mode=req.mode or "enhanced",
        corpus_ids=effective_corpus_ids,
        author_filter=req.author_filter,
        chapter_filter=req.chapter_filter,
        top_k=req.top_k or 10
    )

    return results

@router.post("/explain")
def explain_search_match(
    req: ExplainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify document ownership
    doc = db.query(Document).join(Corpus).filter(
        Document.id == req.doc_id,
        Corpus.owner_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied")

    # Run search hit lookup
    search_res = search_engine.search(query=req.query, mode="enhanced", corpus_ids=[doc.corpus_id], top_k=50)
    matched_hit = None
    for hit in search_res.get("hits", []):
        if hit["doc_id"] == req.doc_id:
            matched_hit = hit
            break

    if not matched_hit:
        return {
            "doc_id": req.doc_id,
            "query": req.query,
            "total_score": 0.0,
            "total_matches": 0,
            "explanation_steps": [{"description": "No matches found for this document."}]
        }

    return MatchExplainer.explain_hit(matched_hit, req.query)
