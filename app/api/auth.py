from fastapi import APIRouter
from app.utils.auth import create_access_token

router = APIRouter()

@router.post("/login")
def login(username: str):
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}