from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.models.clientes.types import EstadoContrato
from src.services.clientes import service
import datetime

router = APIRouter()

class ClientesIn(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    correo: str


class ContratosIn(BaseModel):
    nombre_cliente: str
    numero_contrato: int
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    presupuesto: float


class ContratoUpdateEstadoIn(BaseModel):
    nuevo_estado: EstadoContrato


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

    return {"message": "Cliente creado exitosamente"}


@router.get("/contratos")
async def obtener_contratos_clientes():
    contratos = service.obtener_contratos_clientes()

    if contratos is None:
        return []

    return contratos


@router.post("/contratos")
async def registrar_contrato_cliente(payload: ContratosIn):
    contrato = service.registrar_contrato_cliente(
        payload.nombre_cliente,
        payload.numero_contrato,
        payload.fecha_inicio,
        payload.fecha_fin,
        payload.presupuesto,
    )

    if contrato is None:
        raise HTTPException(500, {"message": "No se pudo crear el contrato"})

    return {"message": "Contrato creado exitosamente", "contrato": contrato}


@router.put("/contratos/{numero_contrato}/estado")
async def actualizar_estado_contrato(
    numero_contrato: int, payload: ContratoUpdateEstadoIn
):
    contrato = service.actualizar_estado_contrato(numero_contrato, payload.nuevo_estado)

    if contrato is None:
        raise HTTPException(
            500, {"message": "No se pudo actualizar el estado del contrato"}
        )

    return {
        "message": "Estado del contrato actualizado exitosamente",
        "contrato": contrato,
    }
