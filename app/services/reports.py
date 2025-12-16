from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_

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
    def __init__(self, db):
        self.db = db  # DBManager instance

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
        existing_reports = await self.db.reports.get_filtered(
            filter_by={
                'reporter_id': reporter_id,
                'content_type': ReportContentTypeEnum(report_data.content_type.value),
                'content_id': report_data.content_id
            }
        )
        if existing_reports:
            raise DuplicateReportError
        
        # Создаем жалобу
        report_data_dict = {
            'reporter_id': reporter_id,
            'content_type': ReportContentTypeEnum(report_data.content_type.value),
            'content_id': report_data.content_id,
            'reason': report_data.reason,
            'description': report_data.description,
            'status': ReportStatusEnum.PENDING,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        new_report = await self.db.reports.add(report_data_dict)
        return new_report

    async def get_report(self, report_id: int) -> Optional[ReportModel]:
        """Получение жалобы по ID"""
        return await self.db.reports.get(report_id)

    async def get_report_with_details(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Получение жалобы с детальной информацией"""
        report = await self.db.reports.get(report_id)
        if not report:
            return None
        
        # Получаем информацию о репортере
        reporter = await self.db.users.get(report.reporter_id)
        
        # Получаем информацию о модераторе (если есть)
        moderator = None
        if report.moderator_id:
            moderator = await self.db.users.get(report.moderator_id)
        
        # Получаем информацию о контенте
        content_info = await self._get_content_info(report.content_type, report.content_id)
        
        # Формируем результат
        result_dict = {
            "id": report.id,
            "reporter_id": report.reporter_id,
            "reporter_name": reporter.name if reporter else None,
            "content_type": report.content_type.value,
            "content_id": report.content_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status.value,
            "moderator_id": report.moderator_id,
            "moderator_name": moderator.name if moderator else None,
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
        filters = {}
        if status:
            filters['status'] = ReportStatusEnum(status.value)
        if content_type:
            filters['content_type'] = ReportContentTypeEnum(content_type.value)
        if reporter_id:
            filters['reporter_id'] = reporter_id
            
        return await self.db.reports.get_filtered(
            **filters,
            offset=skip,
            limit=limit
        )

    async def get_reports_with_details(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ReportStatus] = None
    ) -> List[Dict[str, Any]]:
        """Получение жалоб с дополнительной информацией"""
        filters = {}
        if status:
            filters['status'] = ReportStatusEnum(status.value)
            
        reports = await self.db.reports.get_filtered(
            **filters,
            offset=skip,
            limit=limit
        )
        
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
        
        # Подготовим данные для обновления
        update_values = {
            "updated_at": datetime.utcnow(),
            "moderator_id": moderator_id
        }
        
        if report_data.status:
            update_values["status"] = ReportStatusEnum(report_data.status.value)
        
        if report_data.moderator_comment:
            update_values["moderator_comment"] = report_data.moderator_comment
        
        await self.db.reports.edit(update_values, id=report_id)

    async def delete_report(self, report_id: int, user_id: int, is_admin: bool = False) -> None:
        """Удаление жалобы (только автор или админ)"""
        report = await self.get_report(report_id)
        if not report:
            raise ReportNotFoundError
        
        # Проверка прав доступа
        if not is_admin and report.reporter_id != user_id:
            raise ReportAccessDeniedError
        
        await self.db.reports.delete(id=report_id)

    async def _check_content_exists(self, content_type: ContentType, content_id: int) -> bool:
        """Проверка существования контента"""
        if content_type == ContentType.POST:
            post = await self.db.posts.get(content_id)
            return post is not None
        else:  # COMMENT
            comment = await self.db.comments.get(content_id)
            return comment is not None

    async def _get_content_info(self, content_type: ReportContentTypeEnum, content_id: int) -> Dict[str, Any]:
        """Получение информации о контенте"""
        if content_type == ReportContentTypeEnum.POST:
            post = await self.db.posts.get(content_id)
            if post:
                author = await self.db.users.get(post.user_id)
                return {
                    "content_preview": post.header[:100] if post.header else "",
                    "content_body": post.body[:200] if post.body else "",
                    "content_author_id": post.user_id,
                    "content_author_name": author.name if author else "Unknown"
                }
        else:  # COMMENT
            comment = await self.db.comments.get(content_id)
            if comment:
                author = await self.db.users.get(comment.user_id)
                return {
                    "content_preview": comment.body[:100] if comment.body else "",
                    "content_body": comment.body[:200] if comment.body else "",
                    "content_author_id": comment.user_id,
                    "content_author_name": author.name if author else "Unknown"
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
        reporter = await self.db.users.get(report.reporter_id)
        
        # Получаем информацию о модераторе
        moderator = None
        if report.moderator_id:
            moderator = await self.db.users.get(report.moderator_id)
        
        # Получаем информацию о контенте
        content_info = await self._get_content_info(report.content_type, report.content_id)
        
        return {
            "id": report.id,
            "reporter_id": report.reporter_id,
            "reporter_name": reporter.name if reporter else None,
            "content_type": report.content_type.value,
            "content_id": report.content_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status.value,
            "moderator_id": report.moderator_id,
            "moderator_name": moderator.name if moderator else None,
            "moderator_comment": report.moderator_comment,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
            **content_info
        }

    async def get_report_stats(self) -> Dict[str, Any]:
        """Получение статистики по жалобам"""
        # Получаем все отчеты для подсчета статистики
        all_reports = await self.db.reports.get_all()
        total = len(all_reports)
        
        # Подсчитываем по статусам
        pending = len([r for r in all_reports if r.status == ReportStatusEnum.PENDING])
        resolved = len([r for r in all_reports if r.status == ReportStatusEnum.RESOLVED])
        rejected = len([r for r in all_reports if r.status == ReportStatusEnum.REJECTED])
        
        # Подсчитываем по типам контента
        posts_count = len([r for r in all_reports if r.content_type == ReportContentTypeEnum.POST])
        comments_count = len([r for r in all_reports if r.content_type == ReportContentTypeEnum.COMMENT])
        
        return {
            "total_reports": total,
            "pending_reports": pending,
            "resolved_reports": resolved,
            "rejected_reports": rejected,
            "reports_on_posts": posts_count,
            "reports_on_comments": comments_count
        }