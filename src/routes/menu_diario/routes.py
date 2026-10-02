import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from src.schemas.menus import *
from src.services.menu_diario import service
from typing import Optional
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
from src.models.platillos.types import *

router = APIRouter(tags=["Menus"])

@router.get("/")
async def obtener_menu(day: Optional[datetime.date] = Query(default=None)):
    if day is not None:
        menu = service.obtener_menu_dia_service(day)
        return menu

    menus = service.obtener_historial_menu_service()
    return menus


@router.get("/hoy")
async def obtener_menu_hoy():    
    menu = service.obtener_menu_dia_hoy()
    return menu



@router.post("/")
async def crear_menu(payload: MenuIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        print(payload.hora)
        service.crear_menu_service(
            day=payload.day, nombre_platillo=payload.nombre_platillo, hora=payload.hora, monto=payload.monto, username=usuario_actual.username
        )
        return {"detail": "Menu creado con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.put("/{id_menu}")
async def editar_menu(id_menu: int, payload: MenuUpdate, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        service.editar_menu_service(
            id_menu=id_menu, nombre_platillo=payload.nombre_platillo, username=usuario_actual.username
        )
        return {"detail": "Menu editado con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.get('/horarios')
async def obtener_horarios_menu(Nombre: str = Query(default=None)):
    if not Nombre:
        return service.obtener_cambios_de_hora()
    
    return service.obtener_cambio_de_hora(Nombre)

@router.post('/horarios')
async def crear_horarios_menu(payload: CambioDeHoraModel):
    return service.nuevo_cambio_de_hora(payload.nombre, payload.HoraInicio, payload.HoraFinal)

@router.put('/horarios/si')
async def editar_horarios_menu(payload: CambioDeHoraModelEditar):
    return service.editar_cambio_de_hora(payload.nombre,payload.nombreNuevo, payload.HoraInicio, payload.HoraFinal)

@router.delete('/horarios/{Nombre}')
async def borrar_horarios_menu(Nombre: str):
    return service.eliminar_cambio_de_hora(Nombre)