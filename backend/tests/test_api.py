import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PROTECTED = [
    ("GET", "/api/v1/projects"),
    ("POST", "/api/v1/projects"),
    ("GET", f"/api/v1/projects/{uuid.uuid4()}/documents"),
    ("POST", f"/api/v1/projects/{uuid.uuid4()}/chat"),
]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


@pytest.mark.parametrize("method,path", PROTECTED)
def test_protected_endpoints_require_token(method, path):
    assert client.request(method, path, json={}).status_code == 401
