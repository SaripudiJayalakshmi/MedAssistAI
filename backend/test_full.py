import time
import pytest
from fastapi.testclient import TestClient
from main import app
from database.db import users_collection
from services.auth_service import create_access_token
from services.chat_service import messages_collection

client = TestClient(app)

TEST_EMAIL = "pytest_user@example.com"
TEST_PASSWORD = "PytestPass123!"


def auth(email):
    token = create_access_token({"sub": email, "name": "pytest"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module", autouse=True)
def test_user():
    users_collection.delete_one({"email": TEST_EMAIL})
    r = client.post("/register", json={"name": "Pytest", "email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 200
    yield
    users_collection.delete_one({"email": TEST_EMAIL})
    messages_collection.delete_many({"user_email": TEST_EMAIL})


@pytest.fixture(scope="module")
def admin_headers():
    admin = users_collection.find_one({"is_admin": True})
    assert admin, "No admin user found in the database"
    return auth(admin["email"])


# ---------- Authentication ----------

def test_register_duplicate_rejected():
    r = client.post("/register", json={"name": "x", "email": TEST_EMAIL, "password": "x"})
    assert "error" in r.json()


def test_login_success_returns_token():
    r = client.post("/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    body = r.json()
    assert r.status_code == 200 and "access_token" in body and body["is_admin"] is False


def test_login_wrong_password():
    r = client.post("/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert "error" in r.json()


@pytest.mark.parametrize("path", ["/history", "/bookmarks", "/admin/documents", "/admin/analytics"])
def test_protected_get_routes_require_login(path):
    assert client.get(path).status_code in (401, 403)


def test_ask_requires_login():
    assert client.post("/ask", json={"question": "hi"}).status_code in (401, 403)


def test_ask_image_requires_login():
    r = client.post("/ask-image", files={"file": ("a.png", b"x", "image/png")})
    assert r.status_code in (401, 403)


# ---------- Admin permissions and documents ----------

def test_non_admin_blocked_from_admin_routes():
    h = auth(TEST_EMAIL)
    assert client.get("/admin/documents", headers=h).status_code == 403
    assert client.get("/admin/analytics", headers=h).status_code == 403
    r = client.post("/upload", headers=h, files={"file": ("a.pdf", b"x", "application/pdf")})
    assert r.status_code == 403


def test_admin_list_documents_shape(admin_headers):
    r = client.get("/admin/documents", headers=admin_headers)
    assert r.status_code == 200
    for d in r.json()["documents"]:
        assert {"filename", "chunk_count", "status"} <= set(d)


def test_admin_rejects_non_pdf_upload(admin_headers):
    r = client.post("/upload", headers=admin_headers, files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_corrupt_pdf_marked_failed_then_removed(admin_headers):
    r = client.post("/upload", headers=admin_headers, files={"file": ("pytest_fake.pdf", b"not a pdf", "application/pdf")})
    assert r.status_code == 422
    docs = client.get("/admin/documents", headers=admin_headers).json()["documents"]
    assert any(d["filename"] == "pytest_fake.pdf" and d["status"] == "failed" for d in docs)
    assert client.delete("/admin/documents/pytest_fake.pdf", headers=admin_headers).status_code == 200
    docs = client.get("/admin/documents", headers=admin_headers).json()["documents"]
    assert not any(d["filename"] == "pytest_fake.pdf" for d in docs)


# ---------- RAG, evidence, safety ----------

def test_ask_returns_evidence_structure_and_is_fast():
    start = time.perf_counter()
    r = client.post("/ask", headers=auth(TEST_EMAIL), json={"question": "What symptoms suggest CNS involvement?"})
    elapsed = time.perf_counter() - start
    body = r.json()
    assert r.status_code == 200
    assert {"answer", "sources", "evidence", "grounded", "message_id"} <= set(body)
    assert body["answer"].strip()
    for e in body["evidence"]:
        assert {"document", "page", "passage"} <= set(e)
    assert elapsed < 30


def test_off_topic_question_is_not_grounded():
    r = client.post("/ask", headers=auth(TEST_EMAIL), json={"question": "What is the capital of France?"})
    body = r.json()
    assert r.status_code == 200
    assert body["grounded"] is False and body["evidence"] == []


def test_emergency_question_gets_safety_notice():
    r = client.post("/ask", headers=auth(TEST_EMAIL), json={"question": "I have severe chest pain and cannot breathe"})
    assert r.status_code == 200
    assert r.json()["answer"].lstrip().startswith("⚠️")


def test_ask_rejects_empty_body():
    assert client.post("/ask", headers=auth(TEST_EMAIL), json={}).status_code == 422


def test_image_endpoint_rejects_non_image():
    r = client.post("/ask-image", headers=auth(TEST_EMAIL), files={"file": ("a.pdf", b"x", "application/pdf")})
    assert r.status_code == 400


# ---------- Chat history, bookmarks, feedback, exports ----------

def test_chat_flow_history_bookmark_feedback_export_delete():
    h = auth(TEST_EMAIL)
    q = "What is hypertension?"
    r = client.post("/ask", headers=h, json={"question": q})
    assert r.status_code == 200
    mid = r.json()["message_id"]

    history = client.get("/history", headers=h).json()["history"]
    assert any(m["question"] == q for m in history)

    assert client.patch(f"/history/{mid}/feedback", headers=h, json={"feedback": "like"}).json()["updated"] is True
    assert client.patch(f"/history/{mid}/bookmark", headers=h).json()["bookmarked"] is True
    assert client.get("/bookmarks", headers=h).status_code == 200

    pdf = client.get(f"/export/{mid}/pdf", headers=h)
    assert pdf.status_code == 200 and "pdf" in pdf.headers["content-type"]
    docx = client.get(f"/export/{mid}/docx", headers=h)
    assert docx.status_code == 200 and "wordprocessingml" in docx.headers["content-type"]
    assert client.get(f"/export/{mid}/pdf").status_code in (401, 403)

    assert client.delete(f"/history/{mid}", headers=h).json()["deleted"] is True
    history = client.get("/history", headers=h).json()["history"]
    assert not any(m["question"] == q for m in history)