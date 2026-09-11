from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Collection, Document
from app.db.schemas import CollectionCreate, CollectionResponse
from app.services.auth_service import get_current_user, require_admin

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("", response_model=List[CollectionResponse])
def list_collections(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    collections = db.query(Collection).all()
    res = []
    for c in collections:
        doc_count = db.query(Document).filter(Document.collection_id == c.id).count()
        item = CollectionResponse.from_orm(c)
        item.document_count = doc_count
        res.append(item)
    return res

@router.post("", response_model=CollectionResponse)
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing = db.query(Collection).filter(Collection.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection with this name already exists")
    
    collection = Collection(name=data.name, description=data.description)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    res = CollectionResponse.from_orm(collection)
    res.document_count = 0
    return res

@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    db.delete(collection)
    db.commit()
    return {"message": f"Collection '{collection.name}' deleted successfully"}
