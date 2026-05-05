from src.models.comedor import models as comedor
from sqlmodel import Session
from src.config.database import db_engine
from datetime import datetime
MC = comedor.MonitorComedor()
horaApertura = None
horaCerrar = None

from logs import logsApp
logs = logsApp.Logs()

def agregar_orden_comedor(IdMesa: int, IdOrden: int):
    
    if IdMesa > MC.MaxIdGenerado:
        return False
    
    MC.agregar_orden(IdMesa=IdMesa, IdOrden=IdOrden)

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
    orden = MC.obtener_orden(IdMesa=IdMesa, IdOrden=IdOrden)

    if not orden:
        return {"msj": F"ERROR NO EN CONTRADO LA ORDEN EN ASOCIADA A LA MESA {IdOrden}", "ERROR": 404}
    
    orden.HoraSalida = datetime.now()

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
            return None


