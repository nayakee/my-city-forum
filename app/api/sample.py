from fastapi import APIRouter

router = APIRouter(prefix="/sample",tags=["Sample"])

@router.get("/")
async def sample_func():
    return {"msg":"Пример ручки"}