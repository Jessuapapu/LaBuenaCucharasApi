import logging
from src.config.socket import sio
from src.schemas.caja import CuentaOrdenIn
from src.services.caja import service as servicesCaja

@sio.on('orden_caja')   
async def manda_a_caja_comedor(sid, data):
    try:
        # 1. Validación estricta con Pydantic
        datos_validados = CuentaOrdenIn(**data)
        IdOrden = datos_validados.IdOrden
        Monto = datos_validados.Monto

        # 2. Verificamos si la orden ya está en la memoria de la Caja
        cuenta = servicesCaja.obtener_cuenta(IdOrden)
        
        if not cuenta:
            # Creación: La orden llega a caja por primera vez
            cuenta = servicesCaja.Mandar_a_caja(IdOrden=IdOrden, Monto=Monto)
            if not cuenta:
                await sio.emit('error_agregar', {"msj": "Error al mandar a caja (verifique si está abierta)"}, to=sid)
                return
        else:
            # Actualización: La orden ya existía, pero cambió su total
            cuenta = servicesCaja.Actualizar_Monto(IdOrden=IdOrden, Monto=Monto)
            if not cuenta:
                await sio.emit('error_actualizar', {"msj": "Error al actualizar el monto en la caja"}, to=sid)
                return
        
        # 3. Broadcast: Notificamos a todos los clientes (cajeros) conectados
        await sio.emit('actualizar_caja', cuenta)
        
    except Exception as e:
        # Log del error en el servidor para debugging (Evita el "bare except" que oculta errores)
        logging.error(f"Error procesando socket 'orden_caja': {str(e)}")
        await sio.emit('error_agregar', {"msj": "Estructura de datos inválida o error interno"}, to=sid)