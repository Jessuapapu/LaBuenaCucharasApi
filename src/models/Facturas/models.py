from sqlmodel import Field, SQLModel
from .types import EstadoFactura
import datetime
import decimal

class Facturas(SQLModel, table=True):
    IdFactura: int | None = Field(default=None, primary_key=True)
    MontoTotal: decimal.Decimal = Field(nullable=False)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    IdOrdenes: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    CantidadTotal: int = Field(nullable=False)
    Estado: EstadoFactura = Field(nullable=False)
