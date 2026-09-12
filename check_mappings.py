import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.db.database import SessionLocal
from app.db.models import Document, Collection

db = SessionLocal()

print("=== Current Document-Collection Mapping ===")
docs = db.query(Document).all()
for doc in docs:
    coll_name = doc.collection_id
    if coll_name:
        coll = db.query(Collection).filter(Collection.id == coll_name).first()
        coll_name = coll.name if coll else f"Unknown (ID: {coll_name})"
    else:
        coll_name = "None (Unassigned)"
    
    print(f"  {doc.filename} -> Collection: {coll_name} (status: {doc.status})")

db.close()
