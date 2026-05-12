from typing import Optional
from src.schemas.pedidos import PedidosIn, PedidosUpdate
from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service
import datetime

router = APIRouter()


@router.get("/")
async def obtener_pedidos():
    pass


@router.get("/detalle/")
async def obtener_detalle():
    pass

@router.post("/")
async def crear_pedido(payload: PedidosIn):
    pass


@router.put("/detalles/{id_pedido}")
async def actualizar_detalles_pedido(id_pedido: int, payload: PedidosUpdate):
    pass


@router.get("/conteo/semanal")
async def obtener_conteo_Ordenes_semanal():
    pass
    return



@router.get("/platillos/conteo")
async def obtener_platillos_populares():
    pass
    return
