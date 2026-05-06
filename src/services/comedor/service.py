from src.models.comedor import models as comedor
from src.models.ordenes import models as orden
from src.schemas.pedidos import Detalles
from src.services.platillos.service import obtener_platillo_id_por_nombre   
from sqlmodel import Session
from src.config.database import db_engine
from datetime import datetime
MC = comedor.MonitorComedor()
horaApertura = None
horaCerrar = None

from logs import logsApp
logs = logsApp.Logs()

def agregar_orden_comedor(IdMesa: int, IdOrden: int):
    
    if IdMesa > MC.MaxIdGenerado or IdMesa < 0:
        return False
    
    MC.agregar_orden(IdMesa=IdMesa, IdOrden=IdOrden)
    return True

def abrir_comedor():
    global horaApertura 
    horaApertura = datetime.now()
    logs.add_log("APERTURA COMEDOR", "INFO")
    return

def cerrar_comedor():
    if not horaApertura:    
        return False
    
    with Session(db_engine) as session:
        try: 
            auditoria_nueva = comedor.Auditoria_Comedor(HoraApertura=horaApertura, HoraCerrar=datetime.now())
            logs.add_log("CERRAR COMEDOR", "INFO")
            session.add(auditoria_nueva)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(e)
            return False
        
def guardar_comedor_orden(IdMesa: int, IdOrden: int):
    orden = MC.guardar_orden(IdMesa=IdMesa, IdOrden=IdOrden)

    if not orden:
        return False

    with Session(db_engine) as session:
        try: 
            
            auditoria_nueva = comedor.Auditoria_Mesas(IdMesa=IdMesa, IdOrden=IdOrden, HoraEntrada=orden.HoraEntrada, 
            HoraSalida=orden.HoraSalida)

            session.add(auditoria_nueva)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(e)
            return False


def obtener_estado_activas(IdMesa: int):
    return MC.obtener_ordenActiva(IdMesa=IdMesa)

def obtener_estado_terminadas(IdMesa: int):
    return MC.obtener_ordenTerminadas(IdMesa=IdMesa)

def obtener_estado_total():
    return MC.to_dict()

def obtener_estado(IdMesa: int):
    return MC.obtener_orden(IdMesa=IdMesa).to_dict()

def obtener_IdMesas():
    return MC.mesasId()

def generar_orden_comedor(IdMesa: int, detalles: list[Detalles]):
    nuevo_Orden = orden.Ordenes(IdCliente=1, Fecha=datetime.now(), CostoTotal=0.0)
    with Session(db_engine) as session:
        try:
            session.add(nuevo_Orden)
            session.flush()

            if nuevo_Orden.IdOrdenes is None:   
                raise ValueError("La base de datos no generó IdOrden")

            MC.agregar_orden(IdMesa=IdMesa, IdOrden=nuevo_Orden.IdOrdenes)

            monto_total = 0.0
            cantidad_total = 0

            for det in detalles:
                id_platillo = obtener_platillo_id_por_nombre(det.nombre_platillo)

                if id_platillo is None:
                    session.rollback()
                    return None

                costo_por_platillo = float(det.cantidad) * float(det.precio_unitario)
                monto_total += costo_por_platillo
                cantidad_total += det.cantidad

                detalle_nuevo = orden.DetallesOrdenes(
                    IdOrdenes=nuevo_Orden.IdOrdenes,
                    IdPlatillo=id_platillo,
                    CantidadPlatillo=det.cantidad,
                    PrecioUnico=det.precio_unitario,
                    CostoTotal=costo_por_platillo
                )
                session.add(detalle_nuevo)

            nuevo_Orden.CostoTotal = monto_total

            session.commit()
            return nuevo_Orden.model_dump_json()

        except Exception as e:
            session.rollback()
            print(e)
            return None