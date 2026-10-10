from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    assert client.get("/").status_code == 200

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_ask_requires_auth():
    assert client.post("/ask", json={"question": "hi"}).status_code in (401, 403)

def test_history_requires_auth():
    assert client.get("/history").status_code in (401, 403)

def test_admin_requires_auth():
    assert client.get("/admin/documents").status_code in (401, 403)

def test_login_wrong_password():
    r = client.post("/login", json={"email": "nobody@x.com", "password": "wrong"})
    assert "error" in r.json()