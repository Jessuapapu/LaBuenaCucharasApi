from pydantic import BaseModel
from typing import List
import datetime
from src.models.facturas.types import EstadoFactura


class detallesfacturas(BaseModel):
    IdOrden: int


class facturaIn(BaseModel):
    fecha: datetime.datetime
    detalles: list[detallesfacturas]
    Estado: EstadoFactura