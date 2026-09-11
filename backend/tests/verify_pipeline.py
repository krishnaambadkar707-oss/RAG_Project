import os
import sys

# Ensure backend package path is present
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Collection, Document
from app.services.auth_service import get_password_hash
from app.services.document_parser import parse_document
from app.services.chunking_service import chunk_document
from app.services.vector_store import vector_store
from app.services.llm_service import generate_grounded_answer
from app.services.eval_service import run_evaluation_suite

def test_full_pipeline():
    print("=== Step 1: Initializing DB & Creating Tables ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create admin user if not exists
    admin = db.query(User).filter(User.email == "admin@company.com").first()
    if not admin:
        admin = User(email="admin@company.com", password_hash=get_password_hash("admin123"), role="admin")
        db.add(admin)

    # Create default HR and IT collections
    hr_coll = db.query(Collection).filter(Collection.name == "HR & Policy").first()
    if not hr_coll:
        hr_coll = Collection(name="HR & Policy", description="Internal HR Policies")
        db.add(hr_coll)

    it_coll = db.query(Collection).filter(Collection.name == "IT & Operations").first()
    if not it_coll:
        it_coll = Collection(name="IT & Operations", description="IT & Security Guides")
        db.add(it_coll)

    eng_coll = db.query(Collection).filter(Collection.name == "Engineering & Architecture").first()
    if not eng_coll:
        eng_coll = Collection(name="Engineering & Architecture", description="Core Platform Architecture Specs")
        db.add(eng_coll)

    db.commit()
    db.refresh(hr_coll)
    db.refresh(it_coll)
    db.refresh(eng_coll)

    print(f"Collections initialized: HR ID={hr_coll.id}, IT ID={it_coll.id}, ENG ID={eng_coll.id}")

    print("\n=== Step 2: Ingesting Sample Enterprise Documents ===")
    sample_files = [
        ("HR_Policy.txt", hr_coll.id),
        ("IT_Setup_Guide.txt", it_coll.id),
        ("Engineering_Architecture.txt", eng_coll.id)
    ]

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_documents"))

    for filename, coll_id in sample_files:
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found.")
            continue

        doc = db.query(Document).filter(Document.filename == filename).first()
        if not doc:
            doc = Document(filename=filename, collection_id=coll_id, file_path=file_path, status="pending")
            db.add(doc)
            db.commit()
            db.refresh(doc)

        parse_res = parse_document(file_path)
        chunks = chunk_document(parse_res, document_id=doc.id, filename=filename, collection_id=coll_id)
        vector_store.add_chunks(chunks)

        doc.status = "processed"
        doc.page_count = parse_res.total_pages
        doc.chunk_count = len(chunks)
        db.commit()

        print(f"Ingested '{filename}': {parse_res.total_pages} pages, {len(chunks)} chunks added to ChromaDB.")

    print("\n=== Step 3: Verifying RAG Query Retrieval & Answer Grounding ===")
    test_queries = [
        ("What is the annual leave policy for full-time employees?", hr_coll.id),
        ("How do I request a VPN certificate?", it_coll.id),
        ("What database is used for platform persistence?", eng_coll.id),
        ("What is the secret recipe for baking sourdough bread?", None) # Out of scope
    ]

    for q, coll_id in test_queries:
        print(f"\nQUERY: '{q}' (Scope collection_id={coll_id})")
        citations = vector_store.search(query=q, collection_id=coll_id, top_k=5)
        answer, sources, latency = generate_grounded_answer(query=q, citations=citations)

        print(f"LATENCY: {latency} ms")
        print(f"CITATIONS ({len(sources)}): {[c.filename + ' p.' + str(c.page_number) for c in sources]}")
        print(f"ANSWER:\n{answer}")

    print("\n=== Step 4: Triggering Benchmark Evaluation Run ===")
    eval_run = run_evaluation_suite(db=db, name="Initial Test Suite Run")

    print("\nEVALUATION RESULTS SCORECARD:")
    print(f" - Run ID: {eval_run.id}")
    print(f" - Retrieval Precision@5: {round(eval_run.avg_precision_k * 100, 2)}%")
    print(f" - Answer Relevance: {round(eval_run.avg_relevance * 100, 2)}%")
    print(f" - Hallucination Rate: {round(eval_run.hallucination_rate * 100, 2)}%")
    print(f" - Avg Latency: {eval_run.avg_latency_ms} ms")

    db.close()
    print("\n[SUCCESS] Verification Completed Successfully!")

if __name__ == "__main__":
    test_full_pipeline()
