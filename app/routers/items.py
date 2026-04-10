from fastapi import APIRouter, Depends, Security
from app.core.security import get_current_user, require_role
from app.models import User
from app.core.logger import logger

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/",
    summary="Получить список предметов",
    description="Доступно только с scope 'read:items'.",
    responses={
        200: {"description": "Список предметов"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав (нет scope read:items)"}
    }
)
async def read_items(current_user: User = Security(get_current_user, scopes=["read:items"])):
    logger.info(f"Пользователь {current_user.email} запросил список предметов")
    return [{"item": "example_item", "user": current_user.email}]


@router.delete(
    "/{item_id}",
    summary="Удалить предмет",
    description="Только для администраторов.",
    responses={
        200: {"description": "Предмет удалён"},
        401: {"description": "Не авторизован"},
        403: {"description": "Требуется роль admin"}
    }
)
async def delete_item(item_id: int, current_user: User = Depends(require_role("admin"))):
    return {"message": f"Item {item_id} deleted by admin {current_user.email}"}