from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reports import ReportModel, ReportContentTypeEnum, ReportStatusEnum
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.users import UserModel
from app.schemes.reports import SReportCreate, SReportUpdate, ContentType, ReportStatus
from app.exceptions.reports import (
    ReportNotFoundError,
    ReportAccessDeniedError,
    ContentNotFoundError,
    DuplicateReportError,
    OnlyModeratorAccessError
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(self, report_data: SReportCreate, reporter_id: int) -> ReportModel:
        """Создание новой жалобы"""
        # Проверяем существование контента
        content_exists = await self._check_content_exists(
            report_data.content_type, 
            report_data.content_id
        )
        if not content_exists:
            raise ContentNotFoundError
        
        # Проверяем дубликаты
        duplicate_query = select(ReportModel).where(
            and_(
                ReportModel.reporter_id == reporter_id,
                ReportModel.content_type == ReportContentTypeEnum(report_data.content_type.value),
                ReportModel.content_id == report_data.content_id
            )
        )
        duplicate_result = await self.db.execute(duplicate_query)
        if duplicate_result.scalar_one_or_none():
            raise DuplicateReportError
        
        # Создаем жалобу
        new_report = ReportModel(
            reporter_id=reporter_id,
            content_type=ReportContentTypeEnum(report_data.content_type.value),
            content_id=report_data.content_id,
            reason=report_data.reason,
            description=report_data.description,
            status=ReportStatusEnum.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(new_report)
        await self.db.commit()
        await self.db.refresh(new_report)
        return new_report

    async def get_report(self, report_id: int) -> Optional[ReportModel]:
        """Получение жалобы по ID"""
        query = select(ReportModel).where(ReportModel.id == report_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_report_with_details(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Получение жалобы с детальной информацией"""
        query = select(ReportModel).where(ReportModel.id == report_id)
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Получаем информацию о репортере
        reporter_query = select(UserModel).where(UserModel.id == report.reporter_id)
        reporter_result = await self.db.execute(reporter_query)
        reporter = reporter_result.scalar_one_or_none()
        
        # Получаем информацию о модераторе (если есть)
        moderator = None
        if report.moderator_id:
            moderator_query = select(UserModel).where(UserModel.id == report.moderator_id)
            moderator_result = await self.db.execute(moderator_query)
            moderator = moderator_result.scalar_one_or_none()
        
        # Получаем информацию о контенте
        content_info = await self._get_content_info(report.content_type, report.content_id)
        
        # Формируем результат
        result_dict = {
            "id": report.id,
            "reporter_id": report.reporter_id,
            "reporter_name": reporter.username if reporter else None,
            "content_type": report.content_type.value,
            "content_id": report.content_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status.value,
            "moderator_id": report.moderator_id,
            "moderator_name": moderator.username if moderator else None,
            "moderator_comment": report.moderator_comment,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
            **content_info
        }
        
        return result_dict

    async def get_reports(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ReportStatus] = None,
        content_type: Optional[ContentType] = None,
        reporter_id: Optional[int] = None
    ) -> List[ReportModel]:
        """Получение списка жалоб с фильтрацией"""
        query = select(ReportModel)
        
        conditions = []
        if status:
            conditions.append(ReportModel.status == ReportStatusEnum(status.value))
        if content_type:
            conditions.append(ReportModel.content_type == ReportContentTypeEnum(content_type.value))
        if reporter_id:
            conditions.append(ReportModel.reporter_id == reporter_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit).order_by(ReportModel.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_reports_with_details(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ReportStatus] = None
    ) -> List[Dict[str, Any]]:
        """Получение жалоб с дополнительной информацией"""
        base_query = select(ReportModel)
        
        if status:
            base_query = base_query.where(ReportModel.status == ReportStatusEnum(status.value))
        
        base_query = base_query.offset(skip).limit(limit).order_by(ReportModel.created_at.desc())
        
        result = await self.db.execute(base_query)
        reports = result.scalars().all()
        
        detailed_reports = []
        for report in reports:
            # Получаем детальную информацию для каждой жалобы
            detailed_report = await self._get_detailed_report_info(report)
            detailed_reports.append(detailed_report)
        
        return detailed_reports

    async def update_report(
        self, 
        report_id: int, 
        report_data: SReportUpdate, 
        moderator_id: int
    ) -> None:
        """Обновление жалобы (только модераторы)"""
        report = await self.get_report(report_id)
        if not report:
            raise ReportNotFoundError
        
        # Обновляем жалобу
        update_values = {
            "updated_at": datetime.utcnow(),
            "moderator_id": moderator_id
        }
        
        if report_data.status:
            update_values["status"] = ReportStatusEnum(report_data.status.value)
        
        if report_data.moderator_comment:
            update_values["moderator_comment"] = report_data.moderator_comment
        
        query = (
            update(ReportModel)
            .where(ReportModel.id == report_id)
            .values(**update_values)
        )
        
        await self.db.execute(query)
        await self.db.commit()

    async def delete_report(self, report_id: int, user_id: int, is_admin: bool = False) -> None:
        """Удаление жалобы (только автор или админ)"""
        report = await self.get_report(report_id)
        if not report:
            raise ReportNotFoundError
        
        # Проверка прав доступа
        if not is_admin and report.reporter_id != user_id:
            raise ReportAccessDeniedError
        
        query = delete(ReportModel).where(ReportModel.id == report_id)
        await self.db.execute(query)
        await self.db.commit()

    async def _check_content_exists(self, content_type: ContentType, content_id: int) -> bool:
        """Проверка существования контента"""
        if content_type == ContentType.POST:
            query = select(PostModel).where(PostModel.id == content_id)
        else:  # COMMENT
            query = select(CommentModel).where(CommentModel.id == content_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _get_content_info(self, content_type: ReportContentTypeEnum, content_id: int) -> Dict[str, Any]:
        """Получение информации о контенте"""
        if content_type == ReportContentTypeEnum.POST:
            query = (
                select(PostModel, UserModel.username)
                .join(UserModel, PostModel.user_id == UserModel.id)
                .where(PostModel.id == content_id)
            )
            result = await self.db.execute(query)
            row = result.first()
            
            if row:
                post, author_name = row
                return {
                    "content_preview": post.header[:100] if post.header else "",
                    "content_body": post.body[:200] if post.body else "",
                    "content_author_id": post.user_id,
                    "content_author_name": author_name
                }
        else:  # COMMENT
            query = (
                select(CommentModel, UserModel.username)
                .join(UserModel, CommentModel.user_id == UserModel.id)
                .where(CommentModel.id == content_id)
            )
            result = await self.db.execute(query)
            row = result.first()
            
            if row:
                comment, author_name = row
                return {
                    "content_preview": comment.body[:100] if comment.body else "",
                    "content_body": comment.body[:200] if comment.body else "",
                    "content_author_id": comment.user_id,
                    "content_author_name": author_name
                }
        
        return {
            "content_preview": None,
            "content_body": None,
            "content_author_id": None,
            "content_author_name": None
        }

    async def _get_detailed_report_info(self, report: ReportModel) -> Dict[str, Any]:
        """Получение детальной информации о жалобе"""
        # Получаем информацию о репортере
        reporter_query = select(UserModel).where(UserModel.id == report.reporter_id)
        reporter_result = await self.db.execute(reporter_query)
        reporter = reporter_result.scalar_one_or_none()
        
        # Получаем информацию о модераторе
        moderator = None
        if report.moderator_id:
            moderator_query = select(UserModel).where(UserModel.id == report.moderator_id)
            moderator_result = await self.db.execute(moderator_query)
            moderator = moderator_result.scalar_one_or_none()
        
        # Получаем информацию о контенте
        content_info = await self._get_content_info(report.content_type, report.content_id)
        
        return {
            "id": report.id,
            "reporter_id": report.reporter_id,
            "reporter_name": reporter.username if reporter else None,
            "content_type": report.content_type.value,
            "content_id": report.content_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status.value,
            "moderator_id": report.moderator_id,
            "moderator_name": moderator.username if moderator else None,
            "moderator_comment": report.moderator_comment,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
            **content_info
        }

    async def get_report_stats(self) -> Dict[str, Any]:
        """Получение статистики по жалобам"""
        # Общее количество жалоб
        total_query = select(func.count(ReportModel.id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Жалобы по статусам
        pending_query = select(func.count(ReportModel.id)).where(
            ReportModel.status == ReportStatusEnum.PENDING
        )
        pending_result = await self.db.execute(pending_query)
        pending = pending_result.scalar() or 0
        
        resolved_query = select(func.count(ReportModel.id)).where(
            ReportModel.status == ReportStatusEnum.RESOLVED
        )
        resolved_result = await self.db.execute(resolved_query)
        resolved = resolved_result.scalar() or 0
        
        rejected_query = select(func.count(ReportModel.id)).where(
            ReportModel.status == ReportStatusEnum.REJECTED
        )
        rejected_result = await self.db.execute(rejected_query)
        rejected = rejected_result.scalar() or 0
        
        # Жалобы по типам контента
        posts_query = select(func.count(ReportModel.id)).where(
            ReportModel.content_type == ReportContentTypeEnum.POST
        )
        posts_result = await self.db.execute(posts_query)
        posts_count = posts_result.scalar() or 0
        
        comments_query = select(func.count(ReportModel.id)).where(
            ReportModel.content_type == ReportContentTypeEnum.COMMENT
        )
        comments_result = await self.db.execute(comments_query)
        comments_count = comments_result.scalar() or 0
        
        return {
            "total_reports": total,
            "pending_reports": pending,
            "resolved_reports": resolved,
            "rejected_reports": rejected,
            "reports_on_posts": posts_count,
            "reports_on_comments": comments_count
        }