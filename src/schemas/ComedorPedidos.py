from pydantic import BaseModel
from typing import List
from .pedidos import Detalles
import datetime

class OrdenComedorIN(BaseModel):
    IdMesa: int
    Detalles: list[Detalles]


    