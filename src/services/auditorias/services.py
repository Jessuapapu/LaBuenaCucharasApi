from datetime import datetime
from sqlmodel import Session

from src.config.database import db_engine
from src.models.auditorias.models import *

def registrar_auditoria_mesa(id_mesa: int, id_orden: int, hora_entrada: datetime, hora_salida: datetime = None) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Mesas(
                IdMesa=id_mesa, 
                IdOrden=id_orden, 
                HoraEntrada=hora_entrada, 
                HoraSalida=hora_salida
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de mesa: {e}")
            return False

def registrar_auditoria_comedor(username: str, hora_apertura: datetime, hora_cerrar: datetime) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Comedor(
                Username=username, 
                HoraApertura=hora_apertura, 
                HoraCerrar=hora_cerrar
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de comedor: {e}")
            return False
        
def registrar_auditoria_Caja(username: str, hora_apertura: datetime, hora_cerrar: datetime) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Caja(
                Username=username, 
                HoraApertura=hora_apertura, 
                HoraCerrar=hora_cerrar
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de comedor: {e}")
            return False