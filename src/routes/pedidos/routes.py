from typing import Optional
from src.schemas.pedidos import PedidosIn, PedidosUpdate
from fastapi import APIRouter, HTTPException, Query
from src.services.pedidos import service
import datetime

router = APIRouter()


@router.get("/")
async def obtener_pedidos(
    pagina: int = Query(1, description="Número de página"), 
    rows: int = Query(10, description="Filas por página"), 
    todo: bool = Query(False, description="Traer todo sin paginar")
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
async def obtener_conteo_Ordenes_semanal():
    conteo = service.conteo_Ordenes_semanal()
    return conteo


@router.get("/facturas")
async def obtener_facturas_endpoint(
    id_cliente: int | None = Query(default=None),
    id_orden: int | None = Query(default=None),
    fecha_inicio: datetime.datetime | None = Query(default=None),
    fecha_fin: datetime.datetime | None = Query(default=None),
    monto: float | None = Query(default=None),
    monto_fin: float | None = Query(default=None),
    cantidad_total: int | None = Query(default=None)
):
    facturas = service.obtener_facturas_ordenes(
        id_cliente=id_cliente,
        id_orden=id_orden,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto=monto,
        monto_fin=monto_fin,
        cantidad_total=cantidad_total
    )

    if not facturas:
        return []

    return facturas


@router.get("/platillos/conteo")
async def obtener_platillos_populares():
    platillos = service.obtener_contador_platillos()
    return platillos
