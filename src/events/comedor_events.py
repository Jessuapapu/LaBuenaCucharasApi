from src.config.socket import sio
from src.services.ordenes import service as ordenesService
from src.services.comedor import service as comedorService
from src.services.caja import service as cajaService # 🆕 Importamos el servicio de Caja
from src.models.comedor import models as comedor
from src.schemas.ComedorPedidos import OrdenComedorIN
from src.schemas.pedidos import Detalles
from src.models.ordenes.types import EstadoOrden
from src.services.auditorias.services import registrar_auditoria_orden
from src.models.auditorias.types import TipoDeAccion
from decimal import Decimal
import datetime

MC = comedorService.MC
print("EVENTOS DEL COMEDOR CARGADOS")

# Función de apoyo para calcular el total de los detalles recibidos
def calcular_total_detalles(detalles: list[Detalles]) -> float:
    total = 0.0
    for d in detalles:
        # Como 'd' es un modelo Pydantic, usamos la notación de punto (.)
        cantidad = float(d.cantidad)
        precio = float(d.precio_unitario)
        total += (cantidad * precio)
        
    return total

@sio.on("crear_orden")
async def nueva_orden(sid, data):
    try:
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        username = "system"

        nueva_orden = ordenesService.crear_orden(datetime.datetime.now(), detalle=Detalles, Id_cliente=1)
        MC.agregar_orden(int(nueva_orden.IdOrdenes), NumeroMesa)

        try:
            registrar_auditoria_orden(username, nueva_orden.IdOrdenes, TipoDeAccion.CREAR)
        except Exception:
            pass

        if not nueva_orden:
            await sio.emit("error_generar", {"MENSAJE": "ERROR AL GENERAR LA ORDEN"}, to=sid)
            return

        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})
        await sio.emit("orden_generada", data={"IdMesa": NumeroMesa, "IdOrden": nueva_orden.IdOrdenes}, to=sid)
        
    except Exception as e: 
        print(f"Error WS crear_orden: {e}")
        await sio.emit("error_generar", {"MENSAJE": "ERROR CRÍTICO AL CREAR"}, to=sid)

@sio.on("actualizar_orden")
async def actualizar_orden(sid, data):
    try:
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        orden = MC.obtener_ordenActiva(IdMesa=NumeroMesa)

        if not orden:
            await sio.emit("error_actualizar", {"MENSAJE": "ORDEN NO ENCONTRADA EN MESA"}, to=sid)
            return

        id_orden = orden["IdOrden"] 
        username = "system"

        orden_actualizada = ordenesService.actualizar_ordenes(id_pedido=id_orden, Id_cliente=1, estado=EstadoOrden.PENDIENTE, detalles=Detalles, username=username)

        estado_caja = cajaService.obtener_estado_caja()
        if estado_caja:
            total_nuevo = calcular_total_detalles(Detalles)
            if cajaService.CajaMonitor.validarId(id_orden):
                cajaService.Actualizar_Monto(id_orden, total_nuevo)
                await sio.emit("actualizar_caja", cajaService.obtener_Caja()) # Avisamos a la caja del cambio

        try:
            registrar_auditoria_orden(username, id_orden, TipoDeAccion.ACTUALIZAR)
        except Exception:
            pass

        if not orden_actualizada:
            await sio.emit("error_actualizar", {"MENSAJE": "ERROR AL ACTUALIZAR LA BD"}, to=sid)
            return

        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})
        await sio.emit("orden_actualizar", data={"Status": True}, to=sid)
    except Exception as e: 
        print(f"Error WS actualizar_orden: {e}")
        await sio.emit("error_actualizar", {"MENSAJE": "ERROR INTERNO"}, to=sid)

@sio.on("cancelar_orden")
async def cancelar_orden(sid, data):
    try:
        # Validamos para que lo detalles vayan correctamente formateados
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        orden = MC.obtener_ordenActiva(IdMesa=NumeroMesa)

        if not orden:
            sio.emit("error_actualizar", {"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

        id_orden = orden["IdOrden"]

        username = "system"

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden,Id_cliente=1,estado=EstadoOrden.ANULADO,detalles=Detalles, username=username)

        MC.eliminar_orden(IdMesa= NumeroMesa, IdOrden=id_orden)
        cajaService.CajaMonitor.AnularOrden(id_orden)

        # Auditoría: cancelación/eliminación desde websocket
        try:
            registrar_auditoria_orden(username, id_orden, TipoDeAccion.ELIMINAR)
        except Exception:
            pass
        if not orden_actualizado:
            await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

        
        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})
    except:     
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True}, to=sid)

@sio.on("guardar_orden")
async def guardar_estado_orden(sid, data):
    try:
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        orden = MC.obtener_ordenActiva(IdMesa=NumeroMesa)

        if not orden:
            await sio.emit("error_actualizar", {"MENSAJE": "NO HAY ORDEN ACTIVA EN LA MESA"}, to=sid)
            return

        id_orden = orden["IdOrden"]
        
        # 1. Verificar si la caja está abierta
        if not cajaService.obtener_estado_caja():
            await sio.emit("error_actualizar", {"MENSAJE": "LA CAJA ESTÁ CERRADA. NO SE PUEDE MANDAR LA CUENTA."}, to=sid)
            return
        # 2. Calcular el total (Necesitas adaptar calcular_total_detalles a la estructura exacta de tus Detalles)
        total_pagar = calcular_total_detalles(Detalles)
        if total_pagar <= 0:
            await sio.emit("error_actualizar", {"MENSAJE": "EL MONTO DE LA ORDEN DEBE SER MAYOR A 0"}, to=sid)
            return

        # 3. Enviar a la Memoria de la Caja
        if cajaService.CajaMonitor.validarId(id_orden):
            # Ya existía en caja (el mesero agregó algo y volvió a mandar) -> Actualizamos
            cajaService.Actualizar_Monto(IdOrden=id_orden, Monto=total_pagar)
        else:
            # Es la primera vez que se manda a caja -> Insertamos
            cajaService.Mandar_a_caja(IdOrden=id_orden, Monto=total_pagar)


        # 5. Notificar a las pantallas correspondientes
        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa}) # Limpia la mesa al mesero
        await sio.emit("actualizar_caja", cajaService.obtener_Caja())    # Suena en el monitor de caja
        
        await sio.emit("orden_actualizar", data={"Status": True, "Msj": "Enviado a Caja"}, to=sid)

    except Exception as e: 
        print(f"Error WS guardar_orden (Mandar a Caja): {e}")
        await sio.emit("error_actualizar", {"MENSAJE": "ERROR AL MANDAR A CAJA"}, to=sid)