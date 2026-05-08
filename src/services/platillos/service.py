from src.models import Platillos, CategoriaPlatillos, CatalogoPlatillos
from sqlmodel import Session, select
from src.config.database import db_engine


def obtener_platillos_service():
    with Session(db_engine) as session:
        statement = (
            select(
                Platillos.NombrePlatillo,
                CatalogoPlatillos.NombreCatalogoPlatillo,
            )
            .select_from(Platillos)
            .join(CategoriaPlatillos)
            .join(CatalogoPlatillos)
        )

        platillos_query = session.exec(statement).all()

        if not platillos_query:
            return []

        platillos = []

        for nombre_platillo, nombre_categoria in platillos_query:
            platillos.append(
                {
                    "nombre_platillo": nombre_platillo,
                    "nombre_categoria": nombre_categoria,
                }
            )

        return platillos


def obtener_categorias_platillos_service():
    with Session(db_engine) as session:
        statement = select(CatalogoPlatillos)

        categorias_query = session.exec(statement).all()

        if not categorias_query:
            return []

        categorias = []

        for categoria in categorias_query:
            categorias.append(
                {
                    "id_categoria": categoria.IdCatalogoPlatillo,
                    "nombre_categoria": categoria.NombreCatalogoPlatillo,
                }
            )

        return categorias


def añadir_platillo(nombre_platillo: str, nombre_categoria: str):
    with Session(db_engine) as session:
        try:
            nuevo_platillo = Platillos(NombrePlatillo=nombre_platillo)
            session.add(nuevo_platillo)

            session.flush()

            
            id_categoria = obtener_categoria_id_por_nombre(nombre_categoria)
            print(id_categoria)

            if id_categoria is None:
                return False

            categoria = CategoriaPlatillos(
                IdPlatillo=nuevo_platillo.IdPlatillo, IdCatalogoPlatillo=id_categoria
            )

            session.add(categoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e


def añadir_categoria_platillo(nombre_categoria: str):
    with Session(db_engine) as session:
        try:
            nueva_categoria = CatalogoPlatillos(NombreCatalogoPlatillo=nombre_categoria)
            session.add(nueva_categoria)
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


def obtener_categoria_id_por_nombre(nombre_categoria: str):
    with Session(db_engine) as session:
        try:
            statement = select(CatalogoPlatillos.IdCatalogoPlatillo).where(
                CatalogoPlatillos.NombreCatalogoPlatillo == nombre_categoria
            )
            id_categoria = session.exec(statement).first()
            return id_categoria
        except Exception as e:
            raise e


