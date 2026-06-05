from src.models.pedidos.models import (
    Pedidos
)

from src.models.facturas.models import (
    Facturas, FacturasOrdenes
)

from src.models.ordenes.models import Ordenes, DetallesOrdenes
from src.models.ordenes.types import EstadoOrden
from fastapi import HTTPException
from src.models.clientes.models import Clientes, ClienteDireccion
from src.models.pedidos.types import EstadoPedido
from src.models.facturas.types import EstadoFactura
from sqlmodel import Session, select
from src.config.database import db_engine
from src.models.platillos.models import Platillos
from src.services.clientes.service import obtener_id_cliente_por_nombre
from src.services.platillos.service import obtener_platillo_id_por_nombre
from src.schemas.pedidos import Detalles
from typing import List
from decimal import Decimal
import datetime
from sqlalchemy import select as func, cast
from sqlalchemy.types import Date

from sqlmodel import Session
from sqlalchemy import text
from src.config.database import db_engine
from src.services.auditorias.services import registrar_auditoria_orden
from src.models.auditorias.types import TipoDeAccion

def obtener_orden(IdOrden: int):
    with Session(db_engine) as session:
        try:
            query = select(Ordenes).select_from(Ordenes).where(Ordenes.IdOrdenes == IdOrden)
            orden = session.exec(query).first()

            return orden    
        
        except:
            return None
        
def listar_historial_Ordenes(
    id_orden: int | None = None, 
    pagina: int = 1, 
    rows: int = 10, 
    todo: int = 0,
    NombreCliente: str = None
):
    id_cliente = obtener_id_cliente_por_nombre(NombreCliente)
    with Session(db_engine) as session:
  
        statement = text("""
            EXEC MostrarOrdenes 
                @IdOrden = :id_orden, 
                @Pagina = :pagina, 
                @Rows = :rows, 
                @Todo = :todo,
                @IdCliente = :id_cliente
        """)

        parametros = {
            "id_orden": id_orden,
            "pagina": pagina,
            "rows": rows,
            "todo": todo,
            "id_cliente": id_cliente
        }

        resultados = session.exec(statement, params=parametros).all()

        historial = []
        
        for row in resultados:
            historial.append({
                "id_pedido": row.IdOrdenes,
                "monto_total": row.MONTOTOTAL,
                "fecha": row.Fecha,
                "cliente" : {
                    "nombre_cliente": row.NombreCliente,
                    "direccion_cliente" : row.dirreccion
                },
                "estado_pedido": row.Estado,
                "detalles": detalle_Ordenes(id_orden=row.IdOrdenes)

            })

        return historial

def detalle_Ordenes(
    id_orden: int | None = None,
    id_cliente: int | None = None
):
    if id_orden is None and id_cliente is None:
        raise HTTPException(
            status_code=400, 
            detail="Error: Debe ingresar al menos un identificador (IdOrden o IdCliente)."
        )

    with Session(db_engine) as session:
        statement = text("EXEC MostrarDetalles  @Id = :id_orden,     @IdCliente = :id_cliente")
        
        parametros = {
            "id_orden": id_orden,
            "id_cliente": id_cliente
        }
        
        resultados = session.exec(statement, params=parametros).all()

        detalles_lista = []
        
        for row in resultados:
            detalles_lista.append({
                "id_orden": row.IdOrdenes,
                "nombre_platillo": row.NombrePlatillo,
                "cantidad": row.CantidadPlatillo,
                "precio_unitario": row.PrecioUnico,
            })

        return detalles_lista

def crear_orden( fecha: datetime.date, detalle: List[Detalles], Id_cliente: int | None = None, nombre_cliente: str | None = None, username: str | None = None):
    

    id_cliente = Id_cliente if Id_cliente else obtener_id_cliente_por_nombre(nombre_cliente)

    if id_cliente is None:
        raise ValueError(f"No se pudo obtener un id de cliente con el nombre de cliente {nombre_cliente}")

    nuevo_Orden = Ordenes(IdCliente=id_cliente, FechaPedido=str(fecha), CostoTotal=0.0)

    with Session(db_engine) as session:
        try:
            session.add(nuevo_Orden)
            session.flush()

            if nuevo_Orden.IdOrdenes is None:   
                raise ValueError("La base de datos no generó IdPedido")

            monto_total = 0.0
            cantidad_total = 0

            for det in detalle:
                id_platillo = obtener_platillo_id_por_nombre(det.nombre_platillo)

                if id_platillo is None:
                    session.rollback()
                    return None

                costo_por_platillo = float(det.cantidad) * float(det.precio_unitario)
                monto_total += costo_por_platillo
                cantidad_total += det.cantidad

                detalle_nuevo = DetallesOrdenes(
                    IdOrdenes=nuevo_Orden.IdOrdenes,
                    IdPlatillo=id_platillo,
                    CantidadPlatillo=det.cantidad,
                    PrecioUnico=det.precio_unitario,
                    CostoTotal=costo_por_platillo
                )
                session.add(detalle_nuevo)


            nuevo_Orden.CostoTotal = monto_total

            session.commit()
            session.refresh(nuevo_Orden)
            # Auditoría: creación de orden
            if username and nuevo_Orden.IdOrdenes is not None:
                try:
                    registrar_auditoria_orden(username, nuevo_Orden.IdOrdenes, TipoDeAccion.CREAR)
                except Exception:
                    pass

            return nuevo_Orden

        except Exception as e:
            session.rollback()
            print(e)
            return None


def actualizar_ordenes(
    id_pedido: int, estado: EstadoOrden, detalles: List[Detalles], Id_cliente: int | None = None, nombre_cliente: str | None = None, username: str | None = None
):
    with Session(db_engine) as session:
        statement = (
            select(DetallesOrdenes)
            .join(Ordenes, Ordenes.IdOrdenes == DetallesOrdenes.IdOrdenes)
            .where(Ordenes.IdOrdenes == id_pedido)
        )

        stmt_orden = (
            select(Ordenes)
            .where(Ordenes.IdOrdenes == id_pedido)
        )

        detalles_actualizar = session.exec(statement).all()
        resultado = session.exec(stmt_orden).first()
        nuevo_id_cliente = Id_cliente if Id_cliente else obtener_id_cliente_por_nombre(nombre_cliente)
        
        if not resultado or not nuevo_id_cliente:
            return None

        pedido = resultado

        if pedido.Estado == EstadoOrden.ANULADO:
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
            
            costo_fila = Decimal(det.cantidad) * Decimal(str(det.precio_unitario))

            session.add(
                DetallesOrdenes(
                    IdOrdenes=id_pedido,
                    IdPlatillo=id_platillo,
                    CantidadPlatillo=det.cantidad,
                    PrecioUnico=det.precio_unitario,
                    CostoTotal=costo_fila
                )
            )

            monto_total += costo_fila
            cantidad_total += det.cantidad
        
        if estado in EstadoOrden.ANULADO:
            statement = text("EXEC ActualizarPagos  @IdOrden = :idOrden")

            session.exec(statement=statement, params={'idOrden': pedido.IdOrdenes})

        session.commit()
        session.refresh(pedido)

        # Auditoría: actualización de orden
        if username:
            try:
                registrar_auditoria_orden(username, id_pedido, TipoDeAccion.ACTUALIZAR)
            except Exception:
                pass

        return True


def pagar_orden_service(id_pedido: int):
    with Session(db_engine) as session:
        statement = (
            select(Ordenes)
            .select_from(Ordenes)
            .where(Ordenes.IdOrdenes == id_pedido)
        )

        resultado = session.exec(statement).first()


        if not resultado:
            return None

        pedido = resultado

        if (
            pedido.Estado == EstadoPedido.ENTREGADO
            or pedido.Estado == EstadoPedido.ANULADO
        ):
            return None

        pedido.Estado = EstadoPedido.ENTREGADO     

        session.commit()
        session.refresh(pedido)

        return True


def anular_orden_service(id_pedido: int, username: str | None = None):
    with Session(db_engine) as session:
        statement = (
            select(Ordenes, Facturas)
            .select_from(Ordenes)
            .join(Facturas)
            .where(Ordenes.IdOrdenes == id_pedido)
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

        # Auditoría: eliminación/anulación de orden
        if username:
            try:
                registrar_auditoria_orden(username, id_pedido, TipoDeAccion.ELIMINAR)
            except Exception:
                pass

        return True


def conteo_Ordenes_semanal():
    with Session(db_engine) as session:
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        statement = (
            select(Ordenes.Fecha)
            .select_from(Ordenes)
            .where(cast(Ordenes.Fecha, Date).between(start_of_week, end_of_week))
        )

        resultados = session.exec(statement).all()

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

        for (fecha_pedido_raw) in resultados:
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


def obtener_contador_platillos():
    with Session(db_engine) as session:
        statement = (
            select(
                Platillos.NombrePlatillo,
                func.SUM(DetallesOrdenes.CantidadPlatillo).label("total_vendido"),
            )
            .select_from(DetallesOrdenes)
            .join(Platillos)
            .group_by(Platillos.NombrePlatillo)
            .order_by(func.SUM(DetallesOrdenes.CantidadPlatillo).desc())
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
