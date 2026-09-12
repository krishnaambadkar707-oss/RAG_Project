import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.config import settings
import chromadb
from chromadb.config import Settings as ChromaSettings

# Connect to ChromaDB directly
client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_DIR,
    settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
)
collection = client.get_or_create_collection(
    name="enterprise_knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

# Check what's actually in the collection
print("=== ChromaDB Collection Info ===")
print(f"Collection count: {collection.count()}")

# Get all items to inspect metadata
try:
    all_items = collection.get(include=["metadatas"])
    print(f"Total documents: {len(all_items['ids'])}")
    
    # Sample metadata
    if all_items['metadatas']:
        print("\n=== Sample Metadata ===")
        for meta in all_items['metadatas'][:3]:
            print(f"  {meta}")
            
        # Count by collection_id
        print("\n=== Documents by collection_id ===")
        from collections import Counter
        coll_ids = [m.get('collection_id', 'N/A') for m in all_items['metadatas']]
        for cid, count in Counter(coll_ids).items():
            print(f"  collection_id={cid}: {count}")
            
        # Test where filter
        print("\n=== Testing Where Filter ===")
        result = collection.query(
            query_embeddings=[[0.1]*384],  # Dummy embedding
            n_results=5,
            where={"collection_id": 1},
            include=["metadatas"]
        )
        print(f"Results with where={{'collection_id': 1}}: {len(result['ids'])}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
