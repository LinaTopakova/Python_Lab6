from fastapi import APIRouter, Security
from app.core.security import get_current_user
from app.models import User

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
async def read_items(
    current_user: User = Security(get_current_user, scopes=["read:items"])
):
    return [
        {"item": "example_item", "user": current_user.email}
    ]