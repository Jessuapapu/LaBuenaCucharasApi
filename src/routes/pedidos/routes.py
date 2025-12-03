from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.pedidos import service
import datetime

router = APIRouter()

class PedidosIn(BaseModel):
    nombre_cliente: str
    fecha: datetime.date

class PedidosOp(BaseModel):
    id: int


@router.get("/")
async def obtener_pedidos(filtro: str, dia: datetime.date):
    pass


@router.get("/detalle/{id}")
async def obtener_detalle(id: int):
    pass


@router.post("/")
async def crear_pedido(payload: PedidosIn):
    pedido = service.crear_pedido(payload.nombre_cliente, payload.fecha)

    if not pedido:
        raise HTTPException(500, {"message": "No se pudo crear el pedido"})

    return {
        "message": "Pedido creada exitosamente",
        "pedido": pedido
    }


@router.post("/pagar/{id}")
async def pagar_pedido(id: int):
    pass


@router.post("/cancelar/{id}")
async def cancelar_pedido(id: int):
    pass
