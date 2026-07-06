"""PDF utilities. Uses pypdf to extract text from an uploaded PDF resume."""

import io

from pypdf import PdfReader

MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB is plenty for a resume


def extract_pdf_text(file_bytes: bytes) -> str:
    """Read PDF bytes and return the concatenated text of all pages.

    Returns an empty string if extraction fails. Callers should validate
    that the returned string is not empty before using it.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text: list[str] = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            # Skip unreadable page rather than fail the whole upload.
            continue
    return clean_text("\n".join(pages_text))


def clean_text(text: str) -> str:
    """Very simple whitespace normalisation."""
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty)
