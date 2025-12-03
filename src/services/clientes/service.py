from src.models.clientes.models import Clientes
from sqlmodel import Session, select
from src.config.database import db_engine

def crear_cliente(nombre: str, direccion: str):
    nuevo_cliente = Clientes(NombreCliente=nombre, DireccionCliente=direccion)
    
    with Session(db_engine) as session:
        try:
            session.add(nuevo_cliente)
            session.commit()
            return nuevo_cliente
        except Exception as e:
            session.rollback()
            return e

def obtener_id_cliente_por_nombre(nombre: str):
    with Session(db_engine) as session:
        statement = select(Clientes.IdCliente).where(Clientes.NombreCliente == nombre)
        id_cliente = session.exec(statement).first()
        if not id_cliente:
            return None
        return id_cliente