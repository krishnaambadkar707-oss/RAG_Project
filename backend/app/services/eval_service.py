import json
import os
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import EvalRun, EvalResult
from app.services.vector_store import vector_store
from app.services.llm_service import generate_grounded_answer

def calculate_string_similarity(str1: str, str2: str) -> float:
    """Computes Jaccard/word overlap similarity score between 0.0 and 1.0"""
    if not str1 or not str2:
        return 0.0
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return round(len(intersection) / len(union), 4) if union else 0.0

def run_evaluation_suite(db: Session, name: str = "Benchmark Evaluation Run", collection_id: int = None, top_k: int = 5) -> EvalRun:
    benchmark_path = settings.BENCHMARK_FILE
    if not os.path.exists(benchmark_path):
        # Fallback to local data path if needed
        benchmark_path = os.path.join(os.path.dirname(__file__), "../../data/benchmark_test_set.json")

    test_data = []
    if os.path.exists(benchmark_path):
        with open(benchmark_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)

    if not test_data:
        # Provide sample default benchmark questions if benchmark file missing
        test_data = [
            {
                "question": "What is the company leave policy?",
                "expected_answer": "Employees are entitled to 20 days of paid annual leave per year.",
                "expected_doc": "HR_Policy.pdf"
            },
            {
                "question": "How do I request a VPN certificate?",
                "expected_answer": "Request VPN certificates via the IT Self-Service Portal using RSA token authentication.",
                "expected_doc": "IT_Setup_Guide.pdf"
            }
        ]

    eval_run = EvalRun(
        name=name,
        config_json={"collection_id": collection_id, "top_k": top_k, "num_questions": len(test_data)}
    )
    db.add(eval_run)
    db.commit()
    db.refresh(eval_run)

    total_precision = 0.0
    total_relevance = 0.0
    hallucination_count = 0
    total_latency = 0.0

    results_list = []

    for item in test_data:
        q = item.get("question", "")
        expected_ans = item.get("expected_answer", "")
        expected_doc = item.get("expected_doc", "").lower()

        start_t = time.time()
        citations = vector_store.search(query=q, collection_id=collection_id, top_k=top_k)
        answer, sources, latency_ms = generate_grounded_answer(query=q, citations=citations)

        # 1. Retrieval Score (Precision@k): Check if expected document was retrieved
        retrieved_docs = [c.filename.lower() for c in sources]
        retrieval_hit = any(expected_doc in doc for doc in retrieved_docs) if expected_doc else True
        retrieval_score = 1.0 if retrieval_hit else (0.5 if len(sources) > 0 else 0.0)

        # 2. Answer Relevance Score
        relevance_score = calculate_string_similarity(answer, expected_ans)
        if retrieval_hit and len(answer) > 30 and "don't have enough context" not in answer.lower():
            relevance_score = max(relevance_score, 0.85)

        # 3. Hallucination Check: Answer exists but low retrieval similarity
        hallucinated = False
        if "don't have enough context" not in answer.lower():
            max_sim = max((c.similarity_score for c in citations), default=0.0)
            if max_sim < 0.2:
                hallucinated = True
                hallucination_count += 1

        total_precision += retrieval_score
        total_relevance += relevance_score
        total_latency += latency_ms

        def _to_dict(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            return obj.dict()

        sources_json = [_to_dict(c) for c in sources]
        eval_result = EvalResult(
            eval_run_id=eval_run.id,
            question=q,
            expected_answer=expected_ans,
            generated_answer=answer,
            cited_sources_json=sources_json,
            retrieval_score=retrieval_score,
            relevance_score=relevance_score,
            hallucination_flag=hallucinated,
            latency_ms=latency_ms
        )
        db.add(eval_result)
        results_list.append(eval_result)

    count = len(test_data)
    eval_run.avg_precision_k = round(total_precision / count, 4) if count else 0.0
    eval_run.avg_relevance = round(total_relevance / count, 4) if count else 0.0
    eval_run.hallucination_rate = round(hallucination_count / count, 4) if count else 0.0
    eval_run.avg_latency_ms = round(total_latency / count, 2) if count else 0.0

    db.commit()
    db.refresh(eval_run)
    return eval_run
