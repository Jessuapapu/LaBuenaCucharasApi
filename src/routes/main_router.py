from fastapi import APIRouter

from src.models import platillos
from . import menu_diario, platillos, clientes, pedidos, proveedores, abastecimiento, facturas, comedor

app_router = APIRouter()


@app_router.get("/")
async def health():
    return "OK"

app_router.include_router(menu_diario.router, prefix="/menu")
app_router.include_router(platillos.router, prefix="/platillos")
app_router.include_router(clientes.router, prefix="/clientes")
app_router.include_router(pedidos.router, prefix="/pedidos")
app_router.include_router(proveedores.router, prefix="/proveedores")
app_router.include_router(abastecimiento.router, prefix="/bodega")
app_router.include_router(facturas.router, prefix="/facturas")
app_router.include_router(comedor.router, prefix="/comedor")