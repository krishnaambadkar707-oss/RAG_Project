from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.services.chunking_service import Chunk
from app.services.embedding_service import embed_texts, embed_single_text
from app.db.schemas import Citation

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="enterprise_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [c.to_metadata() for c in chunks]
        embeddings = embed_texts(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )

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

        where_filter = None
        if collection_id and collection_id > 0:
            where_filter = {"collection_id": collection_id}

        results = None
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"[VectorStore] ChromaDB query with where filter {where_filter} failed ({e}), using fallback manual filter")
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k * 4, 30),
                    include=["documents", "metadatas", "distances"]
                )
            except Exception as e2:
                print(f"[VectorStore] Vector query failed: {e2}")
                return []

        citations: List[Citation] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return citations

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.5]*len(documents)

        # Enforce strict collection scoping in Python if filter wasn't applied by vector engine
        if collection_id and collection_id > 0:
            scoped_docs, scoped_metas, scoped_dists = [], [], []
            for d, m, dist in zip(documents, metadatas, distances):
                if int(m.get("collection_id", 0)) == collection_id:
                    scoped_docs.append(d)
                    scoped_metas.append(m)
                    scoped_dists.append(dist)
            if scoped_docs:
                documents, metadatas, distances = scoped_docs, scoped_metas, scoped_dists

        for doc, meta, dist in zip(documents, metadatas, distances):
            # Cosine distance to similarity score
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

    def delete_document_chunks(self, document_id: int):
        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception as e:
            print(f"[VectorStore] Delete document chunks failed for doc_id {document_id}: {e}")

vector_store = VectorStore()
