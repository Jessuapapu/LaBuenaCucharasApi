from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def obtener_historial_abastecimiento():
    pass


@router.post("/")
async def registrar_abastecimiento():
    pass
