from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Conversation
from app.db.schemas import ConversationResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    return convs

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully"}
