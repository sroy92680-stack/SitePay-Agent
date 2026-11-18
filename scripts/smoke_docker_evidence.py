#Owner::ANIKET::ANHOTRA = MR.Panda
"""Exercise real private MinIO evidence persistence through live Docker HTTP."""

from __future__ import annotations

import hashlib
import json
import secrets
import struct
import zlib
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from scripts.smoke_docker_api import BASE_URL, request_json, require_ready


def synthetic_png(rgb: tuple[int, int, int]) -> bytes:
    """Create a valid one-pixel PNG labelled as synthetic test-only data."""

    def chunk(name: bytes, data: bytes) -> bytes:
        payload = name + data
        return struct.pack(">I", len(data)) + payload + struct.pack(
            ">I", zlib.crc32(payload) & 0xFFFFFFFF
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes((0, *rgb))))
        + chunk(b"IEND", b"")
    )


def multipart_payload(fields: dict[str, str], original: bytes) -> tuple[bytes, str]:
    """Construct a well-formed upload request without a browser or mock service."""

    boundary = "sitepay" + uuid4().hex
    body = bytearray()
    for field_name, value in fields.items():
        body.extend(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{field_name}"'
            "\r\n\r\n".encode()
        )
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")
    body.extend(
        f'--{boundary}\r\nContent-Disposition: form-data; '
        'name="original"; filename="synthetic.png"\r\n'
        "Content-Type: image/png\r\n\r\n".encode()
    )
    body.extend(original)
    body.extend(f"\r\n--{boundary}--\r\n".encode())
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def upload(
    project_id: str, token: str, fields: dict[str, str], original: bytes
) -> tuple[int, dict]:
    """POST original bytes and return only the status and structured receipt."""

    payload, content_type = multipart_payload(fields, original)
    request = Request(
        f"{BASE_URL}/projects/{project_id}/evidence",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def get_original(project_id: str, evidence_id: str, token: str) -> tuple[int, bytes]:
    """Retrieve server-verified original bytes from the actual HTTP API."""

    request = Request(
        f"{BASE_URL}/projects/{project_id}/evidence/{evidence_id}/content",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(request, timeout=12) as response:
            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers["Content-Disposition"].startswith("attachment;")
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def verify_evidence_workflow() -> None:
    """Prove tenant restriction, idempotency and exact-byte persistence in MinIO."""

    require_ready()
    owner_status, account = request_json(
        "/auth/register",
        {
            "email": f"evidence-ci-{uuid4().hex}@example.com",
            "password": secrets.token_urlsafe(24),
            "full_name": "CI synthetic evidence owner",
            "organization_name": "CI synthetic contractor",
        },
    )
    assert owner_status == 201
    token = account["access_token"]
    _, project = request_json(
        "/projects",
        {"organization_id": account["organization_id"], "name": "CI synthetic job"},
        token,
    )
    _, site = request_json(
        f"/projects/{project['id']}/sites", {"name": "CI synthetic block"}, token
    )
    first = synthetic_png((12, 34, 56))
    changed = synthetic_png((56, 34, 12))
    device_id, operation_id = str(uuid4()), str(uuid4())
    fields = {
        "device_id": device_id,
        "client_record_id": operation_id,
        "site_id": site["id"],
        "kind": "photo",
    }
    status, received = upload(project["id"], token, fields, first)
    assert status == 201, received
    source = received["evidence"]
    assert received["reused_original"] is False
    assert source["sha256"] == hashlib.sha256(first).hexdigest()
    assert source["size_bytes"] == len(first)
    assert source["content_type"] == "image/png"
    assert get_original(project["id"], source["id"], token) == (200, first)

    status, retry = upload(project["id"], token, fields, first)
    assert status == 200 and retry["evidence"]["id"] == source["id"]
    status, conflict = upload(project["id"], token, fields, changed)
    assert status == 409 and conflict["detail"] == "Device operation key was already used"

    second = {**fields, "device_id": str(uuid4()), "client_record_id": str(uuid4())}
    status, deduplicated = upload(project["id"], token, second, first)
    assert status == 200 and deduplicated["evidence"]["id"] == source["id"]
    status, stored = request_json(f"/projects/{project['id']}/evidence", token=token)
    assert status == 200 and len(stored["items"]) == 1
    status, acknowledgement = request_json(
        f"/projects/{project['id']}/sync/operations/{device_id}/{operation_id}",
        token=token,
    )
    assert status == 200 and acknowledgement["status"] == "acknowledged"
    assert acknowledgement["sha256"] == source["sha256"]

    invalid = {**fields, "client_record_id": str(uuid4())}
    assert upload(project["id"], token, invalid, b"MZbad executable")[0] == 415
    other_id = {**fields, "client_record_id": str(uuid4()), "site_id": str(uuid4())}
    assert upload(project["id"], token, other_id, first)[0] == 404

    _, outsider = request_json(
        "/auth/register",
        {
            "email": f"outsider-ci-{uuid4().hex}@example.com",
            "password": secrets.token_urlsafe(24),
            "full_name": "CI synthetic outsider",
            "organization_name": "CI unrelated contractor",
        },
    )
    assert get_original(project["id"], source["id"], outsider["access_token"])[0] == 404
    status, audit = request_json(
        f"/organizations/{account['organization_id']}/audit", token=token
    )
    assert status == 200
    assert sum(row["action"] == "evidence.acknowledged" for row in audit) == 2
    print("PASS live S3 original, retry, conflict, dedupe, tenant, receipt and audit flow")


if __name__ == "__main__":
    verify_evidence_workflow()
