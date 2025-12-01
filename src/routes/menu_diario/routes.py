import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.menu_diario.service import crear_menu_service

router = APIRouter()

class MenuIn(BaseModel):
    day: datetime.date
    nombre_platillo: str


@router.get("/")
async def obtener_menu(day: datetime.date):
    pass


@router.post("/")
async def crear_menu(payload: MenuIn):
    try:
        crear_menu_service(day=payload.day, nombre_platillo=payload.nombre_platillo)
        return "Menu creado con exito"
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.delete("/")
async def deshabilitar_menu(day: datetime.date):
    pass
