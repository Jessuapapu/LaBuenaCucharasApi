from src.models import Platillos
from sqlmodel import Session, select
from src.config.database import db_engine


def añadir_platillo(nombre_platillo: str):
    with Session(db_engine) as session:
        try:
            nuevo_platillo = Platillos(NombrePlatillo=nombre_platillo)
            session.add(nuevo_platillo)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def obtener_platillo_id_por_nombre(nombre_platillo: str):
    with Session(db_engine) as session:
        try:
            statement = select(Platillos.IdPlatillo).where(Platillos.NombrePlatillo == nombre_platillo)
            id_platillo = session.exec(statement).first()
            return id_platillo
        except Exception as e:
            raise e
