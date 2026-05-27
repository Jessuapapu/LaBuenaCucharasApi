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

def cerrar_comedor(username: str | None = None):
    if not horaApertura:    
        return False
    from src.services.auditorias.services import registrar_auditoria_comedor

    try:
        # Registrar auditoría mediante el helper central
        user = username if username else "system"
        success = registrar_auditoria_comedor(user, horaApertura, datetime.now())
        logs.add_log("CERRAR COMEDOR", "INFO")
        return success
    except Exception as e:
        print(e)
        return False
        
def guardar_comedor_orden(IdMesa: int, IdOrden: int, username: str | None = None):
    orden = MC.guardar_orden(IdMesa=IdMesa, IdOrden=IdOrden)

    if not orden:
        return False

    with Session(db_engine) as session:
        try: 
            # Usar la función central de auditoría para consistencia
            from src.services.auditorias.services import registrar_auditoria_mesa

            session.add(comedor.Auditoria_Mesas(IdMesa=IdMesa, IdOrden=IdOrden, HoraEntrada=orden.HoraEntrada, HoraSalida=orden.HoraSalida))
            session.commit()

            try:
                registrar_auditoria_mesa(IdMesa, IdOrden, orden.HoraEntrada, orden.HoraSalida)
            except Exception:
                pass

            return True

        except Exception as e:
            session.rollback()
            print(e)
            return False


def obtener_estado_activas():
    return MC.obtener_ordenActivas()

def obtener_estado_terminadas():
    return MC.obtener_ordenTerminadas()

def obtener_estado_orden_mesa_activa(IdMesa: int):
    return MC.obtener_ordenActiva(IdMesa=IdMesa)

def obtener_estado_orden_mesa_terminadas(IdMesa: int):
    return MC.obtener_ordenTerminadasMesa(IdMesa=IdMesa)

def aumentar_mesa():
    return MC.agregar_mesa()

def eliminar_mesa():
    return MC.eliminar_mesa()

def obtener_estado_total():
    return MC.to_dict()

def obtener_estado(IdMesa: int):
    return MC.obtener_orden(IdMesa=IdMesa).to_dict()

def obtener_IdMesas():
    return MC.mesasId()

def generar_orden_comedor(IdMesa: int, detalles: list[Detalles], username: str | None = None):
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
            # Registrar auditoría de orden creada si es posible
            try:
                from src.services.auditorias.services import registrar_auditoria_orden
                from src.models.auditorias.types import TipoDeAccion
                user = username if username else "system"
                registrar_auditoria_orden(user, nuevo_Orden.IdOrdenes, TipoDeAccion.CREAR)
            except Exception:
                pass

            return nuevo_Orden.model_dump_json()

        except Exception as e:
            session.rollback()
            print(e)
            return None