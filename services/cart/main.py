from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Cart Service")

# In Phase 4 this connects to ElastiCache Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class CartResponse(BaseModel):
    user_id: int
    items: List[CartItem]
    total: float


# In-memory store — replaced by Redis in Phase 4
_carts: dict = {}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "cart"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/cart/{user_id}", response_model=CartResponse)
def get_cart(user_id: int):
    items = _carts.get(user_id, [])
    total = round(sum(i["quantity"] * i["price"] for i in items), 2)
    return {"user_id": user_id, "items": items, "total": total}


@app.post("/cart/{user_id}/items", response_model=CartResponse, status_code=201)
def add_item(user_id: int, item: CartItem):
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    if user_id not in _carts:
        _carts[user_id] = []
    # Update quantity if product already in cart
    for existing in _carts[user_id]:
        if existing["product_id"] == item.product_id:
            existing["quantity"] += item.quantity
            total = round(sum(i["quantity"] * i["price"] for i in _carts[user_id]), 2)
            return {"user_id": user_id, "items": _carts[user_id], "total": total}
    _carts[user_id].append(item.model_dump())
    total = round(sum(i["quantity"] * i["price"] for i in _carts[user_id]), 2)
    return {"user_id": user_id, "items": _carts[user_id], "total": total}


@app.delete("/cart/{user_id}", status_code=204)
def clear_cart(user_id: int):
    _carts.pop(user_id, None)


@app.delete("/cart/{user_id}/items/{product_id}", status_code=204)
def remove_item(user_id: int, product_id: int):
    if user_id not in _carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    _carts[user_id] = [i for i in _carts[user_id] if i["product_id"] != product_id]
