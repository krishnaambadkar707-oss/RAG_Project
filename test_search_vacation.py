import sys
import os
os.chdir('c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')
sys.path.insert(0, 'c:/Users/krish/OneDrive/Desktop/RAG_Project/backend')

from app.services.vector_store import vector_store

# Test with exact query from test_query_debug.py
question = "vacation"
print(f"Testing search with query: '{question}'")

# Search WITH collection_id
print("\n=== With collection_id=1 ===")
results_with_coll = vector_store.search(query=question, collection_id=1, top_k=5)
print(f"Results found: {len(results_with_coll)}")
for r in results_with_coll:
    print(f"  - {r.filename} (score: {r.similarity_score})")

# Search WITHOUT collection_id
print("\n=== Without collection_id ===")
results_without_coll = vector_store.search(query=question, top_k=5)
print(f"Results found: {len(results_without_coll)}")
for r in results_without_coll:
    print(f"  - {r.filename} (score: {r.similarity_score})")
