
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import src.services.pedidos.service as pedidosService
from src.models.pedidos.types import TipoPedidoss, EstadoPedido
from src.schemas.pedido import *

router = APIRouter()

@router.post("/", status_code=201)
def crear_nuevo_pedido(payload: PedidoCreateSchema):
    exito = pedidosService.crear_pedido(
        listaIdOrdenes=payload.listaIdOrdenes, 
        tipo_pedido=payload.TipoPedido
    )
    if not exito:
        raise HTTPException(
            status_code=400, 
            detail="Error al crear el pedido. Verifique que las órdenes sean válidas y del mismo cliente."
        )
    return {"message": "Pedido generado con éxito"}


@router.get("/")
def obtener_todos_los_pedidos(
    id_orden: Optional[int] = Query(None),
    id_pedido: Optional[int] = Query(None),
    id_cliente: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    rows: int = Query(10, ge=2),
    todo: int = Query(0, ge=0, le=1)
):
    try:
        data = pedidosService.listar_pedidos(
            id_orden=id_orden, id_pedido=id_pedido, id_cliente=id_cliente,
            tipo=tipo, pagina=pagina, rows=rows, todo=todo
        )
        if data == -1:
             raise HTTPException(status_code=400, detail="Parámetros de paginación inválidos")

        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_pedido}")
def obtener_detalles_de_un_pedido(
    id_pedido: int = Path(..., title="ID del Pedido principal", description="Obligatorio para ver sus detalles"),
    id_orden: Optional[int] = Query(None, description="Opcional: Filtrar por una orden específica dentro del pedido"),
    id_cliente: Optional[int] = Query(None, description="Opcional: Filtrar por un cliente en particular")
):
    try:
        data = pedidosService.obtener_detalles_pedido(
            id_pedido=id_pedido,
            id_orden=id_orden,
            id_cliente=id_cliente
        )
        
        # Si la lista vuelve vacía, significa que el pedido no existe o no tiene órdenes
        if not data:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron detalles para este pedido con los filtros proporcionados"
            )

        return {
            "success": True, 
            "data": data,
            "metadata": {
                "total_registros": len(data)
            }
        }
    except HTTPException as http_exc:
        raise http_exc # Respetamos el 404 lanzado arriba
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{id_pedido}")
def actualizar_pedido(payload: PedidoUpdateSchema, id_pedido: int = Path(...)):
    exito = pedidosService.modificar_pedido(
        id_pedido=id_pedido,
        estado=payload.Estado,
        tipo_pedido=payload.TipoPedido
    )
    if not exito:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o error al actualizar")
    return {"message": "Pedido actualizado con éxito"}


@router.delete("/{id_pedido}")
def borrar_pedido(id_pedido: int = Path(...)):
    exito = pedidosService.eliminar_pedido(id_pedido)
    if not exito:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o error al eliminar")
    return {"message": "Pedido y sus relaciones eliminados con éxito"}