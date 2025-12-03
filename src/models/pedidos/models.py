from sqlmodel import Field, SQLModel
from .types import EstadoPedido, EstadoFactura
import decimal

class Pedidos(SQLModel, table=True):
    IdPedido: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    FechaPedido: str = Field(max_length=10, nullable=False)
    Estado: EstadoPedido = Field(nullable=False)

class DetallesDePedidos(SQLModel, table=True):
    IdDetalle: int | None = Field(default=None, primary_key=True)
    IdPedido: int = Field(foreign_key="pedidos.IdPedido", nullable=False)
    IdPlatillo: int = Field(foreign_key="platillos.IdPlatillo", nullable=False)
    Cantidad: int = Field(nullable=False)
    PrecioUnitario: float = Field(nullable=False)

class Facturas(SQLModel, table=True):
    IdFactura: int | None = Field(default=None, primary_key=True)
    MontoTotal: decimal.Decimal = Field(nullable=False)
    FechaFactura: str = Field(max_length=10, nullable=False)
    CantidadTotal: int = Field(nullable=False)
    Estado: EstadoFactura = Field(nullable=False)

class FacturasPedidos(SQLModel, table=True):
    IdFactura: int | None = Field(
        default=None, primary_key=True, foreign_key="facturas.IdFactura"
    )
    IdPedido: int = Field(nullable=False, foreign_key="pedidos.IdPedido")
