from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service as ordenes
from src.services.comedor import service as comedor
import datetime
from src.schemas.ComedorPedidos import OrdenComedorIN

router = APIRouter()


@router.get('/')
async def obtener_estado_comedor():
    return comedor.obtener_estado_total()

@router.get('/mesa/{Id}/{Estado}')
async def obtener_estado_comedor(Id: int, Estado: bool):
    if not Id:
        return HTTPException(400,"falta el id de mesa")
    
    if Estado:
        return comedor.obtener_estado_activas(IdMesa=Id)
    else:
        return comedor.obtener_estado_terminadas(IdMesa=Id)

@router.put("/{IdMesa}/{IdOrden}")
async def guardar_orden_mesa(IdMesa:int, IdOrden: int):
    if IdMesa not in comedor.obtener_IdMesas():
        return HTTPException(404, 'MESA NO ENCONTRADA')
    
    if not comedor.guardar_comedor_orden(IdMesa=IdMesa, IdOrden=IdOrden):
        return HTTPException(500, 'ERROR AL GUARDAR ORDEN')

@router.post("/{IdMesa}")
async def crear_orden_comedor(IdMesa:int, payload: OrdenComedorIN):
    if not comedor.generar_orden_comedor(IdMesa=IdMesa,detalles=payload.Detalles):
        return False