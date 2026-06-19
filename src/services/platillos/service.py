from src.models import Platillos, CategoriaPlatillos, CatalogoPlatillos
from sqlmodel import Session, select, desc
from src.config.database import db_engine
from src.services.auditorias.services import registrar_auditoria_platillo
from src.models.auditorias.types import TipoDeAccion


def obtener_platillos_service():
    with Session(db_engine) as session:
        statement = (
            select(
                Platillos.IdPlatillo,
                Platillos.NombrePlatillo,
                CatalogoPlatillos.NombreCatalogoPlatillo,
            )
            .select_from(Platillos)
            .join(CategoriaPlatillos)
            .join(CatalogoPlatillos)
            .order_by(desc(Platillos.IdPlatillo))
        )

        platillos_query = session.exec(statement).all()

        if not platillos_query:
            return []

        platillos = []

        for id_platillo, nombre_platillo, nombre_categoria in platillos_query:
            platillos.append(
                {
                    "id_platillo": id_platillo,
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


def añadir_platillo(nombre_platillo: str, nombre_categoria: str, username: str | None = None):
    # HP DAVID NO LO TENIA VALIDADO
    if obtener_platillo_id_por_nombre(nombre_platillo):
        return False

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
            # Auditoría: creación de platillo
            if username and nuevo_platillo.IdPlatillo is not None:
                try:
                    registrar_auditoria_platillo(username, nuevo_platillo.IdPlatillo, TipoDeAccion.CREAR)
                except Exception:
                    pass

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


def actualizar_platillo_por_nombre(nombre_actual: str, nuevo_nombre: str | None = None, nombre_categoria: str | None = None, username: str | None = None):
    """
    Actualiza un platillo identificado por su nombre actual.
    - Puede actualizar el nombre del platillo y/o su categoria.
    - Devuelve True si se actualiza correctamente, False si no existe o falla la categoria.
    """

    with Session(db_engine) as session:
        try:
            statement = select(Platillos).where(Platillos.NombrePlatillo == nombre_actual)
            platillo = session.exec(statement).first()

            if not platillo:
                return False

            # actualizar nombre si se proporciono uno nuevo
            if nuevo_nombre and nuevo_nombre != platillo.NombrePlatillo:
                platillo.NombrePlatillo = nuevo_nombre

            # actualizar categoria si se proporciono
            if nombre_categoria:
                id_categoria = obtener_categoria_id_por_nombre(nombre_categoria)
                if id_categoria is None:
                    return False

                # buscar relacion existente
                stmt_cat = select(CategoriaPlatillos).where(CategoriaPlatillos.IdPlatillo == platillo.IdPlatillo)
                relacion = session.exec(stmt_cat).first()
                if relacion:
                    relacion.IdCatalogoPlatillo = id_categoria
                    session.add(relacion)
                else:
                    nueva_rel = CategoriaPlatillos(IdPlatillo=platillo.IdPlatillo, IdCatalogoPlatillo=id_categoria)
                    session.add(nueva_rel)

            session.add(platillo)
            session.commit()

            # auditoria
            if username and hasattr(platillo, 'IdPlatillo') and platillo.IdPlatillo is not None:
                try:
                    registrar_auditoria_platillo(username, platillo.IdPlatillo, TipoDeAccion.ACTUALIZAR)
                except Exception:
                    pass

            return True
        except Exception as e:
            session.rollback()
            raise e


def relacion_platillo_ingredientes():
    pass