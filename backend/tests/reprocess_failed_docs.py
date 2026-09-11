import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal
from app.db.models import Document
from app.services.document_parser import parse_document
from app.services.chunking_service import chunk_document
from app.services.vector_store import vector_store

def reprocess_failed():
    db = SessionLocal()
    failed_docs = db.query(Document).filter(Document.status == "failed").all()
    print(f"Found {len(failed_docs)} failed documents to re-process.")

    for doc in failed_docs:
        print(f"Re-processing '{doc.filename}' ({doc.file_path})...")
        try:
            parse_result = parse_document(doc.file_path)
            chunks = chunk_document(
                parse_result=parse_result,
                document_id=doc.id,
                filename=doc.filename,
                collection_id=doc.collection_id or 0
            )
            vector_store.add_chunks(chunks)

            doc.status = "processed"
            doc.error_message = None
            doc.page_count = parse_result.total_pages
            doc.chunk_count = len(chunks)
            db.commit()
            print(f"SUCCESS: '{doc.filename}' processed successfully ({parse_result.total_pages} pages, {len(chunks)} chunks).")
        except Exception as e:
            print(f"ERROR re-processing '{doc.filename}': {e}")
            doc.error_message = str(e)
            db.commit()

    db.close()

if __name__ == "__main__":
    reprocess_failed()
