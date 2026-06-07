from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_create_order():
    r = client.post("/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 2, "price": 9.99}]})
    assert r.status_code == 201
    assert r.json()["total"] == 19.98

def test_empty_order():
    assert client.post("/orders", json={"user_id": 1, "items": []}).status_code == 400

def test_order_not_found():
    assert client.get("/orders/9999").status_code == 404
