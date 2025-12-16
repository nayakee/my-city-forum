from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status

from app.api.dependencies import DBDep, UserDepWithRole
from app.exceptions.reports import (
    ReportNotFoundError,
    ReportNotFoundHTTPError,
    ReportAccessDeniedError,
    ReportAccessDeniedHTTPError,
    ContentNotFoundError,
    ContentNotFoundHTTPError,
    DuplicateReportError,
    DuplicateReportHTTPError,
    OnlyModeratorAccessError
)
from app.schemes.reports import (
    SReportCreate, 
    SReportUpdate, 
    SReportGet,
    SReportStats,
    ReportStatus
)
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["Жалобы"])


@router.post("", summary="Создание новой жалобы")
async def create_report(
    report_data: SReportCreate,
    db: DBDep,
    current_user = Depends(UserDepWithRole),
) -> dict[str, str]:
    try:
        await ReportService(db).create_report(report_data, current_user.id)
    except ContentNotFoundError:
        raise ContentNotFoundHTTPError
    except DuplicateReportError:
        raise DuplicateReportHTTPError
    
    return {"status": "OK", "message": "Жалоба успешно отправлена"}


@router.get("/my", summary="Получение жалоб текущего пользователя")
async def get_my_reports(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ReportStatus] = None,
    current_user = Depends(UserDepWithRole),
) -> List[SReportGet]:
    reports = await ReportService(db).get_reports_with_details(
        skip=skip,
        limit=limit,
        status=status
    )
    # Фильтруем только жалобы текущего пользователя
    my_reports = [r for r in reports if r["reporter_id"] == current_user.id]
    return my_reports


@router.get("", summary="Получение всех жалоб (только для модераторов)")
async def get_all_reports(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ReportStatus] = None,
    content_type: Optional[str] = Query(None, regex="^(post|comment)$"),
    current_user = Depends(UserDepWithRole),
) -> List[SReportGet]:
    # Проверяем права доступа (только модераторы/админы)
    is_moderator = current_user.role.level >= 2  # Модератор или выше
    if not is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут просматривать все жалобы"
        )
    
    reports = await ReportService(db).get_reports_with_details(
        skip=skip,
        limit=limit,
        status=status
    )
    return reports


@router.get("/{report_id}", summary="Получение конкретной жалобы")
async def get_report(
    db: DBDep,
    report_id: int = Path(..., description="ID жалобы"),
    current_user = Depends(UserDepWithRole),
) -> SReportGet:
    report = await ReportService(db).get_report_with_details(report_id)
    if not report:
        raise ReportNotFoundHTTPError
    
    # Проверяем права доступа
    is_moderator = getattr(current_user, "is_moderator", False) or getattr(current_user, "is_admin", False)
    if not is_moderator and report["reporter_id"] != current_user.id:
        raise ReportAccessDeniedHTTPError
    
    return report


@router.put("/{report_id}", summary="Обновление жалобы (только модераторы)")
async def update_report(
    report_data: SReportUpdate,
    db: DBDep,
    report_id: int = Path(..., description="ID жалобы"),
    current_user = Depends(UserDepWithRole),
) -> dict[str, str]:
    # Проверяем права доступа
    is_moderator = current_user.role.level >= 2  # Модератор или выше
    if not is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут обновлять жалобы"
        )
    
    try:
        await ReportService(db).update_report(report_id, report_data, current_user.id)
    except ReportNotFoundError:
        raise ReportNotFoundHTTPError
    
    return {"status": "OK", "message": "Жалоба успешно обновлена"}


@router.delete("/{report_id}", summary="Удаление жалобы")
async def delete_report(
    db: DBDep,
    report_id: int = Path(..., description="ID жалобы"),
    current_user = Depends(UserDepWithRole),
) -> dict[str, str]:
    try:
        is_admin = current_user.role.level >= 3  # Администратор
        await ReportService(db).delete_report(report_id, current_user.id, is_admin)
    except ReportNotFoundError:
        raise ReportNotFoundHTTPError
    except ReportAccessDeniedError:
        raise ReportAccessDeniedHTTPError
    
    return {"status": "OK", "message": "Жалоба успешно удалена"}


@router.get("/stats/summary", summary="Статистика жалоб (только модераторы)")
async def get_reports_stats(
    db: DBDep,
    current_user = Depends(UserDepWithRole),
) -> SReportStats:
    # Проверяем права доступа
    is_moderator = current_user.role.level >= 2  # Модератор или выше
    if not is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут просматривать статистику"
        )
    
    stats = await ReportService(db).get_report_stats()
    return stats


@router.get("/content/{content_type}/{content_id}", summary="Получение жалоб на конкретный контент")
async def get_reports_for_content(
    db: DBDep,
    content_type: str = Path(..., description="Тип контента (post или comment)", regex="^(post|comment)$"),
    content_id: int = Path(..., description="ID контента"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(UserDepWithRole),
) -> List[SReportGet]:
    # Проверяем права доступа (только модераторы/админы или автор контента)
    is_moderator = current_user.role.level >= 2  # Модератор или выше
    
    # TODO: Здесь нужно добавить проверку, является ли пользователь автором контента
    
    if not is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут просматривать жалобы на контент"
        )
    
    # Получаем жалобы для конкретного контента
    from app.schemes.reports import ContentType
    
    reports = await ReportService(db).get_reports(
        skip=skip,
        limit=limit,
        content_type=ContentType(content_type)
    )
    
    # Фильтруем по content_id
    filtered_reports = [r for r in reports if r.content_id == content_id]
    
    # Получаем детальную информацию для каждой жалобы
    detailed_reports = []
    for report in filtered_reports:
        detailed_report = await ReportService(db)._get_detailed_report_info(report)
        detailed_reports.append(detailed_report)
    
    return detailed_reports