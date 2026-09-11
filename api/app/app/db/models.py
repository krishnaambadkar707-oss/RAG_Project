import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="employee") # admin | employee
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="collection")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending") # pending | processed | failed
    error_message = Column(Text, nullable=True)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    collection = relationship("Collection", back_populates="documents")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    collection = relationship("Collection", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False) # user | assistant
    content = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    run_date = Column(DateTime, default=datetime.datetime.utcnow)
    config_json = Column(JSON, nullable=True)
    avg_precision_k = Column(Float, default=0.0)
    avg_relevance = Column(Float, default=0.0)
    hallucination_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)

    results = relationship("EvalResult", back_populates="eval_run", cascade="all, delete-orphan")

class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    eval_run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False)
    question = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=True)
    generated_answer = Column(Text, nullable=False)
    cited_sources_json = Column(JSON, nullable=True)
    retrieval_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    hallucination_flag = Column(Boolean, default=False)
    latency_ms = Column(Float, default=0.0)

    eval_run = relationship("EvalRun", back_populates="results")
