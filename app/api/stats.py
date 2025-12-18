from fastapi import APIRouter, Depends
from app.database.db_manager import DBManager
from app.services.stats import StatsService
from app.api.dependencies import get_db

router = APIRouter(prefix="/stats", tags=["Статистика"])

@router.get("", summary="Общая статистика")
async def get_stats(db: DBManager = Depends(get_db)):
    stats_service = StatsService(db)
    stats = await stats_service.get_forum_stats()
    return stats