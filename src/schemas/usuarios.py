from pydantic import BaseModel
from src.models.pedidos.types import TipoPedidoss, EstadoPedido
from typing import List, Optional

class UsuarioSchema(BaseModel):
    user: str
    contra_plano: str
    rol: str
    correo: str