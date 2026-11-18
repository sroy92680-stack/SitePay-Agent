#Owner::ANIKET::ANHOTRA = MR.Panda
"""Bounded file signature validation and SHA-256 evidence fingerprinting."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from fastapi import HTTPException

MAX_ORIGINAL_BYTES = 20 * 1024 * 1024

SIGNATURE_TO_CONTENT_TYPE = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "pdf": "application/pdf",
}
ALLOWED_FILE_FORMATS = {
    "photo": frozenset({"jpeg", "png"}),
    "voice": frozenset({"wav", "ogg"}),
    "drawing": frozenset({"pdf"}),
    "bill": frozenset({"pdf"}),
}


@dataclass(frozen=True)
class ValidatedOriginal:
    """Return only verified properties of exact uploaded original bytes."""

    sha256: str
    size_bytes: int
    content_type: str
    file_format: str


def detect_file_format(content: bytes) -> str | None:
    """Determine a narrow set of supported original formats from magic bytes."""

    if content.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if content.startswith(b"RIFF") and content[8:12] == b"WAVE":
        return "wav"
    if content.startswith(b"OggS"):
        return "ogg"
    if content.startswith(b"%PDF-"):
        return "pdf"
    return None


def validate_original(content: bytes, kind: str) -> ValidatedOriginal:
    """Reject unsupported, mismatched, missing and oversized evidence bytes.

    Uploaded browser MIME types and filenames are never authoritative inputs.
    """
    if not content or len(content) > MAX_ORIGINAL_BYTES:
        raise HTTPException(413, "Empty or oversized original evidence")
    allowed = ALLOWED_FILE_FORMATS.get(kind)
    if allowed is None:
        raise HTTPException(422, "Unsupported evidence kind")
    file_format = detect_file_format(content)
    if file_format not in allowed:
        raise HTTPException(415, "File signature does not match evidence kind")
    return ValidatedOriginal(
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        content_type=SIGNATURE_TO_CONTENT_TYPE[file_format],
        file_format=file_format,
    )
