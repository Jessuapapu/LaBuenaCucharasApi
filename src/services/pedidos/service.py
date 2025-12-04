from src.models.pedidos.models import (
    Pedidos,
    DetallesDePedidos,
    Facturas,
    FacturasPedidos,
)
from src.models.pedidos.types import EstadoPedido, EstadoFactura
from sqlmodel import Session, select
from src.config.database import db_engine
from src.models.platillos.models import Platillos
from src.services.clientes.service import obtener_id_cliente_por_nombre
from src.services.platillos.service import obtener_platillo_id_por_nombre
from src.schemas.pedidos import Detalles
from typing import List
from decimal import Decimal
import datetime


def listar_historial_pedidos(estado: str | None, dia: datetime.date | None):
    with Session(db_engine) as session:
        statement = (
            select(Pedidos, DetallesDePedidos, Platillos, Facturas)
            .select_from(Pedidos)
            .join(DetallesDePedidos)
            .join(Platillos)
            .join(FacturasPedidos)
            .join(Facturas)
        )

        query = session.exec(statement).all()

        historial = []
        for pedido, detalle, platillos, factura in query:
            historial.append(
                {
                    "fecha": pedido.FechaPedido,
                    "estado_pedido": pedido.Estado,
                    "detalle": {
                        "nombre_platillo": platillos.NombrePlatillo,
                        "cantidad": detalle.Cantidad,
                        "precio_unitario": detalle.PrecioUnitario,
                    },
                    "factura": {
                        "fecha_factura": factura.FechaFactura,
                        "monto_total": factura.MontoTotal,
                        "estado_factura": factura.Estado,
                    },
                }
            )

        return historial


def crear_pedido(nombre_cliente: str, fecha: datetime.date, detalle: List[Detalles]):
    id_cliente = obtener_id_cliente_por_nombre(nombre_cliente)

    if id_cliente is None:
        raise ValueError(f"No se pudo obtener un id de cliente con el nombre de cliente {nombre_cliente}")

    nuevo_pedido = Pedidos(IdCliente=id_cliente, FechaPedido=str(fecha), Estado=EstadoPedido.PENDIENTE)

    with Session(db_engine) as session:
        try:
            session.add(nuevo_pedido)

            session.flush()

            if nuevo_pedido.IdPedido is None:
                raise ValueError("La base de datos no generó IdPedido")

            monto_total: Decimal = Decimal("0")
            cantidad_total = 0

            for det in detalle:
                id_platillo = obtener_platillo_id_por_nombre(det.nombre_platillo)

                if id_platillo is None:
                    return None

                detalle_nuevo = DetallesDePedidos(
                    IdPedido=nuevo_pedido.IdPedido,
                    IdPlatillo=id_platillo,
                    Cantidad=det.cantidad,
                    PrecioUnitario=det.precio_unitario,
                )

                session.add(detalle_nuevo)

                monto_total += Decimal(det.cantidad) * Decimal(str(det.precio_unitario))
                cantidad_total += det.cantidad

            factura_nueva = Facturas(
                MontoTotal=monto_total,
                CantidadTotal=cantidad_total,
                Estado=EstadoFactura.GENERADA,
                FechaFactura=str(datetime.date.today()),
            )

            session.add(factura_nueva)

            session.flush()

            if nuevo_pedido.IdPedido is None:
                raise ValueError("La base de datos no generó IdFactura")

            relacion_factura_pedido = FacturasPedidos(
                IdFactura=factura_nueva.IdFactura, IdPedido=nuevo_pedido.IdPedido
            )

            session.add(relacion_factura_pedido)

            session.commit()
            return nuevo_pedido.model_dump_json()
        except Exception as e:
            print(e)
            return None


def pagar_pedido_service(id_pedido: int):
    with Session(db_engine) as session:
        statement = (
            select(Pedidos, Facturas)
            .select_from(Pedidos)
            .join(FacturasPedidos)
            .join(Facturas)
            .where(Pedidos.IdPedido == id_pedido)
        )

        resultado = session.exec(statement).first()

        if not resultado:
            return None

        pedido, factura = resultado

        if (
            pedido.Estado == EstadoPedido.ENTREGADO
            or factura.Estado == EstadoFactura.PAGADA
            or pedido.Estado == EstadoPedido.ANULADO
            or factura.Estado == EstadoFactura.ANULADA
        ):
            return None

        pedido.Estado = EstadoPedido.ENTREGADO
        factura.Estado = EstadoFactura.PAGADA

        session.commit()
        session.refresh(pedido)
        session.refresh(factura)

        return True


def anular_pedido_service(id_pedido: int):
    with Session(db_engine) as session:
        statement = (
            select(Pedidos, Facturas)
            .select_from(Pedidos)
            .join(FacturasPedidos)
            .join(Facturas)
            .where(Pedidos.IdPedido == id_pedido)
        )

        resultado = session.exec(statement).first()

        if not resultado:
            return None

        pedido, factura = resultado

        if (
            pedido.Estado == EstadoPedido.ENTREGADO
            or factura.Estado == EstadoFactura.PAGADA
            or pedido.Estado == EstadoPedido.ANULADO
            or factura.Estado == EstadoFactura.ANULADA
        ):
            return None

        pedido.Estado = EstadoPedido.ANULADO
        factura.Estado = EstadoFactura.ANULADA

        session.commit()
        session.refresh(pedido)
        session.refresh(factura)

        return True
