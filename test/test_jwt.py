import json
from .conftest import users

headers_admin = {'Authorization': f'Bearer {users["admin"]["api_key"]}',
                 'Content-Type': 'application/json'}
headers_user  = {'Authorization': f'Bearer {users["user"]["api_key"]}',
                 'Content-Type': 'application/json'}


def test_user_auth_and_access(client):
    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-check', headers=headers_user)
    assert resp.status_code == 422

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-admin-check', headers=headers_user)
    assert resp.status_code == 422

    # Get JWT access token
    resp = client.post(f'/api/v1/auth', headers=headers_user)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-check', headers=new_user_headers)
    assert resp.status_code == 200

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-admin-check', headers=new_user_headers)
    assert resp.status_code == 403

    # Check regular routes
    resp = client.get(f'/api/v1/check', headers=new_user_headers)
    assert resp.status_code == 403
    resp = client.get(f'/api/v1/admin-check', headers=new_user_headers)
    assert resp.status_code == 403

    # Check with the initial API key
    resp = client.get(f'/api/v1/check', headers=headers_user)
    assert resp.status_code == 200
    resp = client.get(f'/api/v1/admin-check', headers=headers_user)
    assert resp.status_code == 403


def test_admin_auth_and_access(client):
    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-check', headers=headers_admin)
    assert resp.status_code == 422

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-admin-check', headers=headers_admin)
    assert resp.status_code == 422

    # Get JWT access token
    resp = client.post(f'/api/v1/auth', headers=headers_admin)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_admin_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-check', headers=new_admin_headers)
    assert resp.status_code == 200

    # Check JWT API access
    resp = client.get(f'/api/v1/jwt-admin-check', headers=new_admin_headers)
    assert resp.status_code == 200

    # Check regular routes
    resp = client.get(f'/api/v1/check', headers=new_admin_headers)
    assert resp.status_code == 403
    resp = client.get(f'/api/v1/admin-check', headers=new_admin_headers)
    assert resp.status_code == 403

    # Check with the initial API key
    resp = client.get(f'/api/v1/check', headers=headers_admin)
    assert resp.status_code == 200
    resp = client.get(f'/api/v1/admin-check', headers=headers_admin)
    assert resp.status_code == 200


def test_refresh_tokens(client):
    # Get JWT access token
    resp = client.post(f'/api/v1/auth', headers=headers_user)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Refresh access token
    headers_old = new_user_headers
    resp = client.post(f'/api/v1/refresh', headers=new_user_headers)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Refresh access token again
    resp = client.post(f'/api/v1/refresh', headers=new_user_headers)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Check first access token
    resp = client.get(f'/api/v1/jwt-check', headers=headers_old)
    assert resp.status_code == 401

    # Check new access token
    resp = client.get(f'/api/v1/jwt-check', headers=new_user_headers)
    assert resp.status_code == 200


def test_logout(client):
    # Get JWT access token
    resp = client.post(f'/api/v1/auth', headers=headers_user)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Refresh access token
    headers_1 = new_user_headers
    resp = client.post(f'/api/v1/refresh', headers=new_user_headers)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}

    # Refresh access token again
    headers_2 = new_user_headers
    resp = client.post(f'/api/v1/refresh', headers=new_user_headers)
    assert resp.status_code == 200
    jwt_token = resp.json['access_token']
    new_user_headers = {'Authorization': f'Bearer {jwt_token}',
                        'Content-Type': 'application/json'}
    headers_3 = new_user_headers

    # Logout
    resp = client.post(f'/api/v1/logout', headers=headers_3)
    assert resp.status_code == 200

    # Test old tokens
    # Check first access token
    resp = client.get(f'/api/v1/jwt-check', headers=headers_1)
    assert resp.status_code == 401

    # Check 2nd access token
    resp = client.get(f'/api/v1/jwt-check', headers=headers_2)
    assert resp.status_code == 401

    # Check 3rd access token
    resp = client.get(f'/api/v1/jwt-check', headers=headers_3)
    assert resp.status_code == 401
