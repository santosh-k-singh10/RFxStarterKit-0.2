"""
core/ingestor.py
----------------
Parses PDF and DOCX files into section-aware chunks.

Strategy
--------
1. Use `unstructured` to extract elements with type labels (Title, NarrativeText, etc.)
2. Detect heading elements to determine section boundaries
3. Accumulate text within each section into a DocumentChunk
4. Fall back to python-docx or pypdf if unstructured fails

Why section-aware chunking?
    Fixed-token chunking splits mid-paragraph and loses section context.
    Section-aware chunking ensures each chunk's `source_section` field is
    accurate, which is critical for requirement traceability.
"""

from __future__ import annotations

import re
import structlog
from pathlib import Path

from core.schemas import DocumentChunk

log = structlog.get_logger()

# Element types from unstructured that indicate a new section heading
HEADING_TYPES = {"Title", "Header", "SectionHeader"}

# Minimum characters for a *combined section* chunk to be worth processing.
# Optimized to 1600 based on empirical testing for best quality and performance
# - Extracts most requirements (26 vs 23-25 for other sizes)
# - Good processing speed (40.28s vs 33.38s for 800, but better context)
# - Ideal for large RFPs with complex requirements
# See CHUNK_SIZE_OPTIMIZATION_GUIDE.md for details
MIN_CHUNK_CHARS = 1600

# Minimum characters for a *single PDF page* in the pypdf fallback path.
# Pages of small / concise PDFs can legitimately have only a few hundred
# characters, so we use a much lower bar here — just enough to skip truly
# blank or whitespace-only pages.
MIN_PAGE_CHARS = 50


def ingest_document(file_path: str) -> list[DocumentChunk]:
    """
    Main entry point. Accepts PDF or DOCX path.
    Returns a list of DocumentChunk objects ordered as they appear in the doc.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"RFP file not found: {file_path}")

    suffix = path.suffix.lower()
    print(f"\n{'='*60}")
    print(f"[INGESTOR] Starting document ingestion")
    print(f"   File: {path.name}")
    print(f"   Type: {suffix}")
    print(f"   Size: {path.stat().st_size} bytes")
    print(f"{'='*60}\n")
    
    log.info("ingesting_document", file=str(path), type=suffix)

    try:
        if suffix == ".pdf":
            print("[INGESTOR] Attempting unstructured for PDF")
            return _ingest_with_unstructured(file_path)
        elif suffix in (".docx", ".doc"):
            print("[INGESTOR] Attempting unstructured for DOCX")
            return _ingest_with_unstructured(file_path)
        elif suffix == ".txt":
            print("[INGESTOR] Using text file parser")
            return _ingest_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Use PDF, DOCX, or TXT.")
    except ImportError as e:
        print(f"[INGESTOR] ImportError - {str(e)}")
        log.warning("unstructured_import_error", error=str(e))
        if suffix == ".docx":
            print("[INGESTOR] Falling back to python-docx")
            return _ingest_docx_fallback(file_path)
        elif suffix == ".pdf":
            print("[INGESTOR] Falling back to pypdf")
            return _ingest_pdf_fallback(file_path)
        elif suffix == ".txt":
            return _ingest_text_file(file_path)
        raise
    except Exception as e:
        print(f"[INGESTOR] Exception during parsing - {type(e).__name__}: {str(e)}")
        log.error("ingest_with_unstructured_failed", error=str(e), error_type=type(e).__name__)
        # Try fallback for PDFs and DOCX
        if suffix == ".docx":
            print("[INGESTOR] Falling back to python-docx after error")
            return _ingest_docx_fallback(file_path)
        elif suffix == ".pdf":
            print("[INGESTOR] Falling back to pypdf after error")
            return _ingest_pdf_fallback(file_path)
        elif suffix == ".txt":
            return _ingest_text_file(file_path)
        raise


def _ingest_with_unstructured(file_path: str) -> list[DocumentChunk]:
    """Parse using the unstructured library with enhanced table support."""
    from unstructured.partition.auto import partition

    print("[INGESTOR] Calling unstructured.partition()...")
    # Use 'hi_res' strategy for better table extraction
    # This is slower but captures tables properly
    elements = partition(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True  # Enable table structure inference
    )
    print(f"[INGESTOR] Got {len(elements)} elements from unstructured")
    
    # Show first few element types and count tables
    table_count = 0
    if elements:
        preview = ", ".join([type(el).__name__ for el in elements[:5]])
        print(f"   First 5 element types: {preview}...\n")
        table_count = sum(1 for el in elements if type(el).__name__ == "Table")
        if table_count > 0:
            print(f"   [INFO] Found {table_count} table(s) in document\n")

    chunks: list[DocumentChunk] = []
    current_section = "Preamble"
    current_texts: list[str] = []
    current_page_start = 1
    current_page_end = 1
    
    heading_count = 0
    text_count = 0
    table_elements = 0

    for el in elements:
        el_type  = type(el).__name__
        text     = str(el).strip()
        metadata = getattr(el, "metadata", None)

        if not text:
            continue

        # Update page tracking - track range instead of single page
        if metadata:
            page = getattr(metadata, "page_number", None)
            if page:
                if not current_texts:  # First element in section
                    current_page_start = page
                current_page_end = page

        if el_type in HEADING_TYPES:
            heading_count += 1
            # Flush current buffer as a chunk
            if current_texts:
                _flush_chunk(chunks, current_section, current_texts, current_page_start, current_page_end)
                current_texts = []
            current_section = _clean_heading(text)
            # Reset page tracking for new section
            current_page_start = current_page_end
            if heading_count <= 5:  # Show first few headings
                print(f"   [Heading #{heading_count}]: {current_section}")

        elif el_type == "Table":
            # Special handling for tables - format them clearly
            table_elements += 1
            text_count += 1
            # Add markers to help LLM recognize this is tabular data
            table_text = f"\n[TABLE DATA]\n{text}\n[END TABLE]\n"
            current_texts.append(table_text)
            print(f"   [Table #{table_elements} found in section: {current_section}]")
        else:
            text_count += 1
            current_texts.append(text)

    # Flush the last section
    if current_texts:
        _flush_chunk(chunks, current_section, current_texts, current_page_start, current_page_end)

    print(f"\n[INGESTOR] Ingestion statistics:")
    print(f"   Headings found: {heading_count}")
    print(f"   Text elements: {text_count}")
    print(f"   Tables processed: {table_elements}")
    print(f"   Chunks created: {len(chunks)}")
    if chunks:
        print(f"   Avg chunk size: {sum(c.char_count for c in chunks) // len(chunks)} chars")
    print(f"{'='*60}\n")
    
    log.info("ingestion_complete", chunks=len(chunks), file=file_path)
    return chunks


def _ingest_pdf_fallback(file_path: str) -> list[DocumentChunk]:
    """Fallback PDF parser using pypdf."""
    print("[PDF FALLBACK] Using pypdf to extract text from PDF")
    try:
        from pypdf import PdfReader
    except ImportError:
        log.error("pypdf_not_available")
        raise RuntimeError(
            "PDF processing failed. Install PDF support with: pip install pypdf"
        )
    
    reader = PdfReader(file_path)
    chunks: list[DocumentChunk] = []
    print(f"[PDF FALLBACK] PDF has {len(reader.pages)} pages")
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        # Use MIN_PAGE_CHARS (not MIN_CHUNK_CHARS) — individual pages of small
        # or concise PDFs are legitimately short; MIN_CHUNK_CHARS (1600) is
        # intended for combined section chunks and would discard real content.
        if not text or len(text.strip()) < MIN_PAGE_CHARS:
            print(f"   [Page {page_num}]: Skipping (too short)")
            continue
        
        print(f"   [Page {page_num}]: Extracted {len(text)} characters")
        
        # Create one chunk per page
        current_section = f"Page {page_num}"
        # Split by paragraphs (double newlines) to get better chunks
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if paragraphs:
            _flush_chunk_pdf(chunks, current_section, paragraphs, page_num, page_num)
    
    print(f"\n[PDF FALLBACK] Created {len(chunks)} chunks from PDF")
    print(f"{'='*60}\n")
    
    log.info("pdf_fallback_complete", chunks=len(chunks))
    return chunks


def _ingest_docx_fallback(file_path: str) -> list[DocumentChunk]:
    """Fallback DOCX parser using python-docx directly.

    python-docx has no page-number API, so we estimate the page by counting
    paragraphs — roughly PARAS_PER_PAGE non-empty paragraphs ≈ one page.
    This is an approximation but is far better than hardcoding page=1.
    """
    print("[DOCX FALLBACK] Using python-docx")
    from docx import Document  # type: ignore

    PARAS_PER_PAGE = 40   # rough estimate: ~40 non-empty paragraphs per page

    doc = Document(file_path)
    chunks: list[DocumentChunk] = []
    current_section = "Preamble"
    current_texts: list[str] = []
    para_count = 0
    section_page_start = 1

    for para in doc.paragraphs:
        text  = para.text.strip()
        style = para.style.name if (para.style and para.style.name) else ""

        if not text:
            continue

        para_count += 1
        estimated_page = max(1, (para_count - 1) // PARAS_PER_PAGE + 1)

        is_heading = (
            style.startswith("Heading") or
            style in ("Title", "Subtitle") or
            (para.runs and all(r.bold for r in para.runs if r.text.strip()))
        )

        if is_heading:
            if current_texts:
                _flush_chunk(chunks, current_section, current_texts, section_page_start, estimated_page)
                current_texts = []
            current_section = _clean_heading(text)
            section_page_start = estimated_page
        else:
            current_texts.append(text)

    if current_texts:
        _flush_chunk(chunks, current_section, current_texts, section_page_start, estimated_page if para_count else 1)

    print(f"[DOCX FALLBACK] Created {len(chunks)} chunks")
    print(f"{'='*60}\n")
    
    log.info("docx_fallback_complete", chunks=len(chunks))
    return chunks


def _ingest_text_file(file_path: str) -> list[DocumentChunk]:
    """Simple text file parser — splits on blank lines and all-caps headings."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    chunks: list[DocumentChunk] = []
    current_section = "Document"
    current_texts: list[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Heuristic: a line in ALL CAPS or ending with ":" is a heading
        if re.match(r'^[A-Z0-9\s\-:]{5,60}$', line) or (line.endswith(":") and len(line) < 80):
            if current_texts:
                _flush_chunk(chunks, current_section, current_texts, 1, 1)
                current_texts = []
            current_section = line.rstrip(":")
        else:
            current_texts.append(line)

    if current_texts:
        _flush_chunk(chunks, current_section, current_texts, 1)

    return chunks


def _flush_chunk(
    chunks: list[DocumentChunk],
    section: str,
    texts: list[str],
    page_start: int,
    page_end: int | None = None,
) -> None:
    """
    Combine accumulated text lines into a DocumentChunk and append.
    Applies MIN_CHUNK_CHARS to skip sections with too little combined content.
    """
    combined = " ".join(texts).strip()
    if len(combined) >= MIN_CHUNK_CHARS:
        chunks.append(DocumentChunk(
            section=section,
            text=combined,
            page=page_start,
            char_count=len(combined),
        ))


def _flush_chunk_pdf(
    chunks: list[DocumentChunk],
    section: str,
    texts: list[str],
    page_start: int,
    page_end: int | None = None,
) -> None:
    """
    Like _flush_chunk but used by the pypdf fallback path.
    Does NOT apply MIN_CHUNK_CHARS — individual pages of small PDFs are
    legitimately short and must not be discarded.
    """
    combined = " ".join(texts).strip()
    if combined:
        chunks.append(DocumentChunk(
            section=section,
            text=combined,
            page=page_start,
            char_count=len(combined),
        ))


def _clean_heading(text: str) -> str:
    """Normalise a heading string: strip numbering, excessive whitespace."""
    # Remove leading numbering like "1.", "1.2", "Section 3:"
    text = re.sub(r'^[\d\.]+\s*', '', text)
    text = re.sub(r'^(section|clause|article)\s*\d+(?:\.\d+)*[:\.]?\s*', '', text, flags=re.IGNORECASE)
    return text.strip().title() or "Untitled Section"


# Compatibility alias for older test/consumer naming
_normalise_title = _clean_heading
