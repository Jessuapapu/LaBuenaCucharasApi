from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.clientes import service

router = APIRouter()

class ClientesIn(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    correo: str

@router.get("/")
async def obtener_clientes():
    clientes = service.listar_clientes()

    if clientes is None:
        return []

    return clientes


@router.post("/")
async def registrar_cliente(payload: ClientesIn):
    cliente = service.crear_cliente(
        nombre=payload.nombre,
        direccion=payload.direccion,
        correo=payload.correo,
        telefono=payload.telefono,
    )

    if cliente is None:
        raise HTTPException(500, {"message": "No se pudo crear el cliente"})

    return {
        "message": "Cliente creado exitosamente",
        "cliente": cliente
    }
