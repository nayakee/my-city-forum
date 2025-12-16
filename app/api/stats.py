from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["Статистика"])

@router.get("", summary="Общая статистика")
async def get_stats():
    # В реальном приложении здесь будет логика получения статистики из базы данных
    return {
        "total_posts": 0,
        "total_users": 0,
        "total_communities": 0,
        "total_themes": 0
    }