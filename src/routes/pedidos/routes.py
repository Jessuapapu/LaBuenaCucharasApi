from typing import Optional
from src.schemas.pedidos import PedidosIn, PedidosUpdate
from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service
import datetime

router = APIRouter()


@router.get("/")
async def obtener_pedidos():
    pedidos = service.listar_historial_pedidos()

    return pedidos


@router.get("/detalle/{id}")
async def obtener_detalle(id: int):
    pass


@router.post("/")
async def crear_pedido(payload: PedidosIn):
    pedido = service.crear_pedido(
        payload.nombre_cliente, payload.fecha, payload.detalle
    )

    if not pedido:
        raise HTTPException(500, "No se pudo crear el pedido")

    return {
        "message": "Pedido creada exitosamente",
    }


@router.put("/detalles/{id_pedido}")
async def actualizar_detalles_pedido(id_pedido: int, payload: PedidosUpdate):
    resultado = service.actualizar_pedido(
        id_pedido, payload.nombre_cliente, payload.estado, payload.detalles
    )

    if resultado is None or not resultado:
        raise HTTPException(500, "No se pudo actualizar el pedido")

    return {"detail": "El pedido se actualizo correctamente"}


@router.get("/conteo/semanal")
async def obtener_conteo_pedidos_semanal():
    conteo = service.conteo_pedidos_semanal()
    return conteo


@router.get("/facturas")
async def obtener_facturas():
    facturas = service.obtener_facturas_pedidos()
    return facturas
