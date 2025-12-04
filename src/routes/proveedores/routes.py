from fastapi import APIRouter
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
    pass


@router.post("/")
async def registrar_proveedores(payload: ProveedorIn):
    proveedor = service.registrar_proveedor(payload.nombre, payload.direccion, payload.tipo)

    return None
