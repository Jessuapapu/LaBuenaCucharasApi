from sqlmodel import Field, SQLModel
from .types import EstadoFactura
import datetime
import decimal


class Facturas(SQLModel, table=True):
    IdFactura: int | None = Field(default=None, primary_key=True)
    MontoTotal: decimal.Decimal = Field(nullable=False)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    CantidadTotal: int = Field(nullable=False)
    Estado: EstadoFactura = Field(nullable=False)

class FacturasPedidos(SQLModel, table=True):
    IdFactura: int | None = Field(
        default=None, primary_key=True, foreign_key="facturas.IdFactura"
    )
    IdPedido: int = Field(nullable=False, foreign_key="pedidos.IdPedido")

class FacturasOrdenes(SQLModel, table=True):
    IdFactura: int | None = Field(
        default=None, primary_key=True, foreign_key="facturas.IdFactura"
    )
    IdOrdenes: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")