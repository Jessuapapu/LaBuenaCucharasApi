from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.clientes import service

router = APIRouter()

class ClientesIn(BaseModel):
    nombre: str
    direccion: str

@router.get("/")
async def obtener_clientes():
    pass


@router.post("/")
async def registrar_cliente(payload: ClientesIn):
    cliente = service.crear_cliente(nombre=payload.nombre, direccion=payload.direccion)

    if not cliente:
        raise HTTPException(500, {"message": "No se pudo crear el cliente"})

    return {
        "message": "Cliente creado exitosamente",
        "cliente": cliente
    }
