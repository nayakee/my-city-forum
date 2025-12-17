from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from app.api.dependencies import DBDep, get_current_user_id, get_db
from app.services.auth import AuthService
from app.api.dependencies import DBDep
from app.services.posts import PostService
from app.database.db_manager import DBManager
from app.exceptions.auth import JWTTokenExpiredHTTPError

router = APIRouter(prefix="/web", tags=["Фронтенд"])

# Определяем путь к шаблонам
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # app/api/web.py → 3 уровня вверх
TEMPLATES_DIR = project_root / "app" / "templates"

# Для отладки
print(f"=== DEBUG INFO ===")
print(f"Templates directory: {TEMPLATES_DIR}")
print(f"Directory exists: {TEMPLATES_DIR.exists()}")
if TEMPLATES_DIR.exists():
    print(f"Files in templates: {list(TEMPLATES_DIR.glob('*.html'))}")
print(f"==================")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Главная страница
@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: 'DBDep' = None, theme_id: int = None):
    async with DBManager() as db_manager:
        # Получаем посты из базы данных с дополнительной информацией для веб-страницы
        posts = await PostService(db_manager).get_posts_for_web(theme_id=theme_id, limit=10) # Получаем последние 10 постов

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

# Страница отдельного поста с комментариями
@router.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: int, db: 'DBDep' = None):
    async with DBManager() as db_manager:
        # Получаем пост с комментариями по ID
        post = await PostService(db_manager).get_post_with_comments(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        return templates.TemplateResponse("post_detail.html", {
            "request": request,
            "post": post,
            "comments": post.get("comments", [])
        })

# Страница авторизации
@router.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    print(f"Accessing auth.html from: {TEMPLATES_DIR / 'auth.html'}")  # Отладка
    return templates.TemplateResponse("auth.html", {"request": request})

# Страница сообществ
@router.get("/communities", response_class=HTMLResponse)
async def communities_page(request: Request, db: 'DBDep' = None):
    from app.services.communities import CommunitiesService
    from app.database.db_manager import DBManager
    
    async with DBManager() as db_manager:
        # Получаем сообщества из базы данных
        communities = await CommunitiesService(db_manager).get_communities()
    
    print(f"Accessing communities.html from: {TEMPLATES_DIR / 'communities.html'}")  # Отладка
    return templates.TemplateResponse("communities.html", {
        "request": request,
        "communities": communities
    })


# Страница отдельного сообщества
@router.get("/communities/{community_id}", response_class=HTMLResponse)
async def community_detail_page(request: Request, community_id: int, db: 'DBDep' = None):
    from app.services.communities import CommunitiesService
    from app.database.db_manager import DBManager
    from app.services.posts import PostService
    
    async with DBManager() as db_manager:
        # Получаем информацию о сообществе
        community = await CommunitiesService(db_manager).get_community(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Сообщество не найдено")
        
        # Получаем посты, связанные с этим сообществом
        posts = await PostService(db_manager).get_posts_for_web(community_id=community_id, limit=20)
    
    return templates.TemplateResponse("community_detail.html", {
        "request": request,
        "community": community,
        "posts": posts
    })
    
    
# Страница профиля пользователя
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: DBManager = Depends(get_db)
):
    try:
        # Получаем полные данные пользователя с ролями
        user_data = await AuthService(db).get_me(user_id)
        
        # Здесь можно получить дополнительную статистику пользователя
        # Подсчет постов пользователя
        user_posts = await db.posts.get_filtered(user_id=user_id)
        user_posts_count = len(user_posts)
        # Подсчет комментариев пользователя
        user_comments = await db.comments.get_filtered(user_id=user_id)
        user_comments_count = len(user_comments)
        # Подсчет лайков, полученных пользователем за его посты
        user_likes_count = sum(post.likes or 0 for post in user_posts)
        
        # Получаем посты пользователя с дополнительной информацией
        user_posts_detailed = await PostService(db).get_posts_for_web(user_id=user_id)
        
        user_stats = {
            "posts_count": user_posts_count,
            "comments_count": user_comments_count,
            "likes_received": user_likes_count,
            "joined_date": user_data.created_at.strftime('%d.%m.%Y') if hasattr(user_data, 'created_at') and user_data.created_at else 'Неизвестно'
        }
        
        # Create a serializable version of user_data with properly formatted communities
        user_data_dict = user_data.model_dump() if hasattr(user_data, 'model_dump') else user_data.dict()
        
        # Ensure communities are properly serialized
        if hasattr(user_data, 'communities') and user_data.communities is not None:
            serialized_communities = []
            for community in user_data.communities:
                if hasattr(community, 'model_dump'):
                    serialized_communities.append(community.model_dump())
                elif hasattr(community, 'dict'):
                    serialized_communities.append(community.dict())
                else:
                    # If it's already a dict or basic type, use it as is
                    serialized_communities.append(community)
            user_data_dict['communities'] = serialized_communities
        else:
            user_data_dict['communities'] = []
        
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user_data_dict,
            "stats": user_stats,
            "user_posts": user_posts_detailed
        })
    except JWTTokenExpiredHTTPError:
        # Перенаправляем на страницу авторизации при истечении токена
        return RedirectResponse(url="/web/auth")