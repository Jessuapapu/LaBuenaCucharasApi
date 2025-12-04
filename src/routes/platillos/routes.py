from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.platillos import service

router = APIRouter()

class PlatilloIn(BaseModel):
    nombre_platillo: str
    nombre_categoria: str


class CategoriaIn(BaseModel):
    nombre_categoria: str


@router.get("/", response_model=None)
async def obtener_platillos():
    platillos = service.obtener_platillos_service()

    if not platillos or platillos == []:
        return HTTPException(500, "Error al obtener los platillos")

    return platillos


@router.post("/", response_model=None)
async def crear_platillo(payload: PlatilloIn):
    try:
        service.añadir_platillo(payload.nombre_platillo, payload.nombre_categoria)
        return {"detail": "Platillo añadido con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.post("/categoria", response_model=None)
async def crear_categoria(payload: CategoriaIn):
    try:
        service.añadir_categoria_platillo(payload.nombre_categoria)
        return {"detail": "Categoria añadida con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
