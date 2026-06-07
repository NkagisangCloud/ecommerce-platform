from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime

app = FastAPI(title="Orders Service")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total: float
    status: str
    created_at: str


_orders: dict = {}
_counter = 0


@app.get("/health")
def health():
    return {"status": "healthy", "service": "orders"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate):
    global _counter
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")
    _counter += 1
    total = sum(item.quantity * item.price for item in order.items)
    _orders[_counter] = {
        "id": _counter,
        "user_id": order.user_id,
        "items": [i.model_dump() for i in order.items],
        "total": round(total, 2),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    return _orders[_counter]


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return _orders[order_id]


@app.get("/orders/user/{user_id}")
def get_user_orders(user_id: int):
    return [o for o in _orders.values() if o["user_id"] == user_id]


@app.patch("/orders/{order_id}/status")
def update_status(order_id: int, status: str):
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="Order not found")
    valid = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    _orders[order_id]["status"] = status
    return _orders[order_id]
