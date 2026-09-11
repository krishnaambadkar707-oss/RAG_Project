import os
from typing import List, Dict, Any

class ParsedPage:
    def __init__(self, page_number: int, text: str, section_title: str = ""):
        self.page_number = page_number
        self.text = text
        self.section_title = section_title

class DocumentParseResult:
    def __init__(self, pages: List[ParsedPage], total_pages: int):
        self.pages = pages
        self.total_pages = total_pages

def parse_pdf(file_path: str) -> DocumentParseResult:
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path, strict=False)
        pages = []
        total_pages = len(reader.pages)
        
        current_section = "General"
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                continue
            
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if lines and len(lines[0]) < 80 and (lines[0].isupper() or lines[0].istitle() or lines[0].startswith("Section") or lines[0].startswith("Chapter")):
                current_section = lines[0]

            pages.append(ParsedPage(
                page_number=i + 1,
                text=text,
                section_title=current_section
            ))
            
        if pages:
            return DocumentParseResult(pages=pages, total_pages=total_pages)
    except Exception as e:
        print(f"[PDF Parser Warning] pypdf parsing failed for {file_path}: {e}")

    # Fallback 1: Try parsing as DOCX (in case a .docx file was renamed to .pdf)
    try:
        return parse_docx(file_path)
    except Exception:
        pass

    # Fallback 2: Try parsing as TXT
    try:
        return parse_txt(file_path)
    except Exception:
        pass

    raise ValueError("Unable to parse PDF file. Ensure file contains extractable text and is not encrypted.")

def parse_docx(file_path: str) -> DocumentParseResult:
    try:
        from docx import Document as DocxReader
        doc = DocxReader(file_path)
        pages = []
        current_section = "General"
        current_page_text = []
        page_num = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            if para.style and para.style.name and para.style.name.startswith("Heading"):
                current_section = text

            current_page_text.append(text)

            # Approximate page break per ~2500 characters
            if sum(len(t) for t in current_page_text) > 2500:
                pages.append(ParsedPage(
                    page_number=page_num,
                    text="\n".join(current_page_text),
                    section_title=current_section
                ))
                page_num += 1
                current_page_text = []

        if current_page_text:
            pages.append(ParsedPage(
                page_number=page_num,
                text="\n".join(current_page_text),
                section_title=current_section
            ))

        if pages:
            return DocumentParseResult(pages=pages, total_pages=len(pages))
    except Exception as e:
        print(f"[DOCX Parser Warning] python-docx parsing failed: {e}")

    # Fallback: Try TXT parser
    try:
        return parse_txt(file_path)
    except Exception:
        pass

    raise ValueError("Unable to parse Word document file.")

def parse_txt(file_path: str) -> DocumentParseResult:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    blocks = content.split("\n\n")
    pages = []
    current_block = []
    page_num = 1
    current_section = "General"

    for b in blocks:
        b_clean = b.strip()
        if not b_clean:
            continue

        lines = b_clean.split("\n")
        if lines and (lines[0].startswith("#") or lines[0].isupper()):
            current_section = lines[0].replace("#", "").strip()

        current_block.append(b_clean)
        if sum(len(x) for x in current_block) > 2000:
            pages.append(ParsedPage(
                page_number=page_num,
                text="\n\n".join(current_block),
                section_title=current_section
            ))
            page_num += 1
            current_block = []

    if current_block:
        pages.append(ParsedPage(
            page_number=page_num,
            text="\n\n".join(current_block),
            section_title=current_section
        ))

    return DocumentParseResult(pages=pages, total_pages=len(pages))

def parse_document(file_path: str) -> DocumentParseResult:
    # Inspect file magic bytes first to handle misnamed files (e.g. DOCX saved as .pdf)
    try:
        with open(file_path, "rb") as f:
            header = f.read(8)
            if header.startswith(b"PK\x03\x04"): # Zip / DOCX file magic header
                try:
                    return parse_docx(file_path)
                except Exception as docx_err:
                    print(f"[Parser Magic Warning] DOCX parse failed on zip magic header: {docx_err}")
            elif header.startswith(b"%PDF"): # PDF file magic header
                try:
                    return parse_pdf(file_path)
                except Exception as pdf_err:
                    print(f"[Parser Magic Warning] PDF parse failed on PDF magic header: {pdf_err}")
    except Exception as magic_err:
        print(f"[Parser Magic Warning] Failed reading file header: {magic_err}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        try:
            return parse_pdf(file_path)
        except Exception:
            pass
    elif ext in [".docx", ".doc"]:
        try:
            return parse_docx(file_path)
        except Exception:
            pass
    elif ext in [".txt", ".md"]:
        try:
            return parse_txt(file_path)
        except Exception:
            pass

    # Universal Fallback chain across parsers
    for parser in [parse_docx, parse_pdf, parse_txt]:
        try:
            res = parser(file_path)
            if res and res.pages and any(p.text.strip() for p in res.pages):
                return res
        except Exception:
            continue

    raise ValueError(f"Unable to extract readable text from document ({ext}). Ensure file is not encrypted or corrupted.")
