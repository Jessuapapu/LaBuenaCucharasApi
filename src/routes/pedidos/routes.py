from typing import Optional
from src.schemas.pedidos import PedidosIn
from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service
import datetime

router = APIRouter()


@router.get("/")
async def obtener_pedidos(
    estado: Optional[str] = Query(default=None),
    dia: Optional[datetime.date] = Query(default=None),
):
    pedidos = service.listar_historial_pedidos(estado, dia)

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
        raise HTTPException(500, {"message": "No se pudo crear el pedido"})

    return {
        "message": "Pedido creada exitosamente",
    }


@router.put("/pagar/{id_pedido}")
async def pagar_pedido(id_pedido: int):
    resultado = service.pagar_pedido_service(id_pedido)

    if resultado is None or resultado is not True:
        raise HTTPException(500, {"message": "No se pudo pagar el pedido"})

    return {"message": "El pedido se ha pagado exitosamente"}


@router.put("/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int):
    resultado = service.anular_pedido_service(id_pedido)

    if resultado is None or resultado is not True:
        raise HTTPException(500, {"message": "No se pudo cancelado el pedido"})

    return {"message": "El pedido se ha cancelado exitosamente"}
