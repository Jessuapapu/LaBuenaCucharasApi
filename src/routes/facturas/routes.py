from fastapi import APIRouter, HTTPException, Query, Depends
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
from src.services.facturas import service
import datetime
from src.schemas.facturas import facturaIn



router = APIRouter(tags=["Facturas"])

@router.get("/")
async def obtener_facturas_endpoint(
    id_factura: int | None = Query(default=None),
    id_cliente: int | None = Query(default=None),
    id_orden: int | None = Query(default=None),
    fecha_inicio: datetime.datetime | None = Query(default=None),
    fecha_fin: datetime.datetime | None = Query(default=None),
    monto: float | None = Query(default=None),
    monto_fin: float | None = Query(default=None),
    cantidad_total: int | None = Query(default=None),
    pagina: int = Query(1, description="Número de página"), 
    rows: int = Query(10, description="Filas por página"), 
    todo: bool = Query(False, description="Traer todo sin paginar"),
):
    facturas = service.obtener_facturas_ordenes(
        Id_Facturas=id_factura, 
        id_cliente=id_cliente,
        id_orden=id_orden,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto=monto,
        monto_fin=monto_fin,
        cantidad_total=cantidad_total,
        pagina=pagina, 
        rows=rows, 
        todo=todo
    )

    if not facturas:
        return []

    return facturas

@router.post("/")
async def crear_factura(payload: facturaIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):

    id_generado = service.crear_facturas(payload, username=usuario_actual.username)
    if not id_generado:
        raise HTTPException(status_code=500, detail="No se pudo crear la factura")
    return {"message": "Factura creada", "id": id_generado}


@router.put("/{id_factura}")
async def actualizar_factura(id_factura: int, payload: facturaIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    resultado = service.actualizar_factura(id_factura, payload, username=usuario_actual.username)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Factura o alguna orden no encontrada")
    return {"message": "Factura actualizada"}

@router.get("/detalles/{id_factura}")
async def obtener_detalle_factura(id_factura: int):
    resultado = service.obtener_detalle(id_factura)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Factura o alguna orden no encontrada")
    return resultado