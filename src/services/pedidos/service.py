from src.models.pedidos.models import (
    Pedidos,
    DetallesDePedidos,
    Facturas,
    FacturasPedidos,
)
from src.models.clientes.models import Clientes
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
from sqlalchemy import select as sa_select, func, cast
from sqlalchemy.types import Date


def listar_historial_pedidos():
    with Session(db_engine) as session:
        statement = (
            sa_select(Pedidos, DetallesDePedidos, Platillos, Facturas, Clientes)
            .select_from(Pedidos)
            .join(DetallesDePedidos)
            .join(Platillos)
            .join(FacturasPedidos)
            .join(Facturas)
            .join(Clientes)
            .order_by(Pedidos.FechaPedido)
        )

        query = session.execute(statement).all()

        historial_map: dict[int, dict] = {}

        for pedido, detalle, platillo, factura, cliente in query:
            pid: int = pedido.IdPedido
            if pid not in historial_map:
                historial_map[pid] = {
                    "id_pedido": pid,
                    "fecha": pedido.FechaPedido,
                    "estado_pedido": pedido.Estado,
                    "detalles": [],
                    "factura": {
                        "fecha_factura": factura.FechaFactura,
                        "monto_total": factura.MontoTotal,
                        "estado_factura": factura.Estado,
                    },
                    "cliente": {
                        "nombre_cliente": cliente.NombreCliente,
                        "direccion_cliente": cliente.DireccionCliente,
                    },
                }

            historial_map[pid]["detalles"].append(
                {
                    "nombre_platillo": platillo.NombrePlatillo,
                    "cantidad": detalle.Cantidad,
                    "precio_unitario": detalle.PrecioUnitario,
                }
            )

        historial = list(historial_map.values())
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


def actualizar_pedido(
    id_pedido: int, nombre_cliente: str, estado: EstadoPedido, detalles: List[Detalles]
):
    with Session(db_engine) as session:
        statement = (
            select(DetallesDePedidos)
            .select_from(Pedidos)
            .join(DetallesDePedidos)
            .where(Pedidos.IdPedido == id_pedido)
        )

        detalles_actualizar = session.exec(statement).all()

        if not detalles_actualizar:
            return None

        stmt_pedido_factura = (
            select(Pedidos, Facturas)
            .select_from(Pedidos)
            .join(FacturasPedidos)
            .join(Facturas)
            .where(Pedidos.IdPedido == id_pedido)
        )
        resultado = session.exec(stmt_pedido_factura).first()
        if not resultado:
            return None

        pedido, factura = resultado

        if (
            pedido.Estado == EstadoPedido.ANULADO
            or factura.Estado == EstadoFactura.ANULADA
        ):
            return None

        nuevo_id_cliente = obtener_id_cliente_por_nombre(nombre_cliente)
        if nuevo_id_cliente is None:
            return None

        pedido.IdCliente = nuevo_id_cliente
        pedido.Estado = estado

        for d in detalles_actualizar:
            session.delete(d)

        monto_total = Decimal("0")
        cantidad_total = 0

        for det in detalles:
            id_platillo = obtener_platillo_id_por_nombre(det.nombre_platillo)
            if id_platillo is None:
                session.rollback()
                return None

            session.add(
                DetallesDePedidos(
                    IdPedido=id_pedido,
                    IdPlatillo=id_platillo,
                    Cantidad=det.cantidad,
                    PrecioUnitario=det.precio_unitario,
                )
            )

            monto_total += Decimal(det.cantidad) * Decimal(str(det.precio_unitario))
            cantidad_total += det.cantidad

        factura.MontoTotal = monto_total
        factura.CantidadTotal = cantidad_total
        if estado == EstadoPedido.ENTREGADO:
            factura.Estado = EstadoFactura.PAGADA

        if estado == EstadoPedido.PENDIENTE:
            factura.Estado = EstadoFactura.GENERADA

        if estado == EstadoPedido.ANULADO:
            factura.Estado = EstadoFactura.ANULADA

        factura.FechaFactura = str(datetime.date.today())

        session.commit()
        session.refresh(pedido)
        session.refresh(factura)

        return True


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

        print(resultado)

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


def conteo_pedidos_semanal():
    with Session(db_engine) as session:
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        statement = (
            select(Pedidos.FechaPedido)
            .select_from(Pedidos)
            .where(cast(Pedidos.FechaPedido, Date).between(start_of_week, end_of_week))
        )

        resultados = session.execute(statement).all()

        # Mapa de nombres de días en español
        dias_es = [
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        ]

        # Conteo por nombre de día
        conteo_por_dia: dict[str, int] = {dia: 0 for dia in dias_es}

        for (fecha_pedido_raw,) in resultados:
            # Normalizar a date
            if isinstance(fecha_pedido_raw, datetime.date):
                fecha_pedido = fecha_pedido_raw
            else:
                # Asumir formato ISO (YYYY-MM-DD)
                fecha_pedido = datetime.date.fromisoformat(str(fecha_pedido_raw))

            nombre_dia = dias_es[fecha_pedido.weekday()]
            conteo_por_dia[nombre_dia] += 1

        # Construir la salida ordenada de lunes a domingo
        conteo_semanal = [
            {"dia": dia, "conteo": conteo_por_dia[dia]} for dia in dias_es
        ]

        return conteo_semanal


def obtener_facturas_pedidos():
    with Session(db_engine) as session:
        statement = (
            sa_select(Pedidos, Facturas, Clientes)
            .select_from(Pedidos)
            .join(FacturasPedidos)
            .join(Facturas)
            .join(Clientes)
            .order_by(Pedidos.FechaPedido)
        )

        query = session.execute(statement).all()

        facturas_list = []

        for pedido, factura, cliente in query:
            facturas_list.append(
                {
                    "id_pedido": pedido.IdPedido,
                    "monto_total": factura.MontoTotal,
                    "cantidad_total": factura.CantidadTotal,
                    "estado_factura": factura.Estado,
                    "fecha_factura": factura.FechaFactura,
                    "cliente": {
                        "nombre_cliente": cliente.NombreCliente,
                        "direccion_cliente": cliente.DireccionCliente,
                    },
                }
            )

        return facturas_list


def obtener_contador_platillos():
    with Session(db_engine) as session:
        statement = (
            select(
                Platillos.NombrePlatillo,
                func.SUM(DetallesDePedidos.Cantidad).label("total_vendido"),
            )
            .select_from(DetallesDePedidos)
            .join(Platillos)
            .group_by(Platillos.NombrePlatillo)
            .order_by(func.SUM(DetallesDePedidos.Cantidad).desc())
        )

        query = session.exec(statement).all()

        platillos_populares = []

        for nombre_platillo, total_vendido in query:
            platillos_populares.append(
                {
                    "nombre_platillo": nombre_platillo,
                    "total_vendido": total_vendido,
                }
            )

        return platillos_populares
