from sqlmodel import Field, SQLModel
import datetime
import decimal
from .types import TipoDeProveedor

class Proveedores(SQLModel, table=True):
    IdProveedor: int | None = Field(default=None, primary_key=True)
    NombreProveedor: str = Field(max_length= 150, nullable=False)
    Direccion: str | None = Field(default=None)
    Tipo: TipoDeProveedor

class RegistroDeAbastecimiento(SQLModel, table=True):
    IdRegistro: int | None = Field(default=None, primary_key=True)
    TotalIngresado: int = Field(default=None, nullable=False)
    IdProveedor: int | None = Field(default=None, foreign_key="proveedores.IdProveedor")
    CostoTotal: decimal.Decimal = Field(nullable=False)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())

class DetallesRegistroIngredientes(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdIngrediente: int | None = Field(default=None, foreign_key="ingredientes.IdIngrediente", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: decimal.Decimal