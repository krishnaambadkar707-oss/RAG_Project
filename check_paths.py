import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.db.database import SessionLocal
from app.db.models import Document

db = SessionLocal()

print("=== Document File Paths ===")
docs = db.query(Document).all()
for doc in docs:
    print(f"\n{doc.filename}:")
    print(f"  Stored path: {doc.file_path}")
    
    # Check if file exists
    if os.path.exists(doc.file_path):
        print(f"  Status: EXISTS ✓")
    else:
        # Try to find it
        filename_only = os.path.basename(doc.file_path)
        # Search in common locations
        for search_path in ['../uploads/', '../data/sample_documents/', './uploads/', './data/sample_documents/']:
            full_path = search_path + filename_only
            if os.path.exists(full_path):
                print(f"  Found at: {full_path}")
                break
        else:
            print(f"  Status: NOT FOUND ✗")

db.close()
