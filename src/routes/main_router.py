from fastapi import APIRouter

from src.models import platillos
from . import menu_diario, platillos

router = APIRouter()

@router.get("/")
async def health():
    return "OK"

router.include_router(menu_diario.router, prefix="/menu")
router.include_router(platillos.router, prefix="/platillos")
