import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from src.services.menu_diario import service
from typing import Optional

router = APIRouter()

class MenuIn(BaseModel):
    day: datetime.date
    nombre_platillo: str


@router.get("/")
async def obtener_menu(day: Optional[datetime.date] = Query(default=None)):
    if day is not None:
        menu = service.obtener_menu_dia_service(day)
        return menu

    menus = service.obtener_historial_menu_service()
    return menus


@router.post("/")
async def crear_menu(payload: MenuIn):
    try:
        service.crear_menu_service(
            day=payload.day, nombre_platillo=payload.nombre_platillo
        )
        return {"detail": "Menu creado con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
