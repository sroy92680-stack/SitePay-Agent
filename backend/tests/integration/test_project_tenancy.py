#Owner::ANIKET::ANHOTRA = MR.Panda
"""Project, role and site integration tests enforcing customer isolation."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.tests.conftest import authentication_headers, registered_account


def test_owner_can_create_project_and_site(client: TestClient) -> None:
    """A registered owner can create and read their project and site."""
    owner = registered_account(client, "owner@example.com")
    headers = authentication_headers(owner)
    project_response = client.post(
        "/projects",
        headers=headers,
        json={"organization_id": owner["organization_id"], "name": "Site Alpha"},
    )
    assert project_response.status_code == 201, project_response.text
    project = project_response.json()
    assert project["contract_value"] is None
    assert client.get("/projects", headers=headers).json()[0]["id"] == project["id"]
    site_response = client.post(
        f"/projects/{project['id']}/sites",
        headers=headers,
        json={"name": "Main Building", "location_description": "Building A"},
    )
    assert site_response.status_code == 201, site_response.text
    sites = client.get(f"/projects/{project['id']}/sites", headers=headers)
    assert sites.status_code == 200
    assert sites.json()[0]["name"] == "Main Building"
    audit = client.get(
        f"/organizations/{owner['organization_id']}/audit", headers=headers
    )
    assert audit.status_code == 200
    assert {"account.registered", "project.created", "site.created"}.issubset(
        {event["action"] for event in audit.json()}
    )


def test_cross_tenant_access_is_denied(client: TestClient) -> None:
    """Do not reveal another organisation's project, audit or site records."""
    owner_a = registered_account(client, "owner_a@example.com", "Alpha")
    owner_b = registered_account(client, "owner_b@example.com", "Beta")
    headers_a = authentication_headers(owner_a)
    headers_b = authentication_headers(owner_b)
    project = client.post(
        "/projects",
        headers=headers_a,
        json={"organization_id": owner_a["organization_id"], "name": "Private project"},
    ).json()
    assert client.get(f"/projects/{project['id']}", headers=headers_b).status_code == 404
    assert client.get(f"/projects/{project['id']}/sites", headers=headers_b).status_code == 404
    assert client.get(
        f"/organizations/{owner_a['organization_id']}/audit", headers=headers_b
    ).status_code == 404
    assert client.get("/projects", headers=headers_b).json() == []
    assert client.post(
        "/projects",
        headers=headers_b,
        json={"organization_id": owner_a["organization_id"], "name": "Intrusion"},
    ).status_code == 404


def test_worker_role_cannot_create_project_or_site(client: TestClient) -> None:
    """A tenant owner may grant a worker read access without write authority."""
    owner = registered_account(client, "worker_admin@example.com")
    worker = registered_account(client, "worker_account@example.com")
    owner_headers = authentication_headers(owner)
    worker_headers = authentication_headers(worker)
    add = client.post(
        f"/organizations/{owner['organization_id']}/members",
        headers=owner_headers,
        json={"email": worker["user"]["email"], "role": "worker"},
    )
    assert add.status_code == 201, add.text
    assert add.json()["status"] == "pending"
    pending = client.get("/organizations/invitations/pending", headers=worker_headers)
    assert pending.status_code == 200
    assert len(pending.json()) == 1
    assert client.get("/projects", headers=worker_headers).json() == []
    acceptance = client.post(
        f"/organizations/{owner['organization_id']}/invitations/accept",
        headers=worker_headers,
    )
    assert acceptance.status_code == 200
    assert acceptance.json()["status"] == "active"
    assert client.get("/organizations/invitations/pending", headers=worker_headers).json() == []
    project = client.post(
        "/projects",
        headers=owner_headers,
        json={"organization_id": owner["organization_id"], "name": "Shared site"},
    ).json()
    assert client.get(f"/projects/{project['id']}", headers=worker_headers).status_code == 200
    assert client.post(
        "/projects",
        headers=worker_headers,
        json={"organization_id": owner["organization_id"], "name": "Denied"},
    ).status_code == 403
    assert client.post(
        f"/projects/{project['id']}/sites",
        headers=worker_headers,
        json={"name": "Worker not permitted"},
    ).status_code == 403
    assert client.post(
        f"/organizations/{owner['organization_id']}/members",
        headers=worker_headers,
        json={"email": "worker_admin@example.com", "role": "worker"},
    ).status_code == 403


def test_decimal_finance_input_must_not_be_float(client: TestClient) -> None:
    """Protect future financial math from floating point input ambiguity."""
    account = registered_account(client, "finance_owner@example.com")
    headers = authentication_headers(account)
    base = {"organization_id": account["organization_id"], "name": "Contracts"}
    incorrect = client.post(
        "/projects", headers=headers, json={**base, "contract_value": 1.234}
    )
    assert incorrect.status_code == 422
    good = client.post(
        "/projects", headers=headers, json={**base, "contract_value": "1000.10"}
    )
    assert good.status_code == 201, good.text
    assert good.json()["contract_value"] == "1000.10"
