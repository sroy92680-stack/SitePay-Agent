#Owner::ANIKET::ANHOTRA = MR.Panda
"""End-to-end identity and token boundary tests against migrated tables."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.tests.conftest import authentication_headers, registered_account


def test_register_login_and_me(client: TestClient) -> None:
    """Registration creates an owner tenant and a usable signed session."""
    account = registered_account(client, "ENGINEER@example.com")
    assert account["user"]["email"] == "engineer@example.com"
    assert "password_hash" not in account["user"]
    headers = authentication_headers(account)
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == account["user"]["id"]
    login = client.post(
        "/auth/login",
        json={"email": "engineer@example.com", "password": "correct-horse-battery-staple"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    organizations = client.get("/organizations", headers=headers)
    assert organizations.status_code == 200
    assert len(organizations.json()) == 1


def test_duplicate_email_and_invalid_password(client: TestClient) -> None:
    """Refuse duplicate identities and generic wrong credential attempts."""
    registered_account(client, "one@example.com")
    duplicate = client.post(
        "/auth/register",
        json={
            "email": "One@Example.com",
            "password": "new-strong-test-password",
            "full_name": "Duplicate",
            "organization_name": "Other",
        },
    )
    assert duplicate.status_code == 409
    for email, password in [
        ("one@example.com", "not-the-correct-password"),
        ("missing@example.com", "not-the-correct-password"),
    ]:
        response = client.post("/auth/login", json={"email": email, "password": password})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


def test_auth_required_and_invalid_token(client: TestClient) -> None:
    """Do not permit anonymous requests or arbitrary signed-token strings."""
    assert client.get("/projects").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer rubbish"}).status_code == 401


def test_validation_does_not_echo_password(client: TestClient) -> None:
    """Reject malformed credentials without revealing raw password text."""
    password = "leak-this-short-password"
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": password, "full_name": "",
              "organization_name": "Trial"},
    )
    assert response.status_code == 422
    assert password not in response.text
