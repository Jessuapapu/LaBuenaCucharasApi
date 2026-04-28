from sqlmodel import Field, SQLModel
from .types import EstadoPedido
import decimal
import datetime

# Manejo de pedidos de los clientes con contrato o pedidos de comidas para eventos
class Pedidos(SQLModel, table=True):
    IdPedido: int | None = Field(default=None, primary_key=True)
    IdOrdenes: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    Fecha: datetime.datetime = Field(nullable=False)
    Estado: EstadoPedido = Field(nullable=False)