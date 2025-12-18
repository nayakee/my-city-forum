import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Импортируем все модели для регистрации в Base до инициализации приложения
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.communities import CommunityModel
from app.models.user_communities import UserCommunityModel
from app.models.themes import ThemeModel
from app.models.reports import ReportModel
from app.models.favorites import FavoritePostModel

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.web import router as web_router
from app.api.communities import router as community_router
from app.api.comments import router as comment_router
from app.api.reports import router as report_router
from app.api.themes import router as theme_router
from app.api.simple_posts import router as simple_post_router
from app.api.favorites import router as favorites_router
from app.api.stats import router as stats_router

from app.exceptions.auth import JWTTokenExpiredHTTPError

app = FastAPI(title="Форум 'Мой Город'", version="0.0.1")

# Глобальный обработчик исключений для истекших токенов
@app.exception_handler(JWTTokenExpiredHTTPError)
async def handle_expired_token(request, exc: JWTTokenExpiredHTTPError):
    """Обработчик для истечения токена - возвращает специальный ответ для автоматического выхода"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "logout_required": True  # Индикатор, что требуется автоматический выход
        }
    )

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(web_router)
app.include_router(community_router)
app.include_router(comment_router)
app.include_router(report_router)
app.include_router(theme_router)
app.include_router(simple_post_router)
app.include_router(favorites_router)
app.include_router(stats_router)

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/web/")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

