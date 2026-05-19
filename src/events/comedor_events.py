from src.config.socket import sio
from src.services.ordenes import service as ordenesService
from src.services.comedor import service as comedorService
from src.models.comedor import models as comedor
from src.models.ordenes import models as ordenes
from src.schemas.ComedorPedidos import OrdenComedorIN

from decimal import Decimal

import datetime

MC = comedor.MonitorComedor()
print("EVENTOS CARGADOS")

@sio.on("crear_orden")
async def nueva_orden(sid, data):
    print("SIMON YA LO AGARRO")
    try:
        # Validamos para que lo detalles vayan correctamente formateados
        datos_validados = OrdenComedorIN(**data)
        Detalles = datos_validados.Detalles
        NumeroMesa = datos_validados.IdMesa

        nueva_orden = ordenesService.crear_orden("EXPORANERO/COMEDOR",datetime.datetime.now(),detalle=Detalles)

        if not nueva_orden:
            sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS"}, to=sid)
            comedor.logs.add_log('ERROR',"ERROR AL GENERAR LA ORDEN MESA PUEDE SER LOS DATOS")

        print(MC.agregar_orden(int(nueva_orden.IdOrdenes), NumeroMesa))
        print(MC.to_dict())
        print(NumeroMesa)
    except: 
        await sio.emit("error_generar",{"MENSAJE": "ERROR AL GENERAR LA ORDEN MESA"}, to=sid)
        comedor.logs.add_log('ERROR',"ERROR AL GENERAR LA ORDEN MESA")

    await sio.emit("orden_generada", data={"IdMesa": NumeroMesa, "IdOrden": nueva_orden.IdOrdenes})

@sio.on("actualizar_orden")
async def actualizar_orden(sid, data):
    pass

@sio.on("cancelar_orden")
async def cancelar_orden(sid, data):
    pass

@sio.on("actualizar_estado_orden")
async def listar_estado_orden(sid, data ):
    pass