from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import Optional
from src.services.insumos import services as insumosService
from src.schemas.insumos import InsumoCreateSchema, InsumoUpdateSchema
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario

router = APIRouter(tags=["Insumos"])

@router.post("/", status_code=201)
def crear_nuevo_insumo(
    payload: InsumoCreateSchema, 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = insumosService.crear_insumo(
        payload=payload,
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="Error al crear el insumo. Verifique los datos enviados."
        )
        
    return {"message": "Insumo creado con éxito"}


@router.get("/")
def obtener_todos_los_insumos(
    pagina: int = Query(1, ge=1),
    rows: int = Query(10, ge=2),
    todo: int = Query(0, ge=0, le=1)
):
    try:
        data = insumosService.listar_insumos(pagina=pagina, rows=rows, todo=todo)
        
        if data is None:
            raise HTTPException(status_code=500, detail="Error al recuperar la lista de insumos")
            
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_insumo}")
def obtener_detalles_de_un_insumo(
    id_insumo: int = Path(..., title="ID del Insumo", description="Obligatorio para ver sus detalles")
):
    try:
        data = insumosService.obtener_insumo_por_id(id_insumo=id_insumo)
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail="No se encontró el insumo solicitado."
            )

        return {
            "success": True, 
            "data": data
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{id_insumo}")
def actualizar_insumo(
    payload: InsumoUpdateSchema, 
    id_insumo: int = Path(...), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = insumosService.actualizar_insumo(
        id_insumo=id_insumo,
        payload=payload,
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="No se pudo actualizar el insumo. Verifique que el ID exista y los datos sean válidos."
        )
        
    return {"message": "Insumo actualizado con éxito"}


@router.delete("/{id_insumo}")
def borrar_insumo(
    id_insumo: int = Path(...), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = insumosService.eliminar_insumo(
        id_insumo=id_insumo, 
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=404, 
            detail="Insumo no encontrado o error al eliminar."
        )
        
    return {"message": "Insumo eliminado con éxito"}