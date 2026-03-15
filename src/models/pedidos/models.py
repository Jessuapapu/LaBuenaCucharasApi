from sqlmodel import Field, SQLModel
from .types import EstadoPedido
import decimal
import datetime

class Pedidos(SQLModel, table=True):
    IdPedido: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    Fecha: datetime.datetime = Field(nullable=False)
    Estado: EstadoPedido = Field(nullable=False)

class DetallesDePedidos(SQLModel, table=True):
    IdDetalle: int | None = Field(default=None, primary_key=True)
    IdPedido: int = Field(foreign_key="pedidos.IdPedido", nullable=False)
    IdPlatillo: int = Field(foreign_key="platillos.IdPlatillo", nullable=False)
    Cantidad: int = Field(nullable=False)
    PrecioUnitario: float = Field(nullable=False)

