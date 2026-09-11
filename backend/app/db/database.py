import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings, IS_VERCEL, BASE_DIR

db_url = settings.DATABASE_URL
target_tmp_db = "/tmp/rag_assistant.db"

if IS_VERCEL or os.name != "nt":
    if not os.path.exists(target_tmp_db) or os.path.getsize(target_tmp_db) == 0:
        candidate_seeds = [
            os.path.join(BASE_DIR, "rag_assistant.db"),
            os.path.join(BASE_DIR, "backend", "rag_assistant.db"),
            os.path.join(BASE_DIR, "api", "rag_assistant.db"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "rag_assistant.db")
        ]
        for seed_path in candidate_seeds:
            if os.path.exists(seed_path) and os.path.getsize(seed_path) > 0:
                try:
                    shutil.copy2(seed_path, target_tmp_db)
                    print(f"[Database Hydration] Copied pre-populated DB from {seed_path} to {target_tmp_db}")
                    break
                except Exception as copy_err:
                    print(f"[Database Hydration Warning] Failed copying seed DB: {copy_err}")
    db_url = f"sqlite:///{target_tmp_db}"

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
