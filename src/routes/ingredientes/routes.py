from fastapi import APIRouter, Query
from src.services.ingredientes import services as serviceIngredientes
from src.schemas.ingredientes import *

router = APIRouter(tags=["Ingredientes"])

@router.get('/')
def obtener_ingredientes(IdIngrediente: int | None = Query(description='Id del Ingrediente', default=None),
    NombreIngrediente: str | None = Query(description='Nombre del ingrediente', default=None)):
    
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


@router.put('/{IdIngrediente}')
def actualizar_ingrediente(IdIngrediente: int, payload: ingrediente):
    estado = serviceIngredientes.actualizar_Ingrediente(IdIngrediente=IdIngrediente, NombreNuevo=payload.NombreIngrediente,stock=payload.Stock)
    return estado

