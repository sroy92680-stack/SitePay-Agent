#Owner::ANIKET::ANHOTRA = MR.Panda
"""Service health and role-specific construction site permissions."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.tests.conftest import authentication_headers, registered_account


def test_liveness_and_database_readiness(client: TestClient) -> None:
    """Health endpoints reflect a live web process and migrated database."""
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_site_engineer_may_add_site_but_not_project(client: TestClient) -> None:
    """Allow engineering tasks while reserving project creation for managers."""
    owner = registered_account(client, "owner_engineer@example.com")
    engineer = registered_account(client, "engineer_member@example.com")
    owner_headers = authentication_headers(owner)
    engineer_headers = authentication_headers(engineer)
    project_response = client.post(
        "/projects",
        headers=owner_headers,
        json={"organization_id": owner["organization_id"], "name": "Real test boundary"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    invitation = client.post(
        f"/organizations/{owner['organization_id']}/members",
        headers=owner_headers,
        json={"email": engineer["user"]["email"], "role": "site_engineer"},
    )
    assert invitation.status_code == 201
    assert client.post(
        f"/projects/{project_id}/sites",
        headers=engineer_headers,
        json={"name": "Before acceptance"},
    ).status_code == 404
    assert client.post(
        f"/organizations/{owner['organization_id']}/invitations/accept",
        headers=engineer_headers,
    ).status_code == 200
    assert client.post(
        "/projects",
        headers=engineer_headers,
        json={"organization_id": owner["organization_id"], "name": "Denied by role"},
    ).status_code == 403
    site = client.post(
        f"/projects/{project_id}/sites",
        headers=engineer_headers,
        json={"name": "East block", "location_description": "Manually entered"},
    )
    assert site.status_code == 201, site.text
    assert site.json()["name"] == "East block"


def test_owner_cannot_accept_another_users_invitation(client: TestClient) -> None:
    """Only the invited user may accept their own pending membership."""
    owner = registered_account(client, "owner_request@example.com")
    invitee = registered_account(client, "recipient_request@example.com")
    headers = authentication_headers(owner)
    created = client.post(
        f"/organizations/{owner['organization_id']}/members",
        headers=headers,
        json={"email": invitee["user"]["email"], "role": "accounts"},
    )
    assert created.status_code == 201
    owner_accept = client.post(
        f"/organizations/{owner['organization_id']}/invitations/accept",
        headers=headers,
    )
    assert owner_accept.status_code == 404
    recipient_accept = client.post(
        f"/organizations/{owner['organization_id']}/invitations/accept",
        headers=authentication_headers(invitee),
    )
    assert recipient_accept.status_code == 200
    assert recipient_accept.json()["role"] == "accounts"
