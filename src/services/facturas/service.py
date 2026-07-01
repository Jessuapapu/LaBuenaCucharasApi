from fastapi import HTTPException

from sqlmodel import Session
from src.config.database import db_engine
from src.schemas.facturas import facturaIn
import datetime

from sqlmodel import Session
from sqlalchemy import text
from src.config.database import db_engine
from src.services.auditorias.services import registrar_auditoria_factura
from src.models.auditorias.types import TipoDeAccion
from src.models.facturas.models import Facturas, FacturasOrdenes
from src.models.ordenes.models import Ordenes
from decimal import Decimal


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
    


def crear_facturas(
    payLoadDetalles: facturaIn, username: str | None = None
):
    json_string = payLoadDetalles.model_dump_json()

    with Session(db_engine) as session:
        try:

            query = text("EXEC GenerarFactura @PayloadJson = :json_data")
            id_generado = session.exec(query, {"json_data": json_string}).scalar()
            
            session.commit()
            # Auditoría: factura creada
            if username and id_generado:
                try:
                    registrar_auditoria_factura(username, int(id_generado), TipoDeAccion.CREAR)
                except Exception:
                    pass

            return id_generado
            
        except Exception as e:
            print(f"Error al ejecutar el PA sp_GenerarFactura: {e}")
            return False
    return True


def actualizar_factura(IdFactura: int, payLoadDetalles: facturaIn, username: str | None = None):
    with Session(db_engine) as session:
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

            # Auditoría: factura actualizada
            if username:
                try:
                    registrar_auditoria_factura(username, IdFactura, TipoDeAccion.ACTUALIZAR)
                except Exception:
                    pass

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