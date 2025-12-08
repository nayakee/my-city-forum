import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router

app = FastAPI(title="Форум 'Мой Город'", version="0.0.1")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)

app.mount("/static", StaticFiles(directory="app/static"), "static")

# Настраиваем шаблоны из app/templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Страница авторизации
@app.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# Редирект с /web на главную
@app.get("/web")
async def web_redirect():
    return RedirectResponse(url="/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
