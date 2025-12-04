from src.models import MenuDiario, Platillos, platillos
from sqlmodel import Session, select
from src.config.database import db_engine
from src.routes import menu_diario
from src.services.platillos import service
import datetime


def obtener_historial_menu_service():
    with Session(db_engine) as session:
        statement = select(MenuDiario, Platillos).join(Platillos)

        result = session.exec(statement).all()
        if not result:
            return []

        historial = []
        for menu_diario, platillo in result:
            historial.append(
                {
                    "Fecha": menu_diario.FechaMenu,
                    "NombrePlatillo": platillo.NombrePlatillo,
                }
            )

        return historial


def obtener_menu_dia_service(day: datetime.date):
    with Session(db_engine) as session:
        statement = (
            select(MenuDiario, Platillos)
            .join(Platillos)
            .where(MenuDiario.FechaMenu == day)
        )

        result = session.exec(statement).first()
        if result is None:
            return None

        menu_diario, platillos = result

        return {
            "Fecha": menu_diario.FechaMenu,
            "NombrePlatillo": platillos.NombrePlatillo,
        }


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
