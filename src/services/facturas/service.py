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
        
        resultados = session.execute(query, valores).mappings().all()
        
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