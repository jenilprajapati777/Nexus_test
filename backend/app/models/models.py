import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, researcher, user
    created_at = Column(DateTime, default=datetime.utcnow)

    corpora = relationship("Corpus", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="user", cascade="all, delete-orphan")


class Corpus(Base):
    __tablename__ = "corpora"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="corpora")
    documents = relationship("Document", back_populates="corpus", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    corpus_id = Column(String, ForeignKey("corpora.id"), nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True, default="Unknown")
    chapter = Column(String, nullable=True, default="General")
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    
    # Absolute invariant: untouched original text preserved exactly as uploaded
    original_text = Column(Text, nullable=False)
    character_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    
    # Store NLP derived representations & character offset mapping index as JSON
    nlp_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    corpus = relationship("Corpus", back_populates="documents")
    job = relationship("ProcessingJob", back_populates="document", uselist=False, cascade="all, delete-orphan")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    corpus_id = Column(String, ForeignKey("corpora.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Pipeline stages: Uploaded -> Processing -> Indexing -> Ready (or Failed)
    status = Column(String, default="Uploaded", nullable=False)
    current_step = Column(String, default="File Parsing", nullable=False)
    progress_pct = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="jobs")
    document = relationship("Document", back_populates="job")


class LinguisticRule(Base):
    __tablename__ = "linguistic_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    rule_code = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # SANDHI, MORPHOLOGY, SAMASA, NORMALIZATION
    name = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    replacement = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)


class BenchmarkQuery(Base):
    __tablename__ = "benchmark_queries"

    id = Column(String, primary_key=True, default=generate_uuid)
    query_text = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="Sandhi & Morphology")
    # Expected document IDs mapped to relevance score (e.g. {"doc_id_1": 3, "doc_id_2": 1})
    gold_relevance = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
