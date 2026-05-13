from sqlmodel import Field, SQLModel
from .types import EstadoPedido
import decimal
import datetime

# Manejo de pedidos de los clientes con contrato o pedidos de comidas para eventos
class Pedidos(SQLModel, table=True):
    IdPedido: int = Field(primary_key=True)
    Estado: EstadoPedido = Field(nullable=False)
    fecha: datetime.datetime = Field(default=datetime.datetime.now())

class PedidosOrdenes(SQLModel, table=True):
    IdPedidosOrdenes: int = Field(primary_key=True)
    IdPedido: int = Field(foreign_key = "pedidos.IdPedido")
    IdOrdenes: int = Field(foreign_key = "ordenes.IdOrdenes")