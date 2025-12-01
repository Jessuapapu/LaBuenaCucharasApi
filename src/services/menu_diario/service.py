from csv import Error
from src.models import MenuDiario
from sqlmodel import Session
from src.config.database import db_engine
from src.services.platillos import service
import datetime

def crear_menu_service(day: datetime.date, nombre_platillo: str):
    id_platillo = service.obtener_platillo_id_por_nombre(nombre_platillo)

    if id_platillo is None:
        raise ValueError("El platillo con el nombre ingresado no existe")

    nuevo_menu = MenuDiario(FechaMenu=day, IdPlatillo=id_platillo)
    
    with Session(db_engine) as session:
        try:
            session.add(nuevo_menu)
            session.commit()
        except Exception as e:
            session.rollback()
            return e
