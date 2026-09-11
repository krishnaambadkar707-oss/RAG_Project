from typing import List
import os
from app.config import settings

_model = None

def get_embedding_model():
    global _model
    if _model is None and settings.EMBEDDING_PROVIDER == "sentence-transformers":
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            print("[Embedding] sentence_transformers library not installed. Falling back to API/hash embeddings.")
            _model = None
        except Exception as e:
            print(f"[Embedding] Failed to load SentenceTransformer model: {e}")
            _model = None
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
            print(f"[Embedding] OpenAI embedding failed: {e}")

    if provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            import httpx
            embeddings = []
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.GEMINI_API_KEY}"
            with httpx.Client(timeout=10.0) as client:
                for text in texts:
                    resp = client.post(url, json={"model": "models/text-embedding-004", "content": {"parts": [{"text": text}]}})
                    if resp.status_code == 200:
                        embeddings.append(resp.json().get("embedding", {}).get("values", []))
                    else:
                        break
            if len(embeddings) == len(texts):
                return embeddings
        except Exception as e:
            print(f"[Embedding] Gemini embedding failed: {e}")

    # Default: SentenceTransformers local model (if available)
    model = get_embedding_model()
    if model:
        try:
            embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"[Embedding] Local model encoding failed: {e}")

    # Simple deterministic fallback vector (for lightweight testing / serverless without heavy ML models)
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

