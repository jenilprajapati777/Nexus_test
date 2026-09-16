from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User, Document, ProcessingJob, Corpus, LinguisticRule
from app.schemas.schemas import RuleCreate
from app.api.deps import get_current_user
from app.search.indexer import search_indexer
from app.nlp.sandhi import SandhiEngine

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
sandhi_engine = SandhiEngine()

@router.get("/health")
def get_system_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_count = db.query(User).count()
    corpus_count = db.query(Corpus).count()
    document_count = db.query(Document).count()
    job_count = db.query(ProcessingJob).count()

    total_indexed_terms = sum(len(terms) for terms in search_indexer.index.values())

    return {
        "status": "Healthy",
        "system_version": "1.0.0",
        "database": "Operational (SQLite / PostgreSQL)",
        "nlp_engine": "Rule-Based Deterministic active",
        "telemetry": {
            "total_users": user_count,
            "total_corpora": corpus_count,
            "total_documents": document_count,
            "total_jobs": job_count,
            "total_indexed_terms": total_indexed_terms
        }
    }

@router.get("/jobs")
def list_system_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).limit(50).all()
    return jobs

@router.get("/rules")
def list_linguistic_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rules = db.query(LinguisticRule).all()
    if not rules:
        # Seed rules from SandhiEngine
        for r in sandhi_engine.rules:
            lr = LinguisticRule(
                rule_code=r.rule_id,
                category=r.category,
                name=r.rule_id,
                pattern=r.pattern,
                replacement=f"{r.replace_part1} + {r.replace_part2}",
                description=r.description,
                active=True
            )
            db.add(lr)
        db.commit()
        rules = db.query(LinguisticRule).all()
    return rules

@router.post("/rules")
def create_linguistic_rule(rule_in: RuleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(LinguisticRule).filter(LinguisticRule.rule_code == rule_in.rule_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule code already exists")
    
    rule = LinguisticRule(
        rule_code=rule_in.rule_code,
        category=rule_in.category,
        name=rule_in.name,
        pattern=rule_in.pattern,
        replacement=rule_in.replacement,
        description=rule_in.description,
        active=rule_in.active if rule_in.active is not None else True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
