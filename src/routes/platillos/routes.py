from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.platillos.service import añadir_platillo

router = APIRouter()

class PlatilloIn(BaseModel):
    nombre_platillo: str


@router.get("/", response_model=None)
async def obtener_platillos():
    pass


@router.get("/{nombre_platillo}", response_model=None)
async def obtener_platillo(nombre_platillo: str | None):
    pass


@router.post("/", response_model=None)
async def crear_platillo(payload: PlatilloIn):
    try:
        añadir_platillo(payload.nombre_platillo)
        return {"detail": "Platillo añadido con exito"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
