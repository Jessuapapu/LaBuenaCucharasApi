from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import Optional
from src.services.ingredientes.services import service as ingredientesService
from src.schemas.ingredientes import IngredienteCreateSchema, IngredienteUpdateSchema
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario

router = APIRouter(tags=["Ingredientes"])

@router.post("/", status_code=201)
def crear_nuevo_ingrediente(
    payload: IngredienteCreateSchema, 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = ingredientesService.crear_ingrediente(
        payload=payload,
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="Error al crear el ingrediente. Verifique los datos enviados."
        )
        
    return {"message": "Ingrediente y su configuración creados con éxito"}


@router.get("/")
def obtener_todos_los_ingredientes(
    pagina: int = Query(1, ge=1),
    rows: int = Query(10, ge=2),
    todo: int = Query(0, ge=0, le=1)
):
    try:
        data = ingredientesService.listar_ingredientes(pagina=pagina, rows=rows, todo=todo)
        
        if data is None:
            raise HTTPException(status_code=500, detail="Error al recuperar la lista de ingredientes")
            
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analisis-perecederos")
def obtener_analisis_de_inventario(
    id_ingrediente: Optional[int] = Query(None, description="Filtrar análisis por un ingrediente específico")
):
    try:
        data = ingredientesService.analisis_inventario_perecederos(id_ingrediente=id_ingrediente)
        
        if data is None:
            raise HTTPException(
                status_code=500, 
                detail="Error al generar el análisis de inventario perecedero."
            )

        return {
            "success": True, 
            "data": data,
            "metadata": {
                "total_registros_analizados": len(data)
            }
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{id_ingrediente}")
def obtener_detalles_de_un_ingrediente(
    id_ingrediente: int = Path(..., title="ID del Ingrediente", description="Obligatorio para ver sus detalles")
):
    try:
        data = ingredientesService.obtener_ingrediente_por_id(id_ingrediente=id_ingrediente)
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail="No se encontró el ingrediente solicitado."
            )

        return {
            "success": True, 
            "data": data
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{id_ingrediente}")
def actualizar_ingrediente(
    payload: IngredienteUpdateSchema, 
    id_ingrediente: int = Path(...), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = ingredientesService.actualizar_ingrediente(
        id_ingrediente=id_ingrediente,
        payload=payload,
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="No se pudo actualizar el ingrediente. Verifique que el ID exista."
        )
        
    return {"message": "Ingrediente actualizado con éxito"}


@router.delete("/{id_ingrediente}")
def borrar_ingrediente(
    id_ingrediente: int = Path(...), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = ingredientesService.eliminar_ingrediente(
        id_ingrediente=id_ingrediente, 
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=404, 
            detail="Ingrediente no encontrado o error al eliminar."
        )
        
    return {"message": "Ingrediente y su configuración de perecedero eliminados con éxito"}
@router.get("/analisis-perecederos")
def obtener_analisis_de_inventario(
    id_ingrediente: Optional[int] = Query(None, description="Filtrar por un ingrediente específico")
):
    try:
        data = ingredientesService.analisis_inventario_perecederos(id_ingrediente=id_ingrediente)
        
        if data is None:
            raise HTTPException(
                status_code=500, 
                detail="Error al generar el análisis de inventario perecedero."
            )

        return {
            "success": True, 
            "data": data,
            "metadata": {
                "total_registros_analizados": len(data)
            }
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")