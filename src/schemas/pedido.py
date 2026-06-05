
from pydantic import BaseModel
from src.models.pedidos.types import TipoPedidoss, EstadoPedido
from typing import List, Optional

class PedidoCreateSchema(BaseModel):
    listaIdOrdenes: List[int]
    TipoPedido: TipoPedidoss

class PedidoUpdateSchema(BaseModel):
    Estado: Optional[EstadoPedido] = None
    TipoPedido: Optional[TipoPedidoss] = None
    listaIdOrdenes: Optional[List[int]] = None