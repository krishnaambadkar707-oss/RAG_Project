from typing import List, Optional, Dict, Any
import math

from app.config import settings
from app.services.chunking_service import Chunk
from app.services.embedding_service import embed_texts, embed_single_text
from app.db.schemas import Citation

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class VectorStore:
    def __init__(self):
        self._collection = None
        self._memory_store: List[Dict[str, Any]] = []
        self._use_fallback = False
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_DIR,
                settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name="enterprise_knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            print("[VectorStore] Persistent ChromaDB initialized successfully.")
        except Exception as e:
            print(f"[VectorStore Warning] ChromaDB initialization skipped/failed ({e}). Using resilient in-memory vector store fallback.")
            self._use_fallback = True

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [c.to_metadata() for c in chunks]
        embeddings = embed_texts(texts)

        if not self._use_fallback and self._collection is not None:
            try:
                self._collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                return
            except Exception as e:
                print(f"[VectorStore Warning] ChromaDB upsert failed ({e}), using in-memory store.")
                self._use_fallback = True

        # Fallback in-memory storage
        for c_id, text, meta, emb in zip(ids, texts, metadatas, embeddings):
            # Remove any existing chunk with same id
            self._memory_store = [m for m in self._memory_store if m["id"] != c_id]
            self._memory_store.append({
                "id": c_id,
                "text": text,
                "metadata": meta,
                "embedding": emb
            })

    def search(
        self,
        query: str,
        collection_id: Optional[int] = None,
        top_k: int = settings.TOP_K_RETRIEVAL
    ) -> List[Citation]:
        if not query.strip():
            return []

        query_embedding = embed_single_text(query)
        if not query_embedding:
            return []

        if not self._use_fallback and self._collection is not None:
            where_filter = None
            if collection_id and collection_id > 0:
                where_filter = {"collection_id": collection_id}

            try:
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )
                citations: List[Citation] = []
                if results and results.get("documents") and results["documents"][0]:
                    documents = results["documents"][0]
                    metadatas = results["metadatas"][0]
                    distances = results["distances"][0] if "distances" in results and results["distances"] else [0.5]*len(documents)

                    for doc, meta, dist in zip(documents, metadatas, distances):
                        similarity = round(max(0.0, 1.0 - float(dist)), 4)
                        citations.append(Citation(
                            document_id=int(meta.get("document_id", 0)),
                            filename=str(meta.get("filename", "Unknown")),
                            page_number=int(meta.get("page_number", 1)),
                            section_title=str(meta.get("section_title", "General")),
                            snippet=doc,
                            similarity_score=similarity
                        ))
                    return citations[:top_k]
            except Exception as e:
                print(f"[VectorStore Warning] ChromaDB query failed ({e}), using in-memory search fallback.")

        # In-memory search fallback
        scored_items = []
        for item in self._memory_store:
            meta = item["metadata"]
            if collection_id and collection_id > 0:
                if int(meta.get("collection_id", 0)) != collection_id:
                    continue
            
            sim = _cosine_similarity(query_embedding, item["embedding"])
            scored_items.append((sim, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)

        citations: List[Citation] = []
        for sim, item in scored_items[:top_k]:
            meta = item["metadata"]
            citations.append(Citation(
                document_id=int(meta.get("document_id", 0)),
                filename=str(meta.get("filename", "Unknown")),
                page_number=int(meta.get("page_number", 1)),
                section_title=str(meta.get("section_title", "General")),
                snippet=item["text"],
                similarity_score=round(float(sim), 4)
            ))

        return citations

    def delete_document_chunks(self, document_id: int):
        if not self._use_fallback and self._collection is not None:
            try:
                self._collection.delete(where={"document_id": document_id})
            except Exception as e:
                print(f"[VectorStore Warning] ChromaDB delete failed ({e})")
        
        self._memory_store = [
            item for item in self._memory_store 
            if int(item["metadata"].get("document_id", 0)) != document_id
        ]

vector_store = VectorStore()
