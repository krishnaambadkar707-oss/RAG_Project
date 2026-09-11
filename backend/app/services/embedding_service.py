from typing import List
import os
from app.config import settings

_model = None

def get_embedding_model():
    global _model
    if _model is None and settings.EMBEDDING_PROVIDER == "sentence-transformers":
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"[Embedding] OpenAI embedding failed, falling back to SentenceTransformers: {e}")

    # Default: SentenceTransformers local model
    model = get_embedding_model()
    if model:
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    # Simple deterministic fallback vector (e.g. for lightweight testing if no model available)
    import hashlib
    def text_to_fake_vector(t: str, dim: int = 384) -> List[float]:
        h = hashlib.sha256(t.encode('utf-8')).hexdigest()
        nums = [int(h[i:i+2], 16) / 255.0 for i in range(0, min(len(h), dim * 2), 2)]
        while len(nums) < dim:
            nums.extend(nums[:dim - len(nums)])
        return nums[:dim]

    return [text_to_fake_vector(t) for t in texts]

def embed_single_text(text: str) -> List[float]:
    res = embed_texts([text])
    return res[0] if res else []
