from fastapi import APIRouter, HTTPException, Depends
from src.schemas.platillos import PlatilloIn, CategoriaIn
from src.services.platillos import service
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario

router = APIRouter()

@router.get("/", response_model=None)
async def obtener_platillos():
    platillos = service.obtener_platillos_service()

    if not platillos or platillos == []:
        return HTTPException(500, "Error al obtener los platillos")

    return platillos


@router.get("/categoria", response_model=None)
async def obtener_categorias():
    try:
        categorias = service.obtener_categorias_platillos_service()
        if not categorias:
            raise HTTPException(status_code=404, detail="No se encontraron categorías")
        return categorias
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.post("/", response_model=None)
async def crear_platillo(payload: PlatilloIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        # Se valida si la funcion retorna un none para decir que no pudo agregar el platillo
        if not service.añadir_platillo(payload.nombre_platillo, payload.nombre_categoria, username=usuario_actual.username):
            return {"detail": "Error al agregar el platillo"}
        
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


