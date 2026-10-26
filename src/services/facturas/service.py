from fastapi import HTTPException

from sqlmodel import Session, col, select
from src.config.database import db_engine
from src.schemas.facturas import facturaIn
import datetime

from sqlmodel import Session
from sqlalchemy import text
from src.config.database import db_engine

from src.models.facturas.models import Facturas, FacturasOrdenes
from src.models.ordenes.models import Ordenes
from decimal import Decimal
from src.models.clientes.models import Clientes
from src.models.ordenes.types import EstadoOrden
from src.models.facturas.types import EstadoFactura


def obtener_facturas_ordenes(
    Id_Facturas: int | None = None,
    id_cliente: int | None = None,
    id_orden: int | None = None,
    fecha_inicio: datetime.datetime | None = None,
    fecha_fin: datetime.datetime | None = None,
    monto: float | None = None,
    monto_fin: float | None = None,
    cantidad_total: int | None = None,
    pagina: int = 1, 
    rows: int = 10, 
    todo: int = 0
) -> list:
    
    with Session(db_engine) as session:
        try:
            query = text("""
                EXEC MostrarFacturas 
                    @IdFactura = :id_factura,
                    @IdCliente = :id_cliente,
                    @IdOrden = :id_orden,
                    @FechaInicio = :fecha_inicio,
                    @FechaFin = :fecha_fin,
                    @Monto = :monto,
                    @MontoFin = :monto_fin,
                    @CantidadTotal = :cantidad_total,
                    @Pagina = :pagina, 
                    @Rows = :rows, 
                    @Todo = :todo
            """)

            valores = {
                "id_factura": Id_Facturas,
                "id_cliente": id_cliente,
                "id_orden": id_orden,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "monto": monto,
                "monto_fin": monto_fin,
                "cantidad_total": cantidad_total,
                "pagina": pagina,
                "rows": rows,
                "todo": todo
            }

            resultados = session.exec(query, params=valores).mappings().all()

            facturas_list = []
            for row in resultados:
                facturas_list.append({
                    "Id_factura": row.get("IdFactura"),
                    "monto_total": row.get("MontoTotal"),
                    "cantidad_total": row.get("CantidadTotal"),
                    "estado_factura": row.get("Estado"),
                    "fecha_factura": row.get("Fecha"),
                    "nombre_cliente": row.get("NombreCliente"),
                    
                })
        except:
            HTTPException(404,{"NO ENCONTRADO"})
            return None

        return facturas_list

# Búsqueda de órdenes a facturar (la que usa el modal de facturación)

def listar_ordenes_facturables(nombre_cliente: str, limite: int = 50) -> list[dict]:
    """
    Órdenes activas de clientes cuyo nombre contiene `nombre_cliente`.
    Activa = no anulada y todavía sin factura (FacturasOrdenes.IdOrdenes es unique).
    """
    nombre = (nombre_cliente or "").strip()
    if not nombre:
        return []
 
    with Session(db_engine) as session:
        stmt = (
            select(
                Ordenes.IdOrdenes,
                Ordenes.IdCliente,
                Ordenes.CostoTotal,
                Ordenes.Fecha,
                Clientes.NombreCliente,
            )
            .select_from(Ordenes)
            .join(Clientes, Clientes.IdCliente == Ordenes.IdCliente)
            .outerjoin(FacturasOrdenes, FacturasOrdenes.IdOrdenes == Ordenes.IdOrdenes)
            .where(
                col(Clientes.NombreCliente).ilike(f"%{nombre}%"),
                col(FacturasOrdenes.IdOrdenes).is_(None),   # aún sin factura
                Ordenes.Estado != EstadoOrden.ANULADO,
            )
            .order_by(col(Ordenes.Fecha).desc())
            .limit(limite)
        )
 
        filas = session.exec(stmt).all()
 
        return [
            {
                "id_orden": f.IdOrdenes,
                "id_cliente": f.IdCliente,
                "nombre_cliente": f.NombreCliente,
                "monto_total": float(f.CostoTotal or 0),
                "fecha": f.Fecha,
            }
            for f in filas
        ]

def _ids_ordenes(payload: facturaIn) -> list[int]:
    ids = [d.IdOrden for d in payload.detalles]
    if not ids:
        raise HTTPException(status_code=400, detail="Debe incluir al menos una orden")
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=400, detail="Hay órdenes repetidas en la factura")
    return ids
 
#Validaciones paar crear y actualizar, se que ya existen, pero siguen dando fallo y no quiero tocar eso todavia xd
def _validar_ordenes_facturables(
    session: Session, ids_ordenes: list[int], id_factura_actual: int | None = None
) -> dict[int, Ordenes]:
    ordenes = session.exec(
        select(Ordenes).where(col(Ordenes.IdOrdenes).in_(ids_ordenes))
    ).all()
    por_id = {o.IdOrdenes: o for o in ordenes}
 
    faltantes = [i for i in ids_ordenes if i not in por_id]
    if faltantes:
        raise HTTPException(status_code=404, detail=f"Órdenes no encontradas: {faltantes}")
 
    anuladas = [i for i, o in por_id.items() if o.Estado == EstadoOrden.ANULADO]
    if anuladas:
        raise HTTPException(status_code=409, detail=f"Órdenes anuladas: {anuladas}")
 
    # Una orden solo puede estar en una factura (IdOrdenes es unique)
    stmt = select(FacturasOrdenes.IdOrdenes).where(
        col(FacturasOrdenes.IdOrdenes).in_(ids_ordenes)
    )
    if id_factura_actual is not None:
        stmt = stmt.where(FacturasOrdenes.IdFactura != id_factura_actual)
    ya_facturadas = session.exec(stmt).all()
    if ya_facturadas:
        raise HTTPException(
            status_code=409, detail=f"Órdenes ya facturadas: {sorted(ya_facturadas)}"
        )



def crear_facturas(
    payLoadDetalles: facturaIn, username: str | None = None
)-> int:
    ids_ordenes = _ids_ordenes(payLoadDetalles)
    json_string = payLoadDetalles.model_dump_json()

    with Session(db_engine) as session:
        _validar_ordenes_facturables(session, ids_ordenes)
        try:

            query = text("EXEC GenerarFactura @PayloadJson = :json_data")
            id_generado = session.exec(query, {"json_data": json_string}).scalar()
            
            session.commit()


            return id_generado
            
        except Exception as e:
            print(f"Error al ejecutar el PA sp_GenerarFactura: {e}")
            return False
    return True


def actualizar_factura(IdFactura: int, payLoadDetalles: facturaIn, username: str | None = None)-> bool:
    ids_ordenes = _ids_ordenes(payLoadDetalles)
    with Session(db_engine) as session:
        factura = session.get(Facturas, IdFactura)
        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        if factura.Estado == EstadoFactura.ANULADA:
            raise HTTPException(status_code=409, detail="No se puede modificar una factura anulada")
 
        ordenes = _validar_ordenes_facturables(
            session, ids_ordenes, id_factura_actual=IdFactura
        )
        try:
            factura = session.get(Facturas, IdFactura)
            if not factura:
                return False

            # Calcular monto total y cantidad total a partir de las órdenes
            monto_total = Decimal("0")
            cantidad_total = 0

            ids_ordenes = [d.IdOrden for d in payLoadDetalles.detalles]

            for id_orden in ids_ordenes:
                orden = session.get(Ordenes, id_orden)
                if not orden:
                    # orden inexistente -> rollback y error
                    session.rollback()
                    return False
                monto_total += Decimal(str(orden.CostoTotal)) if orden.CostoTotal is not None else Decimal("0")
                cantidad_total += 1

            # Actualizar datos de la factura
            factura.MontoTotal = monto_total
            factura.CantidadTotal = cantidad_total
            factura.Fecha = payLoadDetalles.fecha
            factura.Estado = payLoadDetalles.Estado

            # Eliminar relaciones previas
            session.exec(
                "DELETE FROM facturasordenes WHERE IdFactura = :id_factura",
                {"id_factura": IdFactura},
            )

            # Agregar nuevas relaciones
            for id_orden in ids_ordenes:
                rel = FacturasOrdenes(IdFactura=IdFactura, IdOrdenes=id_orden)
                session.add(rel)

            session.add(factura)
            session.commit()


            return True
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar factura: {e}")
            return False
        

def obtener_detalle(IdFactura: int):
    with Session(db_engine) as session:
        query = text("""
        EXEC MostrarDetalleFactura 
            @Id = :Id
        """)
        params = {
        "Id": IdFactura
        }
        resultado = session.exec(query, params=params)

        return resultado.mappings().all()