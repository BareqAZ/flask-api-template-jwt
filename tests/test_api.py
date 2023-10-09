import json

from .conftest import users

headers_admin = {
    "Authorization": f'Bearer {users["admin"]["api_key"]}',
    "Content-Type": "application/json",
}
headers_user = {
    "Authorization": f'Bearer {users["user"]["api_key"]}',
    "Content-Type": "application/json",
}


def test_api_check(client):
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200

    # Incorrect token check
    resp = client.get("/api/v1/check", headers={"Authorization": "Bearer NotRealToken"})
    assert resp.status_code == 403
    assert resp.json["error"] == "A valid authorization token is required"

    # Incorrect token check
    resp = client.get(
        "/api/v1/admin-check", headers={"Authorization": "Bearer NotRealToken"}
    )
    assert resp.status_code == 403
    assert resp.json["error"] == "A valid authorization token is required"

    # User API token check
    resp = client.get("/api/v1/check", headers=headers_user)
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"

    # User API token check
    resp = client.get("/api/v1/admin-check", headers=headers_user)
    assert resp.status_code == 403
    assert (
        resp.json["error"]
        == "You don't have the permission to access the requested resource. "
        "It is either read-protected or not readable by the server."
    )

    # Admin API token check
    resp = client.get("/api/v1/check", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"

    # Admin API token check
    resp = client.get("/api/v1/admin-check", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"


def test_user_access(client):
    # List users
    resp = client.get("/api/v1/users", headers=headers_user)
    assert resp.status_code == 403

    # Add user
    resp = client.post(
        "/api/v1/users",
        headers=headers_user,
        data=json.dumps({"name": "pytest", "email": "user@pytest"}),
    )
    assert resp.status_code == 403

    # Get user
    resp = client.get("/api/v1/users/random", headers=headers_user)
    assert resp.status_code == 403

    # Modify user
    resp = client.patch("/api/v1/users/random", headers=headers_user)
    assert resp.status_code == 403

    # Delete user
    resp = client.delete("/api/v1/users/random", headers=headers_user)
    assert resp.status_code == 403


def test_admin_user_management_api(client):
    # List all users
    # This should return 3, one initial superuser created on the first run
    # And the 2 Users added by pytest
    resp = client.get("/api/v1/users", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 3

    # Add user 1
    resp = client.post(
        "/api/v1/users",
        headers=headers_admin,
        data=json.dumps(
            {"first_name": "json", "last_name": "derulo", "email": "user1@pytest.local"}
        ),
    )
    user_1 = resp.json["id"]
    assert resp.status_code == 201

    # Add user 2
    resp = client.post(
        "/api/v1/users",
        headers=headers_admin,
        data=json.dumps(
            {
                "first_name": "json2",
                "last_name": "derulo",
                "email": "user2@pytest.local",
            }
        ),
    )
    user_2 = resp.json["id"]
    assert resp.status_code == 201

    # Add user 1 again, this should fail
    resp = client.post(
        "/api/v1/users",
        headers=headers_admin,
        data=json.dumps(
            {
                "first_name": "json2",
                "last_name": "derulo",
                "email": "user2@pytest.local",
            }
        ),
    )
    assert resp.status_code == 400

    # List all
    resp = client.get("/api/v1/users", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 5

    # Get user 1
    resp = client.get(f"/api/v1/users/{user_1}", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json["first_name"] == "json"
    assert resp.json["last_name"] == "derulo"
    assert resp.json["email"] == "user1@pytest.local"
    assert resp.json["is_admin"] is False
    assert resp.json["is_active"] is True

    # Modify user 1 name
    resp = client.patch(
        f"/api/v1/users/{user_1}",
        headers=headers_admin,
        data=json.dumps({"first_name": "Jay"}),
    )
    assert resp.status_code == 200

    # Get user 1
    resp = client.get(f"/api/v1/users/{user_1}", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json["first_name"] == "Jay"
    assert resp.json["last_name"] == "derulo"
    assert resp.json["email"] == "user1@pytest.local"
    assert resp.json["is_admin"] is False
    assert resp.json["is_active"] is True

    # Modify user 1 email to an existing email
    resp = client.patch(
        f"/api/v1/users/{user_1}",
        headers=headers_admin,
        data=json.dumps({"email": "user2@pytest.local"}),
    )
    assert resp.status_code == 400
    assert resp.json["error"] == "Email already exists"

    # Modify user 1 email
    resp = client.patch(
        f"/api/v1/users/{user_1}",
        headers=headers_admin,
        data=json.dumps({"email": "json@pytest.local"}),
    )
    assert resp.status_code == 200

    # Get user 1
    resp = client.get(f"/api/v1/users/{user_1}", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json["first_name"] == "Jay"
    assert resp.json["last_name"] == "derulo"
    assert resp.json["email"] == "json@pytest.local"
    assert resp.json["is_admin"] is False
    assert resp.json["is_active"] is True

    # Delete user 1
    resp = client.delete(f"/api/v1/users/{user_1}", headers=headers_admin)
    assert resp.status_code == 200

    # List all
    resp = client.get("/api/v1/users", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 4

    # Delete user 2
    resp = client.delete(f"/api/v1/users/{user_2}", headers=headers_admin)
    assert resp.status_code == 200

    # List all
    resp = client.get("/api/v1/users", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 3


def test_pagination(client):
    # Add 100 users to test pagination
    for n in range(100):
        resp = client.post(
            "/api/v1/users",
            headers=headers_admin,
            data=json.dumps(
                {
                    "first_name": "json",
                    "last_name": "derulo",
                    "email": f"user{n}@pytest.local",
                }
            ),
        )
        assert resp.status_code == 201

    # Test pagination
    resp = client.get("/api/v1/users?page=1&per_page=20", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 20

    resp = client.get("/api/v1/users?page=1&per_page=50", headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 50

    # Next page navigation
    resp = client.get(resp.json["next_page"], headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 50

    resp = client.get(resp.json["next_page"], headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 3

    # Prev page navigation
    resp = client.get(resp.json["prev_page"], headers=headers_admin)
    assert resp.status_code == 200
    assert len(resp.json["users"]) == 50

    # Incorrect page
    resp = client.get("/api/v1/users?page=-1", headers=headers_admin)
    assert resp.status_code == 404

    resp = client.get("/api/v1/users?page=1000", headers=headers_admin)
    assert resp.status_code == 404

    resp = client.get("/api/v1/users?per_page=-20", headers=headers_admin)
    assert resp.status_code == 404

    resp = client.get("/api/v1/users?per_page=10000", headers=headers_admin)
    assert resp.status_code == 400


def test_user_actions(client):
    # Add user 1
    resp = client.post(
        "/api/v1/users",
        headers=headers_admin,
        data=json.dumps(
            {"first_name": "json", "last_name": "derulo", "email": "user1@pytest.local"}
        ),
    )
    user_id = resp.json["id"]
    user_original_api_key = resp.json["api_key"]

    # Test user 1 original API key
    resp = client.get(
        "/api/v1/check", headers={"Authorization": f"Bearer {user_original_api_key}"}
    )
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"

    # Update API key
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 200
    resp = client.post(
        resp.json["actions"]["regen-api-key"]["uri"], headers=headers_admin
    )
    assert resp.status_code == 200
    user_new_api_key = resp.json["api_key"]

    # Test user 1 original API key
    resp = client.get(
        "/api/v1/check", headers={"Authorization": f"Bearer {user_original_api_key}"}
    )
    assert resp.status_code == 403

    # Test user 1 new API key
    resp = client.get(
        "/api/v1/check", headers={"Authorization": f"Bearer {user_new_api_key}"}
    )
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"
    assert user_original_api_key != user_new_api_key

    # Update user
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 200
    resp = client.patch(
        resp.json["actions"]["modify-user"]["uri"],
        headers=headers_admin,
        data=json.dumps({"email": "lol@pytest.local"}),
    )

    # Read user
    assert resp.status_code == 200
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers_admin)
    assert resp.json["email"] == "lol@pytest.local"

    # Delete user
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 200
    resp = client.delete(
        resp.json["actions"]["delete-user"]["uri"], headers=headers_admin
    )
    assert resp.status_code == 200

    # Read user
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 404


def test_user_lifetime(client):
    # Add a new user
    resp = client.post(
        "/api/v1/users",
        headers=headers_admin,
        data=json.dumps(
            {"first_name": "json", "last_name": "derulo", "email": "user1@pytest.local"}
        ),
    )
    assert resp.status_code == 201
    user_id = resp.json["id"]
    user_api_key = resp.json["api_key"]

    headers_new_user = {
        "Authorization": f"Bearer {user_api_key}",
        "Content-Type": "application/json",
    }

    # Check user access to user API
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 200
    assert resp.json["message"] == "API token is valid"

    # Check user access to admin API
    resp = client.get("/api/v1/admin-check", headers=headers_new_user)
    assert resp.status_code == 403
    assert (
        resp.json["error"]
        == "You don't have the permission to access the requested resource. "
        "It is either read-protected or not readable by the server."
    )

    # Modify privileges
    resp = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers_admin,
        data=json.dumps({"is_admin": True}),
    )
    assert resp.status_code == 200

    # Check user access to admin API
    resp = client.get("/api/v1/admin-check", headers=headers_new_user)
    assert resp.status_code == 200

    # Regen user API key
    resp = client.post(f"/api/v1/users/{user_id}/gen-api-key", headers=headers_admin)
    assert resp.status_code == 200
    user_api_key = resp.json["api_key"]

    # Check old key access
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 403

    headers_new_user = {
        "Authorization": f"Bearer {user_api_key}",
        "Content-Type": "application/json",
    }

    # Check new key access
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 200

    # Update user API key manually
    user_api_key = "This-Is-Test-Key"
    resp = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers_admin,
        data=json.dumps({"api_key": user_api_key}),
    )
    assert resp.status_code == 200

    # Check old key access
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 403

    headers_new_user = {
        "Authorization": f"Bearer {user_api_key}",
        "Content-Type": "application/json",
    }

    # Check new key access
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 200

    # Disable account
    resp = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers_admin,
        data=json.dumps({"is_active": False}),
    )
    assert resp.status_code == 200

    # Check user access to user API
    resp = client.get("/api/v1/check", headers=headers_new_user)
    assert resp.status_code == 403
    assert resp.json["error"] == "Inactive account"

    # Check user access to admin API
    resp = client.get("/api/v1/admin-check", headers=headers_new_user)
    assert resp.status_code == 403
    assert resp.json["error"] == "Inactive account"
