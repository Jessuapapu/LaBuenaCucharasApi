import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from src.services.menu_diario import service
from typing import Optional

router = APIRouter()

class MenuIn(BaseModel):
    day: datetime.date
    nombre_platillo: str
    monto: float


class MenuUpdate(BaseModel):
    nombre_platillo: str


@router.get("/")
async def obtener_menu(day: Optional[datetime.date] = Query(default=None)):
    if day is not None:
        menu = service.obtener_menu_dia_service(day)
        return menu

    menus = service.obtener_historial_menu_service()
    return menus


@router.get("/hoy")
async def obtener_menu_hoy():    
    menu = service.obtener_menu_dia_service(datetime.datetime.now().date())
    return menu




@router.post("/")
async def crear_menu(payload: MenuIn):
    try:
        service.crear_menu_service(
            day=payload.day, nombre_platillo=payload.nombre_platillo, monto=payload.monto
        )
        return {"detail": "Menu creado con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.put("/{id_menu}")
async def editar_menu(id_menu: int, payload: MenuUpdate):
    try:
        service.editar_menu_service(
            id_menu=id_menu, nombre_platillo=payload.nombre_platillo
        )
        return {"detail": "Menu editado con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
