from fastapi import APIRouter, HTTPException
from src.services.proveedores import service
from src.models.insumos.types import TipoDeProveedor
from pydantic import BaseModel

class ProveedorIn(BaseModel):
    nombre: str
    direccion: str
    tipo: TipoDeProveedor

router = APIRouter()

@router.get("/")
async def obtener_proveedores():
    proveedores = service.obtener_proveedores()

    return proveedores


@router.get("/{nombre}")
async def obtener_proveedor_por_nombre(nombre: str):
    proveedores = service.obtener_proveedor_por_nombre(nombre)

    return proveedores


@router.post("/")
async def registrar_proveedores(payload: ProveedorIn):
    proveedor = service.registrar_proveedor(payload.nombre, payload.direccion, payload.tipo)

    if proveedor is None:
        raise HTTPException(500, "No se pudo registrar al proveedor")

    return {"message": "Proveedor registrado con exito"}
