from fastapi import APIRouter, HTTPException, Query, Depends
from src.services.clientes import service
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
import datetime
from src.schemas.clientes import *

router = APIRouter(tags=["Clientes"])


@router.get("/")
async def obtener_clientes():
    clientes = service.listar_clientes()

    if clientes is None:
        return []

    return clientes


@router.post("/")
async def registrar_cliente(payload: ClientesIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    cliente = service.crear_cliente(
        nombre=payload.nombre,
        direccion=payload.direccion,
        correo=payload.correo,
        telefono=payload.telefono,
        username=usuario_actual.username,
    )

    if cliente is None:
        raise HTTPException(500, {"message": "No se pudo crear el cliente"})

    return {"message": "Cliente creado exitosamente"}

@router.get("/contratos")
async def obtener_contratos_clientes_endpoint(
    id_cliente: int | None = Query(default=None, description="Filtra por el identificador único del cliente"),
    fecha_inicio: datetime.datetime | None = Query(default=None, description="Filtra contratos a partir de esta fecha de inicio"),
    fecha_vencimiento: datetime.datetime | None = Query(default=None, description="Filtra contratos hasta esta fecha de vencimiento"),
    presupuesto: float | None = Query(default=None, ge=0, description="Presupuesto inicial mínimo (debe ser mayor o igual a 0)"),
    presupuesto_fin: float | None = Query(default=None, description="Presupuesto final máximo")
):
    # Pasamos los parámetros de manera idéntica a la capa de servicio
    contratos = service.obtener_contratos_clientes(
        id_cliente=id_cliente,
        fecha_inicio=fecha_inicio,
        fecha_vencimiento=fecha_vencimiento,
        presupuesto=presupuesto,
        presupuesto_fin=presupuesto_fin
    )

    if not contratos: 
        return []

    return contratos


@router.post("/contratos")
async def registrar_contrato_cliente(payload: ContratosIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    contrato = service.registrar_contrato_cliente(
        payload.nombre_cliente,
        payload.numero_contrato,
        payload.fecha_inicio,
        payload.fecha_fin,
        payload.presupuesto,
        username=usuario_actual.username,
    )

    if contrato is None:
        raise HTTPException(500, {"message": "No se pudo crear el contrato"})

    return {"message": "Contrato creado exitosamente", "contrato": contrato}


@router.put("/contratos/{numero_contrato}/estado")
async def actualizar_estado_contrato(
    numero_contrato: int, payload: ContratoUpdateEstadoIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    contrato = service.actualizar_estado_contrato(numero_contrato, payload.nuevo_estado, username=usuario_actual.username)

    if contrato is None:
        raise HTTPException(
            500, {"message": "No se pudo actualizar el estado del contrato"}
        )

    return {
        "message": "Estado del contrato actualizado exitosamente",
        "contrato": contrato,
    }
