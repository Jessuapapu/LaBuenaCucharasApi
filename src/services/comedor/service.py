from src.models.comedor import models as comedor
from sqlmodel import Session, select
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

    with Session(db_engine) as session:
        try: 
            auditoria_nueva = comedor.Auditoria_Mesas(IdMesa=IdMesa, IdOrden=IdOrden, HoraEntrada=datetime.now())
            session.add(auditoria_nueva)
            session.commit()

        except Exception as e:
            session.rollback()
            print(e)
            return None

def abrir_comedor():
    global horaApertura 
    horaApertura = datetime.now()
    logs.add_log("APERTURA COMEDOR", "INFO")
    return

def cerrar_comedor():
    with Session(db_engine) as session:
        try: 
            auditoria_nueva = comedor.Auditoria_Comedor(HoraApertura=horaApertura, HoraCerrar=datetime.now())
            logs.add_log("CERRAR COMEDOR", "INFO")
            session.add(auditoria_nueva)
            session.commit()

        except Exception as e:
            session.rollback()
            print(e)
            return None


