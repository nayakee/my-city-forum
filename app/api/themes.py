from fastapi import APIRouter
from typing import List

from app.schemes.themes import SThemeGet

router = APIRouter(prefix="/themes", tags=["Темы"])


@router.get("", summary="Получение списка тем")
async def get_themes() -> List[SThemeGet]:
    """
    Получить список всех тем с количеством постов в каждой теме
    """
    # Временно возвращаем фиксированные темы, пока не решена проблема с ORM
    themes_data = [
        {"id": 1, "name": "Новости", "posts_count": 0, "created_at": None, "updated_at": None},
        {"id": 2, "name": "Недвижимость", "posts_count": 0, "created_at": None, "updated_at": None},
        {"id": 3, "name": "Работа", "posts_count": 0, "created_at": None, "updated_at": None}
    ]
    
    result = []
    for theme_data in themes_data:
        result.append(SThemeGet(**theme_data))
    
    return result