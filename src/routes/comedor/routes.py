from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service as ordenes
from src.services.comedor import service as comedor
import datetime
from src.schemas.ComedorPedidos import OrdenComedorIN

router = APIRouter()

Estado = False

@router.put('/abrir')
async def abrir_comedor():
    if Estado:
        return {"msj":"Ya Comedor abierto","status": False}
    
    comedor.abrir_comedor()
    Estado = True

    return  {"msj":"Comedor abierto","status": True}

@router.put('/cerrar')
async def cerrar_comedor():
    if not Estado:
        return {"msj":"Comedor aun no abierto","status": False}
    
    comedor.cerrar_comedor()
    Estado = False

    return  {"msj":"Comedor cerrado", "status": True}

@router.get('/')
async def obtener_estado_comedor():
    return comedor.obtener_estado_total()

@router.get('/mesa/{Id}/{Estado}')
async def obtener_estado_comedor(Id: int, Estado: bool):
    if not Id:
        return HTTPException(400,"falta el id de mesa")
    
    mesa = None

    if Estado:
        mesa = comedor.obtener_estado_activas(IdMesa=Id)
    else:
        mesa = comedor.obtener_estado_terminadas(IdMesa=Id)

    return mesa if mesa else HTTPException(400,"mesa no encontrada")

@router.post("/{IdMesa}/{IdOrden}")
async def guardar_orden_mesa(IdMesa:int, IdOrden: int):
    if IdMesa not in comedor.obtener_IdMesas():
        return HTTPException(404, 'MESA NO ENCONTRADA')
    
    if not comedor.guardar_comedor_orden(IdMesa=IdMesa, IdOrden=IdOrden):
        return HTTPException(500, 'ERROR AL GUARDAR ORDEN')

@router.post("/{IdMesa}")
async def crear_orden_comedor(IdMesa:int, payload: OrdenComedorIN):
    if not comedor.generar_orden_comedor(IdMesa=IdMesa,detalles=payload.Detalles):
        return False
    
@router.get("/NumeroMesas")
async def obtener_numero_mesas():
    return comedor.obtener_IdMesas()

@router.post("/NumeroMesas/{numeroid}")
async def aumentar_mesas(numeroid: int):
    return 