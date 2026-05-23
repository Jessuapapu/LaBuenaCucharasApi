from src.config.socket import sio
from src.services.ordenes import service as ordenesService
from src.services.comedor import service as comedorService
from src.models.comedor import models as comedor
from src.models.ordenes import models as ordenes
from src.schemas.ComedorPedidos import OrdenComedorIN
from src.models.ordenes.types import EstadoOrden

from decimal import Decimal

import datetime

MC = comedor.MonitorComedor()
print("EVENTOS CARGADOS")

@sio.on("crear_orden")
async def nueva_orden(sid, data):
    try:
        # Validamos para que lo detalles vayan correctamente formateados
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
    
        nueva_orden = ordenesService.crear_orden(datetime.datetime.now(),detalle=Detalles,Id_cliente=1)
        MC.agregar_orden(int(nueva_orden.IdOrdenes), NumeroMesa)

        if not nueva_orden:
            sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

        
    except: 
        await sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_generada", data={"IdMesa": NumeroMesa, "IdOrden": nueva_orden.IdOrdenes})

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

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden, Id_cliente=1, estado=EstadoOrden.PENDIENTE, detalles=Detalles)

        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

    except: 
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True})

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

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden,Id_cliente=1,estado=EstadoOrden.ANULADO,detalles=Detalles)

        MC.eliminar_orden(IdMesa= NumeroMesa, IdOrden=id_orden)
        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS",'ERROR')

    except: 
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GENERAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True})

@sio.on("guardar_orden")
async def guardar_estado_orden(sid, data):
    try:
        
        # Validamos para que lo detalles vayan correctamente formateados
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa
        orden = MC.obtener_ordenActiva(IdMesa=NumeroMesa)

        if not orden:
            sio.emit("error_actualizar", {"MENSAJE": "ERROR AL GUARDAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log("ERROR AL GUARDAR LA ORDEN MESA",'ERROR')

        id_orden = orden["IdOrden"]

        orden_actualizado: True | None = ordenesService.actualizar_ordenes(id_pedido=id_orden,Id_cliente=1,estado=EstadoOrden.ENTREGADO,detalles=Detalles)

        MC.guardar_orden(IdMesa=NumeroMesa,IdOrden=id_orden)
        if not orden_actualizado:
            sio.emit("error_actualizar",{"MENSAJE": "ERROR AL ACTUALIZAR LA ORDEN MESA"}, to=sid)
            comedor.logs.add_log('ERROR',"ERROR AL GUARDAR LA ORDEN MESA PUEDE SER LOS DATOS")

    except: 
        await sio.emit("error_actualizar",{"MENSAJE": "ERROR AL GUARDAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log("ERROR AL GUARDAR LA ORDEN MESA",'ERROR')

    await sio.emit("orden_actualizar", data={"Status": True})



