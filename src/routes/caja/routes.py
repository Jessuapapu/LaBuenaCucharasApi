from fastapi import APIRouter, HTTPException, Query, Depends
from src.services.caja import service as Caja
from src.schemas.caja import *
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario
from src.config.socket import sio

from src.services.comedor import service as comedorService
MC = comedorService.MC

router = APIRouter(tags=["Caja"])

@router.put('/abrir')
async def abrir_Caja(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    if Caja.obtener_estado_caja():
        return {"msj": "Ya Caja abierta", "status": False}
    Caja.abrir_Caja()
    sio.emit('estado_caja', {"estado": True})
    return {"msj": "Caja abierta", "status": True}

@router.put('/cerrar')
async def cerrar_Caja(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    if not Caja.obtener_estado_caja():
        return {"msj": "Caja aun no abierta", "status": False}
    
    if not Caja.Cerrar_Caja(usuario_actual.username):
        raise HTTPException(400, {"msj": "No se puede cerrar la caja. Hay órdenes activas pendientes o error de servidor.", "status": False})
    
    sio.emit('estado_caja', {"estado": False})
    return {"msj": "Caja cerrada", "status": True}

@router.get('/')
async def obtener_caja():
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    return Caja.obtener_Caja()

@router.get('/Estado')
async def obtener_estado_caja():
    estado = Caja.obtener_estado_caja()
    return {"status": estado}

@router.post('/')
async def nueva_cuenta(payload: CuentaOrdenIn):
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})

    cuenta = Caja.Mandar_a_caja(payload.IdOrden, payload.Monto)
    if not cuenta:
        raise HTTPException(403, {"msj": "Error al mandar a caja. Orden ya existe o datos inválidos", "status": False})
    
    sio.emit('actualizar_caja', cuenta)
    return cuenta

@router.put('/pagar') 
async def procesar_pago(payload: PagoIn):
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    
    restante = Caja.Pagar_cuenta(payload.IdOrden, payload.Monto, payload.Metodo, payload.Referencia)
    if restante is False:
        raise HTTPException(400, {"msj": "Error al procesar el pago", "status": False})
    
    cuenta_actualizada = Caja.obtener_cuenta(payload.IdOrden)
    sio.emit('actualizar_caja', cuenta_actualizada)
    return {"msj": "Pago registrado", "restante": restante, "status": True}

@router.post('/finalizar/{id_orden}')
async def finalizar_orden(id_orden: int):
    # Este endpoint se llama cuando la cuenta llega a 0 para cerrarla y guardarla en DB
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    
    exito = Caja.Cancelar_Cuenta(id_orden)
    if not exito:
        raise HTTPException(400, {"msj": "Error al finalizar orden. Asegúrese que el saldo sea 0", "status": False})
    
    MC.guardar_orden(IdOrden=id_orden)
    

    sio.emit('orden_finalizada', {"IdOrden": id_orden})
    sio.emit('actualizar_caja', Caja.obtener_Caja())
    return {"msj": "Orden finalizada y guardada en BD", "status": True}

@router.put('/actualizar')
async def actualizar_monto_orden(payload: ActualizarMontoIn):
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    
    cuenta = Caja.Actualizar_Monto(payload.IdOrden, payload.Monto)
    if not cuenta:
        raise HTTPException(400, {"msj": "Error al actualizar monto", "status": False})
    
    sio.emit('actualizar_caja', cuenta)
    return {"msj": "Monto actualizado", "cuenta": cuenta, "status": True}

@router.delete('/{id_orden}')
async def anular_orden(id_orden: int):
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    
    exito = Caja.Anular_Cuenta(id_orden)
    if not exito:
        raise HTTPException(400, {"msj": "Error al anular orden", "status": False})
    
    sio.emit('orden_anulada', {"IdOrden": id_orden})
    sio.emit('actualizar_caja', Caja.obtener_Caja())
    return {"msj": "Orden anulada con éxito", "status": True}


@router.post('/reembolso')
async def emitir_reembolso(payload: ReembolsoIn):
    if not Caja.obtener_estado_caja():
        raise HTTPException(418, {"msj": "Caja aun no abierta", "status": False})
    
    exito = Caja.Reembolsar(payload.IdOrden, payload.Monto, payload.Razon)
    if not exito:
        raise HTTPException(400, {"msj": "Error al procesar el reembolso. Verifique que la orden exista y tenga pagos.", "status": False})
    
    sio.emit('actualizar_caja', Caja.obtener_Caja())
    return {"msj": "Reembolso registrado con éxito", "status": True}