"""Role-based access matrix tests."""
import pytest

pytestmark = pytest.mark.skip(reason="Role matrix tests require dedicated Postgres/Redis setup; skipped locally")

ROLE_TO_FIXTURE = {
    "admin": "admin_headers",
    "user": "auth_headers",
    "viewer": "viewer_headers",
}

ENDPOINT_MATRIX = [
    ("GET", "/api/v1/documents", {"admin": 200, "user": 200, "viewer": 200}),
    ("GET", "/api/v1/proposals", {"admin": 200, "user": 200, "viewer": 200}),
    ("GET", "/api/v1/templates", {"admin": 200, "user": 200, "viewer": 200}),
    ("GET", "/api/v1/knowledge", {"admin": 200, "user": 200, "viewer": 200}),
]


@pytest.mark.parametrize("method,path,expectations", ENDPOINT_MATRIX)
@pytest.mark.parametrize("role", ["admin", "user", "viewer"])
def test_role_matrix(
    method,
    path,
    expectations,
    role,
    test_client,
    admin_headers,
    auth_headers,
    viewer_headers,
):
    headers_map = {
        "admin": admin_headers,
        "user": auth_headers,
        "viewer": viewer_headers,
    }
    response = test_client.request(method, path, headers=headers_map[role])
    assert response.status_code == expectations[role]
