"""Parse an uploaded transcript file (.txt or .docx) into plain text.

The transcript is treated as transient input (NFR-SEC-03): callers pass the bytes
in, receive plain text out, and must not persist the raw content.
"""
import io

from src.api.exceptions import validation_error

_TXT_EXTENSIONS = (".txt",)
_DOCX_EXTENSIONS = (".docx",)
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def _parse_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _parse_docx(data: bytes) -> str:
    from docx import Document  # imported lazily — python-docx

    document = Document(io.BytesIO(data))
    return "\n".join(p.text for p in document.paragraphs)


def parse_transcript(data: bytes, filename: str) -> str:
    """Return plain text from an uploaded .txt or .docx transcript file."""
    if not data:
        raise validation_error("Transcript file is empty")
    if len(data) > _MAX_BYTES:
        raise validation_error("Transcript file exceeds the 5 MB limit")

    lowered = (filename or "").lower()
    if lowered.endswith(_DOCX_EXTENSIONS):
        text = _parse_docx(data)
    elif lowered.endswith(_TXT_EXTENSIONS):
        text = _parse_txt(data)
    else:
        raise validation_error("Unsupported file type — upload a .txt or .docx file")

    if not text.strip():
        raise validation_error("Transcript file contains no readable text")
    return text
