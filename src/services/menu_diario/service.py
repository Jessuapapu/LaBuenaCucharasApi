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
                    "id": menu_diario.IdMenu,
                    "Fecha": menu_diario.Fecha,
                    "NombrePlatillo": platillo.NombrePlatillo,
                }
            )

        return historial


def obtener_menu_dia_service(day: datetime.date):
    with Session(db_engine) as session:
        statement = (
            select(MenuDiario, Platillos)
            .join(Platillos)
            .where(MenuDiario.Fecha == day)
        )

        result = session.exec(statement).first()
        if result is None:
            return None

        menu_diario, platillos = result

        return {
            "id": menu_diario.IdMenu,
            "Fecha": menu_diario.Fecha,
            "NombrePlatillo": platillos.NombrePlatillo,
        }


def crear_menu_service(day: datetime.date, nombre_platillo: str):
    id_platillo = service.obtener_platillo_id_por_nombre(nombre_platillo)

    if id_platillo is None:
        raise ValueError("El platillo con el nombre ingresado no existe")

    nuevo_menu = MenuDiario(Fecha=day, IdPlatillo=id_platillo)

    with Session(db_engine) as session:
        try:
            session.add(nuevo_menu)
            session.commit()
        except Exception as e:
            session.rollback()
            return e


def editar_menu_service(id_menu, nombre_platillo: str):
    id_platillo = service.obtener_platillo_id_por_nombre(nombre_platillo)

    if id_platillo is None:
        raise ValueError("El platillo con el nombre ingresado no existe")

    with Session(db_engine) as session:
        statement = select(MenuDiario).where(MenuDiario.IdMenu == id_menu)
        menu_a_editar = session.exec(statement).first()

        if menu_a_editar is None:
            raise ValueError("No existe el menu con el Id ingresado")

        menu_a_editar.IdPlatillo = id_platillo

        try:
            session.add(menu_a_editar)
            session.commit()
        except Exception as e:
            session.rollback()
            return e
