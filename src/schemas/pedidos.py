from pydantic import BaseModel
from typing import List
import datetime

from src.models.ordenes.types import EstadoOrden

class Detalles(BaseModel):
    nombre_platillo: str
    cantidad: int
    precio_unitario: float


class PedidosIn(BaseModel):
    nombre_cliente: str
    fecha: datetime.date
    detalle: List[Detalles]


class PedidosUpdate(BaseModel):
    nombre_cliente: str
    estado: EstadoOrden
    detalles: List[Detalles]
