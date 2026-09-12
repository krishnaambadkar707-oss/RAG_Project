import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.services.vector_store import vector_store
from app.services.embedding_service import embed_single_text

# Test 1: Check if ChromaDB is working
print("=== Vector Store Status ===")
print(f"Using fallback: {vector_store._use_fallback}")
print(f"Collection exists: {vector_store._collection is not None}")
print(f"Memory store size: {len(vector_store._memory_store)}")

# Test 2: Try to search
print("\n=== Testing Search ===")
question = "vacation leave policy"
embedding = embed_single_text(question)
print(f"Embedding generated: {embedding is not None}")
if embedding:
    print(f"Embedding size: {len(embedding)}")

# Test 3: Search with collection_id
print("\n=== Searching with collection_id=1 ===")
results = vector_store.search(query=question, collection_id=1, top_k=5)
print(f"Results found: {len(results)}")
for r in results[:3]:
    print(f"  - {r.filename} (score: {r.similarity_score}) - {r.snippet[:100]}")

# Test 4: Search without collection_id
print("\n=== Searching without collection_id ===")
results_all = vector_store.search(query=question, top_k=5)
print(f"Results found: {len(results_all)}")
for r in results_all[:3]:
    print(f"  - {r.filename} (score: {r.similarity_score}) - {r.snippet[:100]}")
