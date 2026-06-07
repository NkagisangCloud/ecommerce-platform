from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_empty_cart():
    r = client.get("/cart/1")
    assert r.status_code == 200
    assert r.json()["total"] == 0

def test_add_item():
    r = client.post("/cart/1/items", json={"product_id": 1, "quantity": 2, "price": 10.00})
    assert r.status_code == 201
    assert r.json()["total"] == 20.0

def test_invalid_quantity():
    assert client.post("/cart/1/items", json={"product_id": 1, "quantity": 0, "price": 10.00}).status_code == 400
