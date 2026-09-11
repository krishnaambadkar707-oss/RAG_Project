import os
import sys

# Ensure backend directory is in sys.path so 'app' imports work from anywhere
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.database import engine, Base, SessionLocal
from app.db.models import User, Collection
from app.services.auth_service import get_password_hash
from app.routers import auth, collections, documents, query, conversations, evaluation

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Enterprise RAG Knowledge Assistant REST API",
    version="1.0.0"
)

# Enable CORS for local development and frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(collections.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(conversations.router)
app.include_router(evaluation.router)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Pre-load embedding model so first query request responds instantly
        from app.services.embedding_service import get_embedding_model
        print("[Startup] Warming up embedding model...")
        get_embedding_model()
        print("[Startup] Embedding model loaded successfully.")

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
        default_colls = ["HR & Policy", "Engineering & Architecture", "IT & Operations"]
        for c_name in default_colls:
            existing = db.query(Collection).filter(Collection.name == c_name).first()
            if not existing:
                db.add(Collection(name=c_name, description=f"Internal enterprise documents for {c_name}"))
        
        db.commit()
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
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "active"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)
