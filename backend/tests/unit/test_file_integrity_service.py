#Owner::ANIKET::ANHOTRA = MR.Panda
"""Guard evidence uploads against wrong bytes, unsupported kinds and oversized files."""

from __future__ import annotations

import hashlib

import pytest
from fastapi import HTTPException

from backend.app.services.file_integrity_service import (
    MAX_ORIGINAL_BYTES,
    validate_original,
)


@pytest.mark.parametrize(
    ("content", "kind", "content_type"),
    [
        (b"\xff\xd8\xff\xdb" + b"\x01" * 20, "photo", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n" + b"\x00" * 20, "photo", "image/png"),
        (b"RIFF" + b"\x20\x00\x00\x00WAVE" + b"\x00" * 20, "voice", "audio/wav"),
        (b"OggS" + b"\x00" * 20, "voice", "audio/ogg"),
        (b"%PDF-1.7\n" + b"\x00" * 20, "bill", "application/pdf"),
        (b"%PDF-1.7\n" + b"\x00" * 20, "drawing", "application/pdf"),
    ],
)
def test_fingerprints_preserve_exact_original_bytes(
    content: bytes, kind: str, content_type: str
) -> None:
    """Hash input exactly without transcoding or changing stored content."""
    original = bytes(content)
    result = validate_original(content, kind)
    assert result.sha256 == hashlib.sha256(original).hexdigest()
    assert result.size_bytes == len(original)
    assert result.content_type == content_type
    assert content == original


@pytest.mark.parametrize(
    ("content", "kind", "status_code"),
    [
        (b"", "photo", 413),
        (b"\xff\xd8\xff", "voice", 415),
        (b"MZ" + b"\x00" * 40, "photo", 415),
        (b"hello", "drawing", 415),
        (b"%PDF-1.7", "undefined", 422),
        (b"\x89PNG\r\n\x1a\n", "bill", 415),
    ],
)
def test_wrong_or_unknown_evidence_is_rejected(
    content: bytes, kind: str, status_code: int
) -> None:
    """Reject unsupported types rather than trust the client MIME header."""
    with pytest.raises(HTTPException) as result:
        validate_original(content, kind)
    assert result.value.status_code == status_code


def test_oversized_evidence_fails_before_persistence() -> None:
    """Enforce a finite payload bound even with a valid photo signature."""
    with pytest.raises(HTTPException) as result:
        validate_original(b"\xff\xd8\xff" + b"\x00" * MAX_ORIGINAL_BYTES, "photo")
    assert result.value.status_code == 413
