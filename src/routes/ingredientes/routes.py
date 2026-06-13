import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from src.services.ingredientes import services as serviceIngredientes
from src.schemas.ingredientes import *

router = APIRouter()

@router.get('/')
def obtener_ingredientes(IdIngrediente: int | None = Query(description='IdIngrediente', default=None),
 NombreIngrediente: str | None = Query(description='Nombre', default=None)):
    
    if not IdIngrediente and not NombreIngrediente:
        return serviceIngredientes.obtener_ingredientes()
    
    ingrediente = serviceIngredientes.obtener_ingrediente(IdIngrediente=IdIngrediente, Nombre=NombreIngrediente)

    return ingrediente


@router.post('/')
def crear_ingrediente(payload: ingrediente):
    estado = serviceIngredientes.crear_ingrediente(Nombre = payload.NombreIngrediente)
    return estado


@router.post('/relacion')
def crear_relacion_platillo_ingrediente(payload: PlatilloIngredienteIn):
    estado = serviceIngredientes.crear_relacion_platillo_ingrediente(listaIngrediente=payload.ingredientes, IdPlatillo=payload.IdPLatillo)
    return estado

