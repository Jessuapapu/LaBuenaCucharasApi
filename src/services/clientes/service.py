import datetime
from src.models.clientes.models import (
    Clientes,
    ClienteCorreo,
    ClienteTelefono,
    ClienteDireccion,
    Contrato
)
from src.models.clientes.types import EstadoContrato
from sqlmodel import Session, select, text
from src.config.database import db_engine
from src.services.auditorias.services import registrar_auditoria_cliente
from src.models.auditorias.types import TipoDeAccion


def listar_clientes():
    with Session(db_engine) as session:
        statement = (
            select(
                Clientes.IdCliente,
                Clientes.NombreCliente,
                ClienteCorreo.CorreoElectronico,
                ClienteDireccion.Dirreccion,
                ClienteTelefono.Telefono,
            )
            .select_from(Clientes)
            .join(ClienteCorreo)
            .join(ClienteTelefono)
            .join(ClienteDireccion)
        )

        clientes_query = session.exec(statement).all()

        if not clientes_query:
            return None

        clientes = []

        for id_cliente, nombre_cliente, correo, direccion_cliente, telefono in clientes_query:
            clientes.append(
                {
                    "IdCliente": id_cliente,
                    "nombre": nombre_cliente,
                    "direccion": direccion_cliente,
                    "correo": correo,
                    "telefono": telefono
                }
            )

        return clientes


def crear_cliente(
    nombre: str, direccion: str, correo: str | None, telefono: str | None, username: str | None = None
):
    with Session(db_engine) as session:
        try:
            nuevo_cliente = Clientes(NombreCliente=nombre)
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

            if direccion is not None and nuevo_cliente.IdCliente is not None:
                nuevo_direccion = ClienteDireccion(IdCliente= nuevo_cliente.IdCliente, Dirreccion= direccion)
                session.add(nuevo_direccion)
            session.commit()

            # Registrar auditoría si se proporcionó username
            if username and nuevo_cliente.IdCliente is not None:
                try:
                    registrar_auditoria_cliente(username, nuevo_cliente.IdCliente, TipoDeAccion.CREAR)
                except Exception:
                    pass

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


def obtener_contratos_clientes(
    id_cliente: int | None = None,
    fecha_inicio: datetime.datetime | None = None,
    fecha_vencimiento: datetime.datetime | None = None,
    presupuesto: float | None = None,
    presupuesto_fin: float | None = None
) -> list:
    with Session(db_engine) as session:
        query = text("""
            EXEC MostrarContratos 
                @IdCliente = :id_cliente,
                @FechaInicio = :fecha_inicio,
                @FechaVencimiento = :fecha_vencimiento,
                @Presupuesto = :presupuesto,
                @PresupuestoFin = :presupuesto_fin
        """)
        
        valores_parametros = {
            "id_cliente": id_cliente,
            "fecha_inicio": fecha_inicio,
            "fecha_vencimiento": fecha_vencimiento,
            "presupuesto": presupuesto,
            "presupuesto_fin": presupuesto_fin
        }
        resultados = session.exec(query, params=valores_parametros).mappings().all()
        
        return [dict(row) for row in resultados]


def registrar_contrato_cliente(
    nombre_cliente: str,
    numero_contrato: int,
    fecha_inicio: datetime.datetime,
    fecha_fin: datetime.datetime,
    presupuesto: float,
    username: str | None = None,
):
    id_cliente = obtener_id_cliente_por_nombre(nombre_cliente)
    if id_cliente is None:
        raise ValueError("Cliente no encontrado")

    nuevo_contrato = Contrato(
        IdCliente=id_cliente,
        NumeroContrato=numero_contrato,
        FechaInicio=fecha_inicio,
        FechaVencimiento=fecha_fin,
        Presupuesto=presupuesto,
        Estado=EstadoContrato.ACTIVO,
    )

    with Session(db_engine) as session:
        try:
            session.add(nuevo_contrato)
            session.commit()
            # Auditoría de creación de cliente/contrato
            if username and nuevo_contrato.IdCliente is not None:
                try:
                    registrar_auditoria_cliente(username, nuevo_contrato.IdCliente, TipoDeAccion.CREAR)
                except Exception:
                    pass
        except Exception as e:
            session.rollback()
            raise e

    return nuevo_contrato


def actualizar_estado_contrato(numero_contrato: int, nuevo_estado: EstadoContrato, username: str | None = None):
    with Session(db_engine) as session:
        statement = select(Contrato).where(Contrato.NumeroContrato == numero_contrato)
        contrato = session.exec(statement).first()

        if not contrato:
            raise ValueError("Contrato no encontrado")

        contrato.Estado = nuevo_estado

        try:
            session.add(contrato)
            session.commit()
            # Auditoría de actualización
            if username and contrato.IdCliente is not None:
                try:
                    registrar_auditoria_cliente(username, contrato.IdCliente, TipoDeAccion.ACTUALIZAR)
                except Exception:
                    pass
        except Exception as e:
            session.rollback()
            raise e

    return contrato
