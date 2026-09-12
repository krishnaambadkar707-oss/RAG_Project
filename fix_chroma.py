import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.services.vector_store import vector_store
from app.services.document_parser import parse_document
from app.services.chunking_service import chunk_document
from app.db.database import SessionLocal
from app.db.models import Document
import shutil

db = SessionLocal()

print("=" * 60)
print("FIXING: Clearing ChromaDB and re-ingesting documents")
print("=" * 60)

# Step 1: Clear ChromaDB
print("\n1. Clearing ChromaDB collection...")
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    
    # Try to delete the existing collection instead of clearing directory
    chroma_dir = 'chroma_data'
    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
    )
    try:
        client.delete_collection("enterprise_knowledge_base")
        print("   ✓ Deleted old ChromaDB collection")
    except:
        pass  # Collection might not exist
    
    # Reinitialize vector store
    vector_store._init_store()
    print("   ✓ Vector store reinitialized")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 2: Re-ingest all documents
print("\n2. Re-ingesting documents with correct collection IDs...")
docs = db.query(Document).all()

success_count = 0
error_count = 0

for doc in docs:
    try:
        file_path = doc.file_path
        
        # If it's a relative path, handle it
        if file_path.startswith('./uploads'):
            # We're running from backend directory, go up one level
            file_path = file_path.replace('./uploads', '../uploads')
        
        # Convert to absolute path if it isn't already
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"   ✗ File not found: {file_path}")
            error_count += 1
            continue
        
        # Parse and chunk with correct collection_id
        parse_result = parse_document(file_path)
        if not parse_result.pages or all(not p.text.strip() for p in parse_result.pages):
            raise ValueError("No readable text")
        
        chunks = chunk_document(
            parse_result=parse_result,
            document_id=doc.id,
            filename=doc.filename,
            collection_id=doc.collection_id or 0  # Use actual collection_id from database
        )
        
        if not chunks:
            raise ValueError("0 chunks generated")
        
        # Add to vector store
        vector_store.add_chunks(chunks)
        
        print(f"   ✓ {doc.filename} ({len(chunks)} chunks, collection_id={doc.collection_id})")
        success_count += 1
        
    except Exception as e:
        print(f"   ✗ {doc.filename}: {e}")
        error_count += 1

print(f"\n3. Summary:")
print(f"   ✓ Successfully re-ingested: {success_count} documents")
print(f"   ✗ Failed: {error_count} documents")

db.close()
print("\n✅ ChromaDB fix complete!")
