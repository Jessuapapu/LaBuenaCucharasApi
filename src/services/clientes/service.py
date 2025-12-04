from src.models.clientes.models import Clientes, ClienteCorreo, ClienteTelefono
from sqlmodel import Session, select
from src.config.database import db_engine


def listar_clientes():
    with Session(db_engine) as session:
        statement = (
            select(
                Clientes.NombreCliente,
                Clientes.DireccionCliente,
                ClienteCorreo.CorreoElectronico,
                ClienteTelefono.Telefono,
            )
            .select_from(Clientes)
            .join(ClienteCorreo)
            .join(ClienteTelefono)
        )

        clientes_query = session.exec(statement).all()

        if not clientes_query:
            return None

        clientes = []

        for nombre_cliente, direccion_cliente, correo, telefono in clientes_query:
            clientes.append(
                {
                    "nombre": nombre_cliente,
                    "direccion": direccion_cliente,
                    "correo": correo,
                    "telefono": telefono,
                }
            )

        return clientes


def crear_cliente(
    nombre: str, direccion: str, correo: str | None, telefono: str | None
):
    with Session(db_engine) as session:
        try:
            nuevo_cliente = Clientes(NombreCliente=nombre, DireccionCliente=direccion)
            session.add(nuevo_cliente)
            session.flush()

            if correo is not None and nuevo_cliente.IdCliente is not None:
                nuevo_correo = ClienteCorreo(
                    IdCliente=nuevo_cliente.IdCliente, CorreoElectronico=correo
                )
                session.add(nuevo_correo)

            if telefono is not None and nuevo_cliente.IdCliente is not None:
                nuevo_telefono = ClienteTelefono(
                    IdCliente=nuevo_cliente.IdCliente, Telefono=telefono
                )
                session.add(nuevo_telefono)

            session.commit()

            return nuevo_cliente
        except Exception:
            session.rollback()
            return None


def obtener_id_cliente_por_nombre(nombre: str):
    with Session(db_engine) as session:
        statement = select(Clientes.IdCliente).where(Clientes.NombreCliente == nombre)
        id_cliente = session.exec(statement).first()
        if not id_cliente:
            return None
        return id_cliente
