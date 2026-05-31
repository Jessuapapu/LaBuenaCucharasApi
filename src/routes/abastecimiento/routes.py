from decimal import Decimal
from fastapi import APIRouter
from src.services.proveedores import service

router = APIRouter()

@router.get("/")
async def obtener_historial_abastecimiento():
    historial = service.obtener_historial_abastecimiento()
    return historial


@router.post("/")
async def registrar_abastecimiento(
    costo_total: Decimal, id_proveedor: int, total_ingresado: int
):
    registro = service.registrar_abastecimiento(
        costo_total, id_proveedor, total_ingresado
    )
    return registro

@router.get("/detalles/{IdAbas}")
async def obtener_historial_abastecimiento(IdAbas: int):
    historial = service.obtener_detalles_abastecimiento(IdAbas)
    return historial
