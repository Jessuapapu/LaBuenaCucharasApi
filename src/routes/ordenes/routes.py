from typing import Optional
from src.schemas.pedidos import PedidosIn, PedidosUpdate
from fastapi import APIRouter, HTTPException, Query, Depends
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
from src.services.ordenes import service
import datetime

router = APIRouter()


@router.get("/")
async def obtener_ordenes(
    pagina: int = Query(1, description="Número de página"), 
    rows: int = Query(10, description="Filas por página"), 
    todo: bool = Query(False, description="Traer todo sin paginar"),
    nombeCliente: str = Query(None, description="Nombre del Cliente"),
):
    pedidos = service.listar_historial_Ordenes(pagina=pagina, rows=rows, todo=todo)
    return pedidos


@router.get("/detalle/")
async def obtener_detalle(
    IdPedido: int | None = Query(None, description="Id de Pedido"),
    IdCliente: int | None  = Query(None, description="Id de Cliente")
    ):

    detalle = service.detalle_Ordenes(id_orden = IdPedido, id_cliente = IdCliente)     
    return detalle

@router.post("/")
async def crear_ordenes(payload: PedidosIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    pedido = service.crear_orden(
        payload.fecha, payload.detalle, nombre_cliente=payload.nombre_cliente, username=usuario_actual.username
    )

    if not pedido:
        raise HTTPException(500, "No se pudo crear el pedido")

    return {
        "message": "Pedido creada exitosamente",
    }


@router.put("/detalles/{id_orden}")
async def actualizar_detalles_ordenes(id_orden: int, payload: PedidosUpdate, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    resultado = service.actualizar_ordenes(
        id_orden, payload.estado, payload.detalles, nombre_cliente=payload.nombre_cliente, username=usuario_actual.username
    )

    if resultado is None or not resultado:
        raise HTTPException(500, "No se pudo actualizar el pedido")

    return {"detail": "El pedido se actualizo correctamente"}


@router.get("/conteo/semanal")
async def obtener_conteo_Ordenes_semanal():
    conteo = service.conteo_Ordenes_semanal()
    return conteo



@router.get("/platillos/conteo")
async def obtener_platillos_populares():
    platillos = service.obtener_contador_platillos()
    return platillos