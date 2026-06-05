from sqlmodel import Field, SQLModel
from .types import EstadoOrden, TipoPago
import datetime
import decimal
   

# Si la orden es un pedido de un contrato o evento
class Ordenes(SQLModel, table = True):
    IdOrdenes: int | None  = Field(default = None, primary_key = True, index = True)
    CostoTotal: decimal.Decimal = Field(default = None)
    IdCliente: int | None = Field(default = 0, foreign_key = "clientes.IdCliente")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    Estado: EstadoOrden = Field(default=EstadoOrden.PENDIENTE)
    

class DetallesOrdenes(SQLModel, table= True):
    IdDetallesOrdenes: int| None = Field(default = None, primary_key = True, index = True)
    IdOrdenes: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    IdPlatillo: int | None = Field(default = None, foreign_key = "platillos.IdPlatillo")
    CantidadPlatillo: int = Field(nullable = False)
    PrecioUnico: decimal.Decimal = Field(nullable=False)
    CostoTotal: decimal.Decimal = Field(nullable=False)