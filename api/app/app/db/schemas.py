import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "employee"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Collection Schemas
class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime.datetime
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    collection_id: Optional[int]
    status: str
    error_message: Optional[str]
    page_count: int
    chunk_count: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Source Citation Schema
class Citation(BaseModel):
    document_id: int
    filename: str
    page_number: int
    section_title: str
    snippet: str
    similarity_score: float

# Query Schemas
class QueryRequest(BaseModel):
    question: str
    collection_id: Optional[int] = None
    conversation_id: Optional[int] = None
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Citation]
    conversation_id: int
    latency_ms: float

# Conversation & Message Schemas
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources_json: Optional[Any] = None
    latency_ms: Optional[float] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: str
    collection_id: Optional[int]
    created_at: datetime.datetime
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True

# Evaluation Schemas
class EvalResultResponse(BaseModel):
    id: int
    question: str
    expected_answer: Optional[str]
    generated_answer: str
    cited_sources_json: Optional[Any]
    retrieval_score: float
    relevance_score: float
    hallucination_flag: bool
    latency_ms: float

    class Config:
        from_attributes = True

class EvalRunResponse(BaseModel):
    id: int
    name: str
    run_date: datetime.datetime
    config_json: Optional[Dict[str, Any]]
    avg_precision_k: float
    avg_relevance: float
    hallucination_rate: float
    avg_latency_ms: float
    results: Optional[List[EvalResultResponse]] = []

    class Config:
        from_attributes = True

class EvalRunRequest(BaseModel):
    name: Optional[str] = "Benchmark Run"
    collection_id: Optional[int] = None
    top_k: Optional[int] = 5
