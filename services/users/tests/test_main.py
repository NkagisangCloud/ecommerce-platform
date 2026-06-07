from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_create_user():
    r = client.post("/users", json={"username": "nkagisang", "email": "n@test.com", "password": "pass"})
    assert r.status_code == 201

def test_duplicate_email():
    client.post("/users", json={"username": "a", "email": "dup@test.com", "password": "p"})
    r = client.post("/users", json={"username": "b", "email": "dup@test.com", "password": "p"})
    assert r.status_code == 409

def test_user_not_found():
    assert client.get("/users/9999").status_code == 404
