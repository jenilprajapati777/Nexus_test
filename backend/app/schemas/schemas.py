from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime

# Auth Schemas
class UserRegister(BaseModel):
    email: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime

# Ingestion Schemas
class CorpusCreate(BaseModel):
    title: str
    description: Optional[str] = None

class CorpusResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    document_count: int = 0
    created_at: datetime

class DocumentResponse(BaseModel):
    id: str
    corpus_id: str
    title: str
    author: Optional[str]
    chapter: Optional[str]
    file_name: str
    file_type: str
    character_count: int
    word_count: int
    created_at: datetime
    original_text: str

class JobStatusResponse(BaseModel):
    id: str
    document_id: str
    corpus_id: str
    status: str
    current_step: str
    progress_pct: int
    error_message: Optional[str] = None

# Search Schemas
class SearchQueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "enhanced" # baseline or enhanced
    corpus_ids: Optional[List[str]] = None
    author_filter: Optional[str] = None
    chapter_filter: Optional[str] = None
    top_k: Optional[int] = 10

class ExplainRequest(BaseModel):
    doc_id: str
    query: str

# Evaluation Schemas
class BenchmarkQueryCreate(BaseModel):
    query_text: str
    description: Optional[str] = None
    category: Optional[str] = "Sandhi & Morphology"
    gold_relevance: Dict[str, int]

# Admin Schemas
class RuleCreate(BaseModel):
    rule_code: str
    category: str
    name: str
    pattern: str
    replacement: str
    description: Optional[str] = None
    active: Optional[bool] = True
