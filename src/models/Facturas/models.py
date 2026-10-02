from sqlmodel import Field, SQLModel
from .types import EstadoFactura
import datetime
import decimal

class Facturas(SQLModel, table=True):
    IdFactura: int = Field(primary_key=True)
    MontoTotal: decimal.Decimal = Field(nullable=False)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    CantidadTotal: int = Field(nullable=False)
    Estado: EstadoFactura = Field(nullable=False)

class FacturasOrdenes(SQLModel, table=True):
    Id: int  = Field(primary_key=True)
    IdFactura: int  = Field(foreign_key = "facturas.IdFactura")
    IdOrdenes: int  = Field(foreign_key = "ordenes.IdOrdenes", unique=True)


