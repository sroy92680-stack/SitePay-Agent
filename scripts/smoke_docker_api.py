#Owner::ANIKET::ANHOTRA = MR.Panda
"""Exercise a live Docker-backed API without fabricated business records."""

from __future__ import annotations

import json
import secrets
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000"


def request_json(
    path: str, payload: dict[str, Any] | None = None, token: str | None = None
) -> tuple[int, dict[str, Any] | list[Any]]:
    """Call a running HTTP endpoint and decode the JSON response.

    Preserve API failure codes without exposing test-only credentials.
    """
    headers = {"Accept": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{BASE_URL}{path}",
        data=body,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        raise AssertionError(f"API status {error.code} for {path}") from error


def require_ready() -> None:
    """Check whether the actual container is serving migrated database requests.

    Fail after a bounded number of connection attempts.
    """
    for attempt in range(30):
        try:
            status, response = request_json("/health/ready")
            if status == 200 and response == {"status": "ready"}:
                return
        except (URLError, OSError, AssertionError):
            pass
        time.sleep(1)
    raise RuntimeError("API readiness check failed")


def verify_smoke_workflow() -> None:
    """Run register, login, project, site and audit through a real HTTP server.

    All generated identifiers are CI-only and the database is disposed after CI.
    """
    require_ready()
    email = f"ci-{uuid4()}@example.invalid"
    password = secrets.token_urlsafe(24)
    status, account = request_json(
        "/auth/register",
        {
            "email": email,
            "password": password,
            "full_name": "CI synthetic user",
            "organization_name": "CI synthetic contractor",
            "preferred_language": "en",
        },
    )
    assert status == 201
    assert isinstance(account, dict)
    token = account["access_token"]
    assert "password_hash" not in account["user"]
    login_status, login = request_json(
        "/auth/login", {"email": email, "password": password}
    )
    assert login_status == 200
    assert isinstance(login, dict)
    assert login["access_token"]
    status, project = request_json(
        "/projects",
        {
            "organization_id": account["organization_id"],
            "name": "CI synthetic project",
        },
        token,
    )
    assert status == 201
    assert isinstance(project, dict)
    assert project["contract_value"] is None
    project_id = project["id"]
    status, sites = request_json(
        f"/projects/{project_id}/sites",
        {"name": "CI synthetic site", "location_description": "Not a real location"},
        token,
    )
    assert status == 201
    assert isinstance(sites, dict)
    status, listed_projects = request_json("/projects", token=token)
    assert status == 200 and isinstance(listed_projects, list)
    assert any(item["id"] == project_id for item in listed_projects)
    status, audit = request_json(
        f"/organizations/{account['organization_id']}/audit", token=token
    )
    assert status == 200 and isinstance(audit, list)
    actions = {event["action"] for event in audit}
    assert {"account.registered", "project.created", "site.created"}.issubset(actions)
    print("PASS Docker HTTP registration, login, project, site and audited workflow")


if __name__ == "__main__":
    verify_smoke_workflow()
