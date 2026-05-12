from fastapi import HTTPException

from sqlmodel import Session, select
from src.config.database import db_engine

from src.schemas.facturas import facturaIn
from typing import List
from decimal import Decimal
import datetime
from sqlalchemy import select as sa_select, func, cast
from sqlalchemy.types import Date

from sqlmodel import Session
from sqlalchemy import text
from src.config.database import db_engine




def obtener_facturas_ordenes(
    id_cliente: int | None = None,
    id_orden: int | None = None,
    fecha_inicio: datetime.datetime | None = None,
    fecha_fin: datetime.datetime | None = None,
    monto: float | None = None,
    monto_fin: float | None = None,
    cantidad_total: int | None = None
) -> list:
    
    with Session(db_engine) as session:
        query = text("""
            EXEC MostrarFacturas 
                @IdCliente = :id_cliente,
                @IdOrden = :id_orden,
                @FechaInicio = :fecha_inicio,
                @FechaFin = :fecha_fin,
                @Monto = :monto,
                @MontoFin = :monto_fin,
                @CantidadTotal = :cantidad_total
        """)
        
        valores = {
            "id_cliente": id_cliente,
            "id_orden": id_orden,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "monto": monto,
            "monto_fin": monto_fin,
            "cantidad_total": cantidad_total
        }
        
        resultados = session.exec(query, params=valores).mappings().all()
        
        facturas_list = []
        for row in resultados:
            facturas_list.append({
                "monto_total": row.get("MontoTotal"),
                "cantidad_total": row.get("CantidadTotal"),
                "estado_factura": row.get("Estado"),
                "fecha_factura": row.get("Fecha"),
                "cliente": {
                    "nombre_cliente": row.get("NombreCliente"),
                    "direccion_cliente": row.get("DireccionCliente", "Sin dirección") 
                }
            })

        return facturas_list
    


def crear_facturas(
    payLoadDetalles: facturaIn
):
    json_string = payLoadDetalles.model_dump_json()

    with Session(db_engine) as session:
        try:

            query = text("EXEC GenerarFactura @PayloadJson = :json_data")
            

            id_generado = session.exec(query, {"json_data": json_string}).scalar()
            
            session.commit()
            return id_generado
            
        except Exception as e:
            print(f"Error al ejecutar el PA sp_GenerarFactura: {e}")
            return False
    return True