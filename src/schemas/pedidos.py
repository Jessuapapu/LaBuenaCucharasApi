from pydantic import BaseModel
from typing import List
import datetime

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
    detalles: List[Detalles]
