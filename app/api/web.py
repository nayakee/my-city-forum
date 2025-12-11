from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

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
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Страница авторизации
@router.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    print(f"Accessing auth.html from: {TEMPLATES_DIR / 'auth.html'}")  # Отладка
    return templates.TemplateResponse("auth.html", {"request": request})

# Страница сообществ
@router.get("/communities", response_class=HTMLResponse)
async def communities_page(request: Request):
    print(f"Accessing communities.html from: {TEMPLATES_DIR / 'communities.html'}")  # Отладка
    return templates.TemplateResponse("communities.html", {"request": request})