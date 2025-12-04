from sqlmodel import Session, select
from src.config.database import db_engine
from src.models.insumos.models import Proveedores
from src.models.insumos.types import TipoDeProveedor


def obtener_proveedores():
    with Session(db_engine) as session:
        statement = select(Proveedores)
        proveedores = session.exec(statement).all()

        return proveedores


def obtener_proveedor_por_nombre(nombre: str):
    with Session(db_engine) as session:
        statement = select(Proveedores).where(Proveedores.NombreProveedor == nombre)
        proveedores = session.exec(statement).first()

        return proveedores


def registrar_proveedor(nombre: str, direccion: str, tipo: TipoDeProveedor):
    nuevo_proveedor = Proveedores(
        NombreProveedor=nombre, Direccion=direccion, Tipo=tipo
    )
    with Session(db_engine) as session:
        session.add(nuevo_proveedor)
        session.commit()

    return nuevo_proveedor
