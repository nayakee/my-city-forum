from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/web", tags=["Фронтенд"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/auth")
async def get_registration_html(request: Request):
    return templates.TemplateResponse(name="auth.html", context={"request": request})


@router.get("/")
async def get_index_html(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})