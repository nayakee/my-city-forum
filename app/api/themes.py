from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.database.db_manager import DBManager
from app.api.dependencies import get_db

from app.schemes.themes import SThemeGet, SThemeCreate, SThemeUpdate
from app.services.themes import ThemeService

router = APIRouter(prefix="/themes", tags=["Темы"])


@router.get("", summary="Получение списка тем")
async def get_themes(db: DBManager = Depends(get_db)) -> List[SThemeGet]:
    """
    Получить список всех тем с количеством постов в каждой теме
    """
    theme_service = ThemeService(db)
    themes = await theme_service.get_themes_with_post_counts()
    
    result = []
    for theme in themes:
        result.append(
            SThemeGet(
                id=theme['id'],
                name=theme['name'],
                posts_count=theme.get('posts_count', 0),
                created_at=theme.get('created_at'),
                updated_at=theme.get('updated_at')
            )
        )
    
    return result


@router.get("/{theme_id}", summary="Получение темы по ID")
async def get_theme(theme_id: int, db: DBManager = Depends(get_db)) -> SThemeGet:
    """
    Получить тему по ID
    """
    theme_service = ThemeService(db)
    theme = await theme_service.get_theme_with_post_count(theme_id)
    
    if not theme:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    return SThemeGet(
        id=theme['id'],
        name=theme['name'],
        posts_count=theme.get('posts_count', 0),
        created_at=theme.get('created_at'),
        updated_at=theme.get('updated_at')
    )


@router.post("", summary="Создание новой темы")
async def create_theme(theme_data: SThemeCreate, db: DBManager = Depends(get_db)) -> SThemeGet:
    """
    Создать новую тему
    """
    theme_service = ThemeService(db)
    theme = await theme_service.create_theme(theme_data)
    
    return SThemeGet(
        id=theme.id,
        name=theme.name,
        posts_count=0, # Новая тема не имеет постов
        created_at=theme.created_at,
        updated_at=theme.updated_at
    )


@router.put("/{theme_id}", summary="Обновление темы")
async def update_theme(theme_id: int, theme_data: SThemeUpdate, db: DBManager = Depends(get_db)) -> SThemeGet:
    """
    Обновить тему
    """
    theme_service = ThemeService(db)
    theme = await theme_service.update_theme(theme_id, theme_data)
    
    if not theme:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    # Обновляем количество постов в теме
    updated_theme = await theme_service.get_theme_with_post_count(theme_id)
    
    return SThemeGet(
        id=updated_theme['id'],
        name=updated_theme['name'],
        posts_count=updated_theme.get('posts_count', 0),
        created_at=updated_theme.get('created_at'),
        updated_at=updated_theme.get('updated_at')
    )


@router.delete("/{theme_id}", summary="Удаление темы")
async def delete_theme(theme_id: int, db: DBManager = Depends(get_db)) -> dict:
    """
    Удалить тему
    """
    theme_service = ThemeService(db)
    success = await theme_service.delete_theme(theme_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    return {"message": "Тема успешно удалена"}