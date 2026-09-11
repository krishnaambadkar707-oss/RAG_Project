from typing import List, Dict, Any
from app.services.document_parser import DocumentParseResult
from app.config import settings

class Chunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        document_id: int,
        filename: str,
        collection_id: int,
        page_number: int,
        section_title: str,
        chunk_index: int
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.document_id = document_id
        self.filename = filename
        self.collection_id = collection_id
        self.page_number = page_number
        self.section_title = section_title
        self.chunk_index = chunk_index

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "collection_id": self.collection_id or 0,
            "page_number": self.page_number,
            "section_title": self.section_title or "General",
            "chunk_index": self.chunk_index
        }

def chunk_document(
    parse_result: DocumentParseResult,
    document_id: int,
    filename: str,
    collection_id: int,
    chunk_size: int = settings.DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = settings.DEFAULT_CHUNK_OVERLAP
) -> List[Chunk]:
    chunks: List[Chunk] = []
    global_chunk_idx = 0

    for page in parse_result.pages:
        text = page.text
        if not text:
            continue

        # Split text into overlapping windows
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_str = text[start:end]

            # Adjust split to avoid cutting words in middle if possible
            if end < text_length:
                last_space = chunk_str.rfind(" ")
                if last_space > chunk_size // 2:
                    end = start + last_space
                    chunk_str = text[start:end]

            chunk_str = chunk_str.strip()
            if len(chunk_str) > 5: # Ignore tiny empty noise chunks
                chunk_id = f"doc_{document_id}_p{page.page_number}_c{global_chunk_idx}"
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    text=chunk_str,
                    document_id=document_id,
                    filename=filename,
                    collection_id=collection_id,
                    page_number=page.page_number,
                    section_title=page.section_title,
                    chunk_index=global_chunk_idx
                ))
                global_chunk_idx += 1

            start += (chunk_size - chunk_overlap)
            if start >= text_length:
                break

    return chunks
