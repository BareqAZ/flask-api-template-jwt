from .conftest import users

headers_admin = {
    "Authorization": f'Bearer {users["admin"]["api_key"]}',
    "Content-Type": "application/json",
}
headers_user = {
    "Authorization": f'Bearer {users["user"]["api_key"]}',
    "Content-Type": "application/json",
}


def test_user_auth_and_access(client):
    # Check JWT API access
    resp = client.get("/api/v1/jwt-check", headers=headers_user)
    assert resp.status_code == 422

    # Check JWT API access
    resp = client.get("/api/v1/jwt-admin-check", headers=headers_user)
    assert resp.status_code == 422

    # Get JWT access token
    resp = client.post("/api/v1/auth", headers=headers_user)
    assert resp.status_code == 200
    jwt_token = resp.json["access_token"]
    new_user_headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }

    # Check JWT API access
    resp = client.get("/api/v1/jwt-check", headers=new_user_headers)
    assert resp.status_code == 200

    # Check JWT API access
    resp = client.get("/api/v1/jwt-admin-check", headers=new_user_headers)
    assert resp.status_code == 403

    # Check regular routes
    resp = client.get("/api/v1/check", headers=new_user_headers)
    assert resp.status_code == 403
    resp = client.get("/api/v1/admin-check", headers=new_user_headers)
    assert resp.status_code == 403

    # Check with the initial API key
    resp = client.get("/api/v1/check", headers=headers_user)
    assert resp.status_code == 200
    resp = client.get("/api/v1/admin-check", headers=headers_user)
    assert resp.status_code == 403


def test_admin_auth_and_access(client):
    # Check JWT API access
    resp = client.get("/api/v1/jwt-check", headers=headers_admin)
    assert resp.status_code == 422

    # Check JWT API access
    resp = client.get("/api/v1/jwt-admin-check", headers=headers_admin)
    assert resp.status_code == 422

    # Get JWT access token
    resp = client.post("/api/v1/auth", headers=headers_admin)
    assert resp.status_code == 200
    jwt_token = resp.json["access_token"]
    new_admin_headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }

    # Check JWT API access
    resp = client.get("/api/v1/jwt-check", headers=new_admin_headers)
    assert resp.status_code == 200

    # Check JWT API access
    resp = client.get("/api/v1/jwt-admin-check", headers=new_admin_headers)
    assert resp.status_code == 200

    # Check regular routes
    resp = client.get("/api/v1/check", headers=new_admin_headers)
    assert resp.status_code == 403
    resp = client.get("/api/v1/admin-check", headers=new_admin_headers)
    assert resp.status_code == 403

    # Check with the initial API key
    resp = client.get("/api/v1/check", headers=headers_admin)
    assert resp.status_code == 200
    resp = client.get("/api/v1/admin-check", headers=headers_admin)
    assert resp.status_code == 200
