from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Conversation, Message
from app.db.schemas import QueryRequest, QueryResponse
from app.services.auth_service import get_current_user
from app.services.vector_store import vector_store
from app.services.llm_service import generate_grounded_answer

router = APIRouter(prefix="/query", tags=["Query & RAG Q&A"])

@router.post("", response_model=QueryResponse)
def query_knowledge_base(
    body: QueryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # 1. Manage Conversation Session
    conversation = None
    if body.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == body.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conversation:
        title = question[:40] + "..." if len(question) > 40 else question
        conversation = Conversation(
            user_id=current_user.id,
            collection_id=body.collection_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Store User Query Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=question
    )
    db.add(user_msg)
    db.commit()

    # 3. Vector Retrieval & Grounded Generation
    citations = vector_store.search(
        query=question,
        collection_id=body.collection_id,
        top_k=body.top_k or 5
    )

    answer, sources, latency_ms = generate_grounded_answer(
        query=question,
        citations=citations
    )

    def _to_dict(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return obj.dict()

    sources_data = [_to_dict(s) for s in sources]
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        sources_json=sources_data,
        latency_ms=latency_ms
    )
    db.add(assistant_msg)
    db.commit()

    return QueryResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation.id,
        latency_ms=latency_ms
    )
