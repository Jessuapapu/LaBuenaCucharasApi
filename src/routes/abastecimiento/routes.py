from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Optional
import src.services.abastecimiento.service as abastecimientoService
from src.schemas.abastecimiento import AbastecimientoCreateSchema
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario

router = APIRouter(tags=["Abastecimiento"])

@router.post("/", status_code=201)
def registrar_nuevo_abastecimiento(
    payload: AbastecimientoCreateSchema, 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    exito = abastecimientoService.registrar_abastecimiento(
        payload=payload,
        username=usuario_actual.username
    )
    
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="Error al crear el abastecimiento. Verifique que los datos de insumos o ingredientes sean válidos."
        )
        
    return {"message": "Registro de abastecimiento generado con éxito"}


@router.get("/")
def obtener_todos_los_abastecimientos():
    try:
        data = abastecimientoService.obtener_historial_abastecimiento()
        
        if data is None:
            raise HTTPException(status_code=500, detail="Error al recuperar el historial de abastecimiento")
            
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_abastecimiento}")
def obtener_detalles_de_un_abastecimiento(
    id_abastecimiento: int = Path(..., title="ID del Abastecimiento principal", description="Obligatorio para ver sus detalles")
):
    try:
        data = abastecimientoService.obtener_detalles_abastecimiento(id_registro=id_abastecimiento)
        
        # Si devuelve None o un diccionario vacío
        if not data:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron detalles para este abastecimiento."
            )

        return {
            "success": True, 
            "data": data
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")