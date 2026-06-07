from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Users Service")

# In a real deployment these come from environment variables
# injected by Kubernetes via External Secrets Operator
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


# In-memory store for now — replaced by Postgres in Phase 4
_users: dict = {}
_counter = 0


@app.get("/health")
def health():
    """Health check endpoint — Kubernetes liveness probe hits this."""
    return {"status": "healthy", "service": "users"}


@app.get("/ready")
def ready():
    """Readiness probe — tells Kubernetes the pod can receive traffic."""
    return {"status": "ready"}


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    global _counter
    for u in _users.values():
        if u["email"] == user.email:
            raise HTTPException(status_code=409, detail="Email already registered")
    _counter += 1
    _users[_counter] = {
        "id": _counter,
        "username": user.username,
        "email": user.email,
    }
    return _users[_counter]


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    return _users[user_id]


@app.get("/users")
def list_users():
    return list(_users.values())
