import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.web import router as web_router
from app.api.communities import router as community_router
from app.api.comments import router as comment_router
from app.api.posts import router as post_pouter
from app.api.reports import router as report_router

app = FastAPI(title="Форум 'Мой Город'", version="0.0.1")

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(web_router)
app.include_router(community_router)
app.include_router(comment_router)
app.include_router(post_pouter)
app.include_router(report_router)

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/web/")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

