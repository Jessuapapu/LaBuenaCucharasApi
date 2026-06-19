from fastapi import APIRouter, Depends

# Importamos nuestro guardián
from src.security.dependency import RequireRole

from src.models import platillos

from . import auth, analytics ,menu_diario, platillos, clientes, pedidos, proveedores, abastecimiento, facturas, comedor, imagenes, ordenes, caja, ingredientes

app_router = APIRouter()

@app_router.get("/")
async def health():
    return "OK"

# ============================================================
# RUTAS PÚBLICAS Y MIXTAS
# ============================================================

app_router.include_router(auth.router)
app_router.include_router(menu_diario.router, prefix="/menu")
app_router.include_router(imagenes.router, prefix="/imagenes")
app_router.include_router(comedor.router, prefix="/comedor")    
app_router.include_router(ordenes.router, prefix="/ordenes")


# ============================================================
# RUTAS PROTEGIDAS NIVEL: ADMIN + MESERO
# ============================================================
dependencia_operativa = [Depends(RequireRole(["admin", "mesero"]))]

app_router.include_router(clientes.router, prefix="/clientes", dependencies=dependencia_operativa)
app_router.include_router(pedidos.router, prefix="/pedidos", dependencies=dependencia_operativa)
app_router.include_router(platillos.router, prefix="/platillos", dependencies=dependencia_operativa)

"""app_router.include_router(clientes.router, prefix="/clientes")
app_router.include_router(pedidos.router, prefix="/pedidos")
app_router.include_router(platillos.router, prefix="/platillos")"""

# ============================================================
# RUTAS PROTEGIDAS NIVEL: SOLO ADMIN
# ============================================================
dependencia_admin = [Depends(RequireRole(["admin"]))]

app_router.include_router(proveedores.router, prefix="/proveedores", dependencies=dependencia_admin)
app_router.include_router(abastecimiento.router, prefix="/bodega", dependencies=dependencia_admin)
app_router.include_router(facturas.router, prefix="/facturas", dependencies=dependencia_admin)
app_router.include_router(caja.router, prefix='/caja', dependencies=dependencia_admin)
app_router.include_router(ingredientes.router, prefix='/ingrediente', dependencies=dependencia_admin)
app_router.include_router(analytics.router, prefix='/informe', dependencies=dependencia_admin)

"""app_router.include_router(proveedores.router, prefix="/proveedores")
app_router.include_router(abastecimiento.router, prefix="/bodega")
app_router.include_router(facturas.router, prefix="/facturas")"""