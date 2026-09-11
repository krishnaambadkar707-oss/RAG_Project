import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import Document, Collection
from app.db.schemas import DocumentResponse
from app.services.auth_service import get_current_user, require_admin
from app.services.document_parser import parse_document
from app.services.chunking_service import chunk_document
from app.services.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    collection_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Document)
    if collection_id:
        query = query.filter(Document.collection_id == collection_id)
    return query.order_by(Document.created_at.desc()).all()

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    collection_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .txt, .md")

    parsed_coll_id: Optional[int] = None
    if collection_id and str(collection_id).strip() and str(collection_id) not in ["null", "undefined", "None"]:
        try:
            parsed_coll_id = int(collection_id)
        except ValueError:
            parsed_coll_id = None

    # Verify collection if specified
    if parsed_coll_id:
        coll = db.query(Collection).filter(Collection.id == parsed_coll_id).first()
        if not coll:
            raise HTTPException(status_code=404, detail="Specified collection does not exist")

    # Save uploaded file
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save document DB record
    doc = Document(
        filename=filename,
        collection_id=parsed_coll_id,
        file_path=file_path,
        status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Ingest document: Parse -> Chunk -> Embed -> ChromaDB
    try:
        parse_result = parse_document(file_path)
        if not parse_result.pages or all(not p.text.strip() for p in parse_result.pages):
            raise ValueError("No readable text could be extracted from this document.")

        chunks = chunk_document(
            parse_result=parse_result,
            document_id=doc.id,
            filename=doc.filename,
            collection_id=parsed_coll_id or 0
        )

        if not chunks:
            raise ValueError("Document yielded 0 valid text chunks after parsing.")

        vector_store.add_chunks(chunks)

        doc.status = "processed"
        doc.page_count = parse_result.total_pages
        doc.chunk_count = len(chunks)
        db.commit()
        db.refresh(doc)
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
        db.refresh(doc)
        print(f"[Document Ingestion Error] {e}")

    return doc

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete chunks from vector store
    vector_store.delete_document_chunks(doc.id)

    # Remove physical file if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"[File Delete Warning] Could not remove {doc.file_path}: {e}")

    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.filename}' deleted successfully"}
