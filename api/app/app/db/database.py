import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings, IS_VERCEL

db_url = settings.DATABASE_URL
if IS_VERCEL or os.name != "nt":
    db_url = "sqlite:////tmp/rag_assistant.db"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_tables_created = False

def init_db():
    global _tables_created
    if not _tables_created:
        try:
            Base.metadata.create_all(bind=engine)
            _tables_created = True
        except Exception as e:
            print(f"[DB Warning] Auto create_all warning: {e}")

def get_db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
