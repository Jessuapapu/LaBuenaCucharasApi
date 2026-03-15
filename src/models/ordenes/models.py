from sqlmodel import Field, SQLModel
import datetime
import decimal


class Ordenes(SQLModel, table = True):
    IdOrdenes: int | None  = Field(default = None, primary_key = True, index = True)
    CostoTotal: decimal.Decimal = Field(default = None)
    IdCliente: int | None = Field(default = 0, foreign_key = "clientes.IdCliente")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    
class MetodosPagoOrdenes(SQLModel, table=True):
    IdMetodoPagoOrdenes: int | None = Field(default = None, primary_key = True)
    NombreTipo: str = Field(nullable = False, max_length=100)
    
class PagoOrdenes(SQLModel, table = True):
    IdPagoOrdenes: int | None  = Field(default = None, primary_key = True, index = True)
    IdMetodoPagoOrdenes: int | None = Field(default = None, foreign_key = "metodosPagoOrdenes.IdMetodoPagoOrdenes")
    IdOrden: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    PagoTotal: decimal.Decimal = Field(default = None)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())

class DetallesOrdenes(SQLModel, table= True):
    IdDetallesOrdenes: int| None = Field(default = None, primary_key = True, index = True)
    IdOrdenes: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    IdPlatillo: int | None = Field(default = None, foreign_key = "platillos.IdPlatillo")
    CantidadPlatillo: int = Field(nullable = False)
    PrecioUnico: decimal.Decimal = Field(nullable=False)
    CostoTotal: decimal.Decimal = Field(nullable=False)