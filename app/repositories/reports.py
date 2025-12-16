from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.reports import ReportModel, ReportStatusEnum
from app.repositories.base import BaseRepository


class ReportsRepository(BaseRepository[ReportModel]):
    """Репозиторий для работы с жалобами"""
    
    def __init__(self, session: AsyncSession):
        self.model = ReportModel
        self.session = session

    async def get_by_status(
        self, 
        status: ReportStatusEnum,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReportModel]:
        """Получение жалоб по статусу"""
        query = (
            select(ReportModel)
            .where(ReportModel.status == status)
            .order_by(desc(ReportModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_reporter(
        self, 
        reporter_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReportModel]:
        """Получение жалоб репортера"""
        query = (
            select(ReportModel)
            .where(ReportModel.reporter_id == reporter_id)
            .order_by(desc(ReportModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_content(
        self, 
        content_type: str,
        content_id: int
    ) -> List[ReportModel]:
        """Получение жалоб на конкретный контент"""
        query = (
            select(ReportModel)
            .where(
                ReportModel.content_type == content_type,
                ReportModel.content_id == content_id
            )
            .order_by(desc(ReportModel.created_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_pending_reports(self) -> List[ReportModel]:
        """Получение всех жалоб в статусе 'pending'"""
        return await self.get_by_status(ReportStatusEnum.PENDING)