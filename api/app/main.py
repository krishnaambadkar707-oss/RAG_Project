import os
import sys

# Ensure backend directory is in sys.path so 'app' imports work from anywhere
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings, IS_VERCEL
from app.db.database import engine, Base, SessionLocal
from app.db.models import User, Collection
from app.services.auth_service import get_password_hash
from app.routers import auth, collections, documents, query, conversations, evaluation

try:
    Base.metadata.create_all(bind=engine)
except Exception as _e:
    print(f"[DB Warning] Module load table creation: {_e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Enterprise RAG Knowledge Assistant REST API",
    version="1.0.0"
)

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    print(f"[Global Server Error] {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Unhandled Server Exception",
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc()
        }
    )

# Enable CORS for local development and frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers (Direct and /api prefixed for Vercel serverless routing)
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

@api_router.get("/health", tags=["Health"])
def health_check_api():
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "active"
    }

api_router.include_router(auth.router)
api_router.include_router(collections.router)
api_router.include_router(documents.router)
api_router.include_router(query.router)
api_router.include_router(conversations.router)
api_router.include_router(evaluation.router)

app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    from app.config import IS_VERCEL
    if IS_VERCEL:
        print("[Startup] Skipping startup seeding on Vercel serverless runtime.")
        return

    db = SessionLocal()
    try:
        # Pre-load embedding model so first query request responds instantly
        try:
            from app.services.embedding_service import get_embedding_model
            print("[Startup] Warming up embedding model...")
            get_embedding_model()
            print("[Startup] Embedding model initialized successfully.")
        except Exception as emb_err:
            print(f"[Startup Warning] Embedding model warmup warning: {emb_err}")


        # Seed default Admin User if database is empty
        admin_user = db.query(User).filter(User.email == "admin@company.com").first()
        if not admin_user:
            admin = User(
                email="admin@company.com",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
        
        employee_user = db.query(User).filter(User.email == "demo@company.com").first()
        if not employee_user:
            emp = User(
                email="demo@company.com",
                password_hash=get_password_hash("password123"),
                role="employee"
            )
            db.add(emp)

        # Seed default Collections
        hr_coll = db.query(Collection).filter(Collection.name == "HR & Policy").first()
        if not hr_coll:
            hr_coll = Collection(name="HR & Policy", description="Internal enterprise HR policies and leave guides")
            db.add(hr_coll)

        it_coll = db.query(Collection).filter(Collection.name == "IT & Operations").first()
        if not it_coll:
            it_coll = Collection(name="IT & Operations", description="IT setup, VPN access, and security guides")
            db.add(it_coll)

        eng_coll = db.query(Collection).filter(Collection.name == "Engineering & Architecture").first()
        if not eng_coll:
            eng_coll = Collection(name="Engineering & Architecture", description="Core platform architecture specifications")
            db.add(eng_coll)

        db.commit()
        db.refresh(hr_coll)
        db.refresh(it_coll)
        db.refresh(eng_coll)

        # Skip slow file re-parsing on serverless cold starts (database already contains pre-parsed records)
        from app.config import IS_VERCEL, BASE_DIR
        if not IS_VERCEL:
            seed_dirs = [
                (os.path.join(BASE_DIR, "data", "sample_documents"), hr_coll.id),
                (os.path.join(BASE_DIR, "uploads"), hr_coll.id),
            ]

            from app.db.models import Document
            from app.services.document_parser import parse_document
            from app.services.chunking_service import chunk_document
            from app.services.vector_store import vector_store

            for s_dir, default_coll_id in seed_dirs:
                if not os.path.exists(s_dir):
                    continue
                for fname in os.listdir(s_dir):
                    fpath = os.path.join(s_dir, fname)
                    if not os.path.isfile(fpath):
                        continue
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
                        continue

                    coll_id = default_coll_id
                    if "IT" in fname:
                        coll_id = it_coll.id
                    elif "Eng" in fname or "PRD" in fname:
                        coll_id = eng_coll.id

                    existing_doc = db.query(Document).filter(Document.filename == fname).first()
                    if not existing_doc:
                        new_doc = Document(
                            filename=fname,
                            collection_id=coll_id,
                            file_path=fpath,
                            status="pending"
                        )
                        db.add(new_doc)
                        db.commit()
                        db.refresh(new_doc)
                        existing_doc = new_doc

                    if existing_doc.status != "processed":
                        try:
                            parse_res = parse_document(fpath)
                            if parse_res and parse_res.pages:
                                chunks = chunk_document(parse_res, document_id=existing_doc.id, filename=fname, collection_id=coll_id)
                                vector_store.add_chunks(chunks)
                                existing_doc.status = "processed"
                                existing_doc.page_count = parse_res.total_pages
                                existing_doc.chunk_count = len(chunks)
                                db.commit()
                        except Exception as parse_err:
                            print(f"[Seed Document Warning] {fname}: {parse_err}")

    except Exception as e:
        print(f"[Startup Warning] Seeding failed: {e}")
    finally:
        db.close()

@app.get("/", include_in_schema=False)
def read_root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "docs": "/docs",
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "llm_provider": settings.LLM_PROVIDER
    }

@app.get("/health", tags=["Health"])
def health_check_app():
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "active"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

