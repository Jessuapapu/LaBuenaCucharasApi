from fastapi import APIRouter, HTTPException, Query
from src.services.facturas import service
import datetime
from src.schemas.facturas import facturaIn



router = APIRouter()

@router.get("/")
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

@router.post("/")
async def actualizar_factura(payload: facturaIn):

    factura = service.crear_facturas(payload)

    return factura