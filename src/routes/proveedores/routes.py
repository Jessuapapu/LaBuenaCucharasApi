from fastapi import APIRouter, HTTPException, Query, Depends, Body
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
from src.schemas.proveedor import ProveedorIn, ProveedorUpdate
from src.services.proveedores import service

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.get("/")
async def obtener_proveedores(
    pagina: int = Query(1, description="Número de página"),
    rows: int = Query(10, description="Filas por página"),
    todo: bool = Query(False, description="Traer todo sin paginar"),
    nombre: str | None = Query(None, description="Nombre del proveedor")
):
    proveedores = service.listar_proveedores(pagina=pagina, rows=rows, todo=todo, nombre=nombre)
    return proveedores

@router.post("/")
async def crear_proveedor(payload: ProveedorIn, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    proveedor = service.crear_proveedor(payload.dict())
    
    if not proveedor:
        raise HTTPException(500, "No se pudo crear el proveedor")
        
    return {"message": "Proveedor creado exitosamente"}

@router.put("/{id_proveedor}")
async def actualizar_proveedor(id_proveedor: int, payload: ProveedorUpdate, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    resultado = service.actualizar_proveedor(id_proveedor, payload.dict())
    
    if not resultado:
        raise HTTPException(500, "No se pudo actualizar el proveedor")
        
    return {"detail": "El proveedor se actualizó correctamente"}

@router.delete("/{id_proveedor}")
async def eliminar_proveedor(id_proveedor: int, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    resultado = service.eliminar_proveedor(id_proveedor)
    
    if not resultado:
        raise HTTPException(500, "No se pudo eliminar el proveedor")
        
    return {"detail": "El proveedor se eliminó correctamente"}