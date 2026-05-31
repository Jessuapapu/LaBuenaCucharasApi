from src.config.socket import sio
from src.services.ordenes import service as ordenesService
from src.services.comedor import service as comedorService
from src.models.comedor import models as comedor
from src.models.ordenes import models as ordenes
from src.schemas.ComedorPedidos import OrdenComedorIN
from src.models.ordenes.types import EstadoOrden
from src.services.auditorias.services import registrar_auditoria_orden
from src.models.auditorias.types import TipoDeAccion

from decimal import Decimal

import datetime

# Usar la instancia compartida del servicio de comedor (evita estados duplicados)
MC = comedorService.MC
print("EVENTOS CARGADOS")

@sio.on("crear_orden")
async def nueva_orden(sid, data):
    try:
        # Validamos para que lo detalles vayan correctamente formateados
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
    
        # intentar obtener username desde el payload (si el cliente lo envía)
        username = "system"

        nueva_orden = ordenesService.crear_orden(datetime.datetime.now(),detalle=Detalles,Id_cliente=1)
        MC.agregar_orden(int(nueva_orden.IdOrdenes), NumeroMesa)

        # Registrar auditoría de orden creada desde websocket
        try:
            registrar_auditoria_orden(username, nueva_orden.IdOrdenes, TipoDeAccion.CREAR)
        except Exception:
            pass

        if not nueva_orden:
            await sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})
        
    except: 
        await sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_generada", data={"IdMesa": NumeroMesa, "IdOrden": nueva_orden.IdOrdenes}, to=sid)

@sio.on("actualizar_orden")
async def actualizar_orden(sid, data):
    try:
        
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        orden = MC.obtener_ordenActiva(IdMesa=NumeroMesa)

        if not orden:
            sio.emit("error_actualizar", {"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log('ERROR',"ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS")

        id_orden = orden["IdOrden"] 

        username = "system"

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden, Id_cliente=1, estado=EstadoOrden.PENDIENTE, detalles=Detalles, username=username)

        # Auditoría: actualización desde websocket
        try:
            
            
            registrar_auditoria_orden(username, id_orden, TipoDeAccion.ACTUALIZAR)
        except Exception:
            pass

        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})

    except: 
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True}, to=sid)

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

        # Auditoría: cancelación/eliminación desde websocket
        try:
            registrar_auditoria_orden(username, id_orden, TipoDeAccion.ELIMINAR)
        except Exception:
            pass
        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
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
            sio.emit("error_actualizar", {"MENSAJE": "ERROR AL GUARDAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GUARDAR LA ORDEN MESA",'ERROR')

        id_orden = orden["IdOrden"]

        username = "system"

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden,Id_cliente=1,estado=EstadoOrden.ENTREGADO,detalles=Detalles, username=username)

        MC.guardar_orden(IdMesa=NumeroMesa,IdOrden=id_orden)

        # Auditoría: guardar/entregar
        try:
            registrar_auditoria_orden(username, id_orden, TipoDeAccion.ACTUALIZAR)
        except Exception:
            pass
        
        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log('ERROR',"ERROR AL GUARDAR LA ORDEN MESA PUEDE SER LOS DATOS")

        await sio.emit("orden_actualizada", data={'IdMesa': NumeroMesa})
    except: 
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL GUARDAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GUARDAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True}, to=sid)



